#!/usr/bin/env python3
from pyspark.sql import SparkSession
from pyspark.storagelevel import StorageLevel
from pyspark.ml.recommendation import ALS
from pyspark.ml.tuning import ParamGridBuilder, TrainValidationSplit
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.sql.functions import expr, collect_list
from pyspark.mllib.evaluation import RankingMetrics

def main():
    # 1. Démarrage de Spark
    spark = (
        SparkSession.builder
        .appName("ALS_Training_Optimized")
        .master("local[*]")
        .config("spark.driver.memory", "6g")
        .config("spark.executor.memory", "6g")
        .config("spark.sql.shuffle.partitions", "200")
        .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    # 2. Chargement des ratings depuis HDFS
    ratings = (
        spark.read
             .csv("hdfs://namenode:9000/movielens/processed/batch/ratings_csv",
                  header=True, inferSchema=True)
             .select("userId", "movieId", "rating")
             .persist(StorageLevel.MEMORY_AND_DISK)
    )
    total = ratings.count()
    print(f"▷ Total interactions : {total}")

    # 3. Split train/test
    train, test = ratings.randomSplit([0.8, 0.2], seed=42)
    train = train.persist(StorageLevel.MEMORY_AND_DISK)
    test  = test.persist(StorageLevel.MEMORY_AND_DISK)
    print(f"▷ Entraînement : {train.count()}  •  Test : {test.count()}")

    # 4. Définition d’ALS et de l’évaluateur
    als = ALS(
        userCol="userId", itemCol="movieId", ratingCol="rating",
        coldStartStrategy="drop"
    )
    evaluator = RegressionEvaluator(
        metricName="rmse", labelCol="rating", predictionCol="prediction"
    )

    # 5. Grille d’hyper-paramètres
    paramGrid = (
        ParamGridBuilder()
            .addGrid(als.rank,    [10, 20, 30])
            .addGrid(als.regParam,[0.01, 0.1])
            .addGrid(als.maxIter, [5, 10])
            .build()
    )

    # 6. Configuration de la recherche
    tvs = TrainValidationSplit(
        estimator=als,
        estimatorParamMaps=paramGrid,
        evaluator=evaluator,
        trainRatio=0.8,
        parallelism=4
    )

    # 7. Entraînement et meilleur modèle
    tvsModel  = tvs.fit(train)
    bestModel = tvsModel.bestModel

    # ── Récupération des meilleurs hyper-paramètres ────────────────────────
    # On récupère la liste des ParamMaps et des scores
    paramMaps = tvsModel.getEstimatorParamMaps()
    metrics   = tvsModel.validationMetrics  # liste de RMSE pour chaque combinaison

    # Trouver l’indice de la meilleure métrique (minimum de RMSE)
    bestIndex    = min(range(len(metrics)), key=lambda i: metrics[i])
    bestParamMap = paramMaps[bestIndex]

    # Extraire rank, regParam et maxIter depuis ce ParamMap
    best_rank = bestParamMap[als.rank]
    best_reg  = bestParamMap[als.regParam]
    best_iter = bestParamMap[als.maxIter]
    print(f"▷ Meilleurs paramètres : rank={best_rank}, regParam={best_reg}, maxIter={best_iter}")

    # 8. Évaluation sur le test (RMSE & MAE)
    predictions = bestModel.transform(test)
    rmse = evaluator.evaluate(predictions)
    mae  = RegressionEvaluator(
        metricName="mae", labelCol="rating", predictionCol="prediction"
    ).evaluate(predictions)
    print(f"▷ Test RMSE : {rmse:.4f}")
    print(f"▷ Test MAE  : {mae:.4f}")

    # 9. Métriques de ranking
    recs = (
        bestModel
        .recommendForAllUsers(10)
        .select("userId", expr("transform(recommendations, x -> x.movieId) as pred"))
    )
    actual = (
        test
        .groupBy("userId")
        .agg(collect_list("movieId").alias("actual"))
    )
    pred_and_labels = (
        recs.join(actual, "userId")
            .select("pred", "actual")
            .rdd.map(lambda r: (r.pred, r.actual))
    )
    metrics_rank = RankingMetrics(pred_and_labels)
    print(f"Precision@10 : {metrics_rank.precisionAt(10):.4f}")
    print(f"Recall@10    : {metrics_rank.recallAt(10):.4f}")
    print(f"MAP@10       : {metrics_rank.meanAveragePrecision:.4f}")
    print(f"NDCG@10      : {metrics_rank.ndcgAt(10):.4f}")

    # 10. Sauvegarde du modèle
    bestModel.write().overwrite().save(
        "hdfs://namenode:9000/movielens/models/als_best"
    )
    print("✅ Modèle sauvegardé dans HDFS sous /movielens/models/als_best")

    spark.stop()


if __name__ == "__main__":
    main()
