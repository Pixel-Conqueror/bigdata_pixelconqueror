import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, expr
from pyspark.sql.types import StructType, StructField, IntegerType, DoubleType, LongType
from pyspark.ml.recommendation import ALSModel
from pymongo import MongoClient

def write_to_mongo(batch_df, batch_id):
    # Convertit DataFrame Spark en liste de dicts
    records = batch_df.select("userId", "recommendations").rdd.map(lambda r: {
        "userId": int(r.userId),
        "recommendations": [int(x) for x in r.recommendations]
    }).collect()
    if not records:
        return
    client = MongoClient("mongodb://localhost:27017/")
    db = client.movielens
    coll = db.recommendations
    # Upsert pour chaque utilisateur
    for rec in records:
        coll.replace_one(
            {"userId": rec["userId"]},
            rec,
            upsert=True
        )
    client.close()

def main():
    spark = SparkSession.builder \
        .appName("StreamingRecs") \
        .master("local[*]") \
        .config("spark.driver.memory", "2g") \
        .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
        .getOrCreate()

    # 1. Charger le modèle ALS sauvegardé
    model = ALSModel.load("hdfs://namenode:9000/movielens/models/als_best")

    # 2. Schéma du message Kafka
    schema = StructType([
        StructField("userId", IntegerType()),
        StructField("movieId", IntegerType()),
        StructField("rating", DoubleType()),
        StructField("timestamp", LongType())
    ])

    # 3. Lecture du flux Kafka
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "movielens_ratings") \
        .load() \
        .selectExpr("CAST(value AS STRING) as json")

    # 4. Parser le JSON
    parsed = df.select(from_json(col("json"), schema).alias("data")) \
               .select("data.*")

    # 5. Pour chaque micro-batch, générer et stocker les recos
    #    on prend les utilisateurs du batch, on demande top-5
    def foreach_batch(batch_df, batch_id):
        users = batch_df.select("userId").distinct()
        recs = model.recommendForUserSubset(users, 5) \
                    .selectExpr("userId", "transform(recommendations, x -> x.movieId) as recommendations")
        write_to_mongo(recs, batch_id)

    query = parsed.writeStream \
        .foreachBatch(foreach_batch) \
        .outputMode("append") \
        .start()

    query.awaitTermination()

if __name__ == "__main__":
    main()
