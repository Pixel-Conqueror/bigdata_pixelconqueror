#!/usr/bin/env python3
# scripts/streaming_recommendations.py

import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, expr
from pyspark.sql.types import StructType, StructField, IntegerType, DoubleType, LongType
from pyspark.ml.recommendation import ALSModel
from pymongo import MongoClient

def get_db():
    """
    Récupère l'URI Mongo depuis MONGO_URI (ex: mongodb://mongo:27017/movies)
    et renvoie la database par défaut.
    """
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017/movies")
    client = MongoClient(mongo_uri)
    return client.get_default_database()

def write_to_mongo(batch_df, batch_id):
    """
    Pour chaque micro-batch, convertit les recommendations en dict
    puis upsert dans la collection `recommendations`.
    """
    db = get_db()
    coll = db.recommendations

    records = batch_df.select("userId", "recommendations") \
                      .rdd.map(lambda r: {
                          "userId": int(r.userId),
                          "recommendations": [int(x) for x in r.recommendations]
                      }).collect()
    if not records:
        return

    for rec in records:
        coll.replace_one({"userId": rec["userId"]}, rec, upsert=True)

def main():
    spark = SparkSession.builder \
        .appName("StreamingRecs") \
        .master("local[*]") \
        .config("spark.driver.memory", "2g") \
        .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
        .getOrCreate()

    # 1. Charger le modèle ALS entraîné
    model = ALSModel.load("hdfs://namenode:9000/movielens/models/als_best")

    # 2. Schéma du JSON entrant de Kafka
    schema = StructType([
        StructField("userId",   IntegerType()),
        StructField("movieId",  IntegerType()),
        StructField("rating",   DoubleType()),
        StructField("timestamp",LongType())
    ])

    # 3. Lecture du topic Kafka
    raw = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "movielens_ratings") \
        .load() \
        .selectExpr("CAST(value AS STRING) AS json")

    # 4. Parsing JSON
    parsed = raw.select(from_json(col("json"), schema).alias("data")) \
                .select("data.*")

    # 5. Pour chaque micro-batch, on génère les recommandations
    def foreach_batch(batch_df, batch_id):
        users = batch_df.select("userId").distinct()
        recs = model.recommendForUserSubset(users, 5) \
                    .selectExpr(
                        "userId",
                        "transform(recommendations, x -> x.movieId) AS recommendations"
                    )
        write_to_mongo(recs, batch_id)

    query = parsed.writeStream \
        .foreachBatch(foreach_batch) \
        .outputMode("append") \
        .start()

    query.awaitTermination()

if __name__ == "__main__":
    main()
