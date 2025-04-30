#!/usr/bin/env python3
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, year, month, dayofmonth,
    avg, stddev
)

def main():
    spark = SparkSession.builder \
        .appName("BatchETL") \
        .master("local[*]") \
        .config("spark.driver.memory", "4g") \
        .config("spark.driver.maxResultSize", "2g") \
        .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
        .getOrCreate()

    # Lecture raw
    movies_raw = spark.read.csv(
        "hdfs://namenode:9000/movielens/raw/movies/movies.csv",
        header=True, inferSchema=True
    )
    ratings_raw = spark.read.csv(
        "hdfs://namenode:9000/movielens/raw/ratings/ratings.csv",
        header=True, inferSchema=True
    )

    # Stats globales
    stats = ratings_raw.select(
        avg("rating").alias("mu"),
        stddev("rating").alias("sigma")
    ).first()
    mu, sigma = stats["mu"], stats["sigma"]

    # Z-score par utilisateur
    user_stats = ratings_raw.groupBy("userId") \
        .agg(
            avg("rating").alias("mu_u"),
            stddev("rating").alias("sigma_u")
        )
    ratings_z = ratings_raw.join(user_stats, "userId") \
        .withColumn("z_score", (col("rating") - col("mu_u"))/col("sigma_u"))

    clean1 = ratings_z.filter(col("z_score").between(-3,3)) \
        .filter((col("rating") >= mu - 3*sigma) & (col("rating") <= mu + 3*sigma))

    # Filtre sur volumes d’interactions
    user_counts = clean1.groupBy("userId").count().filter(col("count") >= 20)
    movie_counts = clean1.groupBy("movieId").count().filter(col("count") >= 50)
    clean2 = clean1.join(user_counts, "userId").join(movie_counts, "movieId")

    # Suppression nulls & doublons (sans cache)
    ratings_clean = clean2.dropna(
        how="any",
        subset=["userId","movieId","rating","timestamp"]
    ).dropDuplicates(["userId","movieId","timestamp"])

    # Enrichissement temporel
    ratings_enriched = ratings_clean \
        .withColumn("year",  year(col("timestamp"))) \
        .withColumn("month", month(col("timestamp"))) \
        .withColumn("day",   dayofmonth(col("timestamp")))

    # Écriture CSV batch
    movies_raw.repartition(1) \
        .write.option("header", True) \
        .mode("overwrite") \
        .csv("hdfs://namenode:9000/movielens/processed/batch/movies_csv")

    ratings_enriched.select(
        "userId","movieId","rating","timestamp","year","month","day"
    ).coalesce(1) \
      .write.option("header", True) \
      .mode("overwrite") \
      .csv("hdfs://namenode:9000/movielens/processed/batch/ratings_csv")

    print("🎉 ETL batch terminé : CSV prêts dans HDFS")
    spark.stop()

if __name__ == "__main__":
    main()
