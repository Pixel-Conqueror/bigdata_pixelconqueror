#!/usr/bin/env python3
# scripts/ingest_spark_to_mongo.py

import os
from pyspark.sql import SparkSession
from pymongo import MongoClient

# reprendre votre get_db()
def get_db():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017/movies")
    client = MongoClient(mongo_uri)
    return client.get_default_database()

def write_movies(partition):
    db = get_db()
    coll = db.movies
    docs = []
    for row in partition:
        # si "(no genres listed)" ou champ vide, on met "unknown"
        raw_genres = row.genres or ""
        cleaned = "unknown" if raw_genres.strip() == "(no genres listed)" else raw_genres
        docs.append({
            "movieId": int(row.movieId),
            "title":    row.title,
            "genres":   cleaned.split("|") if cleaned else ["unknown"]
        })
    if docs:
        coll.insert_many(docs)

def write_ratings(partition):
    db = get_db()
    coll = db.ratings
    docs = []
    for row in partition:
        docs.append({
            "userId":    int(row.userId),
            "movieId":   int(row.movieId),
            "rating":    float(row.rating),
            "timestamp": row.timestamp,
            "year":      int(row.year),
            "month":     int(row.month),
            "day":       int(row.day)
        })
    if docs:
        coll.insert_many(docs)

def main():
    spark = SparkSession.builder \
        .appName("IngestToMongo") \
        .master("local[*]") \
        .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
        .getOrCreate()

    # lire vos CSV HDFS
    movies = spark.read.csv(
        "hdfs://namenode:9000/movielens/processed/batch/movies_csv",
        header=True, inferSchema=True
    ).select("movieId","title","genres")

    ratings = spark.read.csv(
        "hdfs://namenode:9000/movielens/processed/batch/ratings_csv",
        header=True, inferSchema=True
    ).select("userId","movieId","rating","timestamp","year","month","day")

    # on supprime d'abord les données existantes
    db = get_db()
    db.movies.delete_many({})
    db.ratings.delete_many({})

    # écrire par partition
    movies.rdd.foreachPartition(write_movies)
    ratings.rdd.foreachPartition(write_ratings)

    spark.stop()
    print("✅ Chargement Spark → MongoDB terminé")

if __name__=="__main__":
    main()
