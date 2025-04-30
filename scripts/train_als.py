#!/usr/bin/env python3
from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALS
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.mllib.evaluation import RankingMetrics
from pyspark.sql.functions import expr, collect_list

# 1. SparkSession
spark = SparkSession.builder \
    .appName("ALS_Training_Script") \
    .master("local[*]") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
    .getOrCreate()

# 2. Lecture des CSV nettoyés
ratings = spark.read.csv(
    "hdfs://namenode:9000/movielens/processed/batch/ratings_csv",
    header=True, inferSchema=True
).select("userId","movieId","rating")

print(f"▷ Total interactions: {ratings.count()}")

# 3. Split train/test
train, test = ratings.randomSplit([0.8,0.2], seed=42)
print(f"▷ Train: {train.count()}  •  Test: {test.count()}")

# 4. Hyperparam search
ranks = [10,20,30]
regs  = [0.01,0.1]
iters = [5,10]
best_rmse = float("inf")
best_model = None

evaluator_rmse = RegressionEvaluator(
    metricName="rmse", labelCol="rating", predictionCol="prediction"
)
evaluator_mae = RegressionEvaluator(
    metricName="mae", labelCol="rating", predictionCol="prediction"
)

for rank in ranks:
    for reg in regs:
        for n in iters:
            als = ALS(
                userCol="userId", itemCol="movieId", ratingCol="rating",
                coldStartStrategy="drop",
                rank=rank, regParam=reg, maxIter=n
            )
            model = als.fit(train)
            preds = model.transform(test)
            rmse = evaluator_rmse.evaluate(preds)
            mae  = evaluator_mae.evaluate(preds)
            print(f"rank={rank} reg={reg} iter={n} → RMSE={rmse:.4f} MAE={mae:.4f}")
            if rmse < best_rmse:
                best_rmse, best_model = rmse, model

# 5. Metrics de ranking
recs = best_model.recommendForAllUsers(10) \
    .select("userId", expr("transform(recommendations, x -> x.movieId) as pred"))

actual = test.groupBy("userId") \
    .agg(collect_list("movieId").alias("actual"))

pred_and_labels = recs.join(actual, "userId") \
    .select("pred","actual") \
    .rdd.map(lambda r: (r.pred, r.actual))

metrics = RankingMetrics(pred_and_labels)
print(f"Precision@10 : {metrics.precisionAt(10):.4f}")
print(f"Recall@10    : {metrics.recallAt(10):.4f}")
print(f"MAP@10       : {metrics.meanAveragePrecision:.4f}")
print(f"NDCG@10      : {metrics.ndcgAt(10):.4f}")

# 6. Sauvegarde du meilleur modèle
best_model.write().overwrite().save(
    "hdfs://namenode:9000/movielens/models/als_best"
)
print("✅ Modèle ALS sauvegardé dans HDFS : /movielens/models/als_best")

spark.stop()
