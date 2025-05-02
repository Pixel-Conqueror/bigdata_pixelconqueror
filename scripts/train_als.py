#!/usr/bin/env python3
from pyspark.sql import SparkSession
from pyspark.storagelevel import StorageLevel
from pyspark.ml.recommendation import ALS
from pyspark.ml.tuning import ParamGridBuilder, TrainValidationSplit
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.sql.functions import expr, collect_list
from pyspark.mllib.evaluation import RankingMetrics

def main():
    # Démarre Spark en allouant suffisamment de mémoire et en ajustant les partitions de shuffle
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

    # Charge le CSV des évaluations depuis HDFS, sélectionne les colonnes utiles et mets en cache
    ratings = (
        spark.read
        .csv("hdfs://namenode:9000/movielens/processed/batch/ratings_csv",
             header=True, inferSchema=True)
        .select("userId", "movieId", "rating")
        .persist(StorageLevel.MEMORY_AND_DISK)
    )

    # Force le calcul du cache et affiche le nombre d'interactions
    total = ratings.count()
    print(f"▷ Total interactions : {total}")

    # Sépare en ensembles train (80%) et test (20%), et mets chacun en cache
    train, test = ratings.randomSplit([0.8, 0.2], seed=42)
    train = train.persist(StorageLevel.MEMORY_AND_DISK)
    test = test.persist(StorageLevel.MEMORY_AND_DISK)
    print(f"▷ Entraînement : {train.count()}  •  Test : {test.count()}")

    # Définit l'ALS avec gestion des cold starts, et prépare l'évaluateur RMSE
    als = ALS(
        userCol="userId", itemCol="movieId", ratingCol="rating",
        coldStartStrategy="drop"
    )
    evaluator = RegressionEvaluator(
        metricName="rmse", labelCol="rating", predictionCol="prediction"
    )

    # Construit la grille d'hyperparamètres à tester
    paramGrid = (
        ParamGridBuilder()
        .addGrid(als.rank, [10, 20, 30])
        .addGrid(als.regParam, [0.01, 0.1])
        .addGrid(als.maxIter, [5, 10])
        .build()
    )

    # Configure la recherche avec TrainValidationSplit pour aller plus vite
    tvs = TrainValidationSplit(
        estimator=als,
        estimatorParamMaps=paramGrid,
        evaluator=evaluator,
        trainRatio=0.8,
        parallelism=4  # Monter ou descendre selon le nombre de cœurs dispo
    )

    # Lance l'entraînement et récupère le meilleur modèle
    tvsModel = tvs.fit(train)
    bestModel = tvsModel.bestModel

    # Extrait et affiche les meilleurs paramètres
    best_rank = bestModel._java_obj.parent().getOrDefault(als.rank)
    best_reg = bestModel._java_obj.parent().getOrDefault(als.regParam)
    best_iter = bestModel._java_obj.parent().getOrDefault(als.maxIter)
    print(f"▷ Meilleurs paramètres : rank={best_rank}, regParam={best_reg}, maxIter={best_iter}")

    # Évalue les performances sur l'ensemble de test (RMSE & MAE)
    predictions = bestModel.transform(test)
    rmse = evaluator.evaluate(predictions)
    mae = RegressionEvaluator(
        metricName="mae", labelCol="rating", predictionCol="prediction"
    ).evaluate(predictions)
    print(f"▷ Test RMSE : {rmse:.4f}")
    print(f"▷ Test MAE  : {mae:.4f}")

    # Prépare et calcule les métriques de ranking (Precision, Recall, MAP, NDCG)
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
    metrics = RankingMetrics(pred_and_labels)
    print(f"Precision@10 : {metrics.precisionAt(10):.4f}")
    print(f"Recall@10    : {metrics.recallAt(10):.4f}")
    print(f"MAP@10       : {metrics.meanAveragePrecision:.4f}")
    print(f"NDCG@10      : {metrics.ndcgAt(10):.4f}")

    # Sauvegarde du modèle optimisé dans HDFS
    bestModel.write().overwrite().save(
        "hdfs://namenode:9000/movielens/models/als_best"
    )
    print("✅ Modèle sauvegardé dans HDFS sous /movielens/models/als_best")

    spark.stop()


if __name__ == "__main__":
    main()
