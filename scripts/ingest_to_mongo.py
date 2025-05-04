#!/usr/bin/env python3
# scripts/ingest_spark_to_mongo.py

from pyspark.sql import SparkSession
from pyspark.sql.functions import split, col
from pymongo import MongoClient

MONGO_URI = "mongodb://mongo:27017"
DB_NAME   = "movielens"

def write_movies(partition):
    client = MongoClient(MONGO_URI)
    coll  = client[DB_NAME].movies
    docs  = []
    for row in partition:
        docs.append({
            "movieId": int(row.movieId),
            "title":    row.title,
            "genres":   row.genres.split("|") if row.genres else []
        })
    if docs:
        coll.insert_many(docs)
    client.close()

def write_ratings(partition):
    client = MongoClient(MONGO_URI)
    coll  = client[DB_NAME].ratings
    docs  = []
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
    client.close()

def main():
    spark = SparkSession.builder \
        .appName("IngestToMongo") \
        .master("local[*]") \
        .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
        .getOrCreate()

    # Lecture CSV nettoyés
    movies = spark.read.csv(
        "hdfs://namenode:9000/movielens/processed/batch/movies_csv",
        header=True, inferSchema=True
    ).select("movieId","title","genres")

    ratings = spark.read.csv(
        "hdfs://namenode:9000/movielens/processed/batch/ratings_csv",
        header=True, inferSchema=True
    ).select("userId","movieId","rating","timestamp","year","month","day")

    # On vide d'abord les anciennes collections
    client = MongoClient(MONGO_URI)
    db     = client[DB_NAME]
    db.movies.delete_many({})
    db.ratings.delete_many({})
    client.close()

    # Écriture par partition
    movies.rdd.foreachPartition(write_movies)
    ratings.rdd.foreachPartition(write_ratings)

    spark.stop()
    print("✅ Chargement Spark → MongoDB terminé")

if __name__=="__main__":
    main()
