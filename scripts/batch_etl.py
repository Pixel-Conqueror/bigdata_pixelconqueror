#!/usr/bin/env python3
# /scripts/batch_etl.py

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, year, month, dayofmonth

spark = SparkSession.builder \
    .appName("MovieLensBatchETL") \
    .master("local[*]") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
    .getOrCreate()

# 1. Lecture raw
movies = spark.read.csv("/movielens/raw/movies/movie.csv", header=True, inferSchema=True)
ratings = spark.read.csv("/movielens/raw/ratings/rating.csv", header=True, inferSchema=True)

print(f"Raw films: {movies.count()}, raw notes: {ratings.count()}")

# 2. Nettoyage
ratings_clean = (ratings
    .filter((col("rating") >= 0.5) & (col("rating") <= 5.0))
    .dropna(how="any", subset=["userId","movieId","rating","timestamp"])
    .dropDuplicates(["userId","movieId","timestamp"])
)
print(f"Après nettoyage: {ratings_clean.count()} notes")

# 3. Enrichissement temporel
ratings_enriched = (ratings_clean
    .withColumn("year",  year(col("timestamp")))
    .withColumn("month", month(col("timestamp")))
    .withColumn("day",   dayofmonth(col("timestamp")))
)

# 4. Écriture Parquet
movies.write.mode("overwrite") \
    .parquet("/movielens/processed/batch/movies")

ratings_enriched.write.mode("overwrite") \
    .partitionBy("year","month","day") \
    .parquet("/movielens/processed/batch/ratings")

print("✓ ETL batch terminé")
spark.stop()
