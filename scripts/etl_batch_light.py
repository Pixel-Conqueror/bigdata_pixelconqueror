#!/usr/bin/env python3
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, year, month, dayofmonth,
    avg, stddev, rand
)

def main():
    spark = SparkSession.builder \
        .appName("BatchETLLight") \
        .master("local[*]") \
        .config("spark.driver.memory", "4g") \
        .config("spark.driver.maxResultSize", "2g") \
        .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
        .getOrCreate()

    # Lecture des données brutes
    movies_raw = spark.read.csv(
        "hdfs://namenode:9000/movielens/raw/movies/movies.csv",
        header=True, inferSchema=True
    )
    ratings_raw_all = spark.read.csv(
        "hdfs://namenode:9000/movielens/raw/ratings/ratings.csv",
        header=True, inferSchema=True
    )

    # Échantillonnage : garder au plus 1 million de lignes
    total_count = ratings_raw_all.count()
    if total_count > 1_000_000:
        ratings_raw = (
            ratings_raw_all
            .orderBy(rand(seed=42))
            .limit(1_000_000)
        )
    else:
        ratings_raw = ratings_raw_all

    # Statistiques globales sur l'échantillon
    stats = ratings_raw.select(
        avg("rating").alias("mu"),
        stddev("rating").alias("sigma")
    ).first()
    mu, sigma = stats["mu"], stats["sigma"]

    # Calcul du z-score par utilisateur
    user_stats = ratings_raw.groupBy("userId") \
        .agg(
            avg("rating").alias("mu_u"),
            stddev("rating").alias("sigma_u")
        )
    ratings_z = ratings_raw.join(user_stats, "userId") \
        .withColumn("z_score", (col("rating") - col("mu_u")) / col("sigma_u"))

    clean1 = ratings_z \
        .filter(col("z_score").between(-3, 3)) \
        .filter((col("rating") >= mu - 3 * sigma) & (col("rating") <= mu + 3 * sigma))

    # Nouvelle logique de filtrage sur volumes d’interactions adaptée à l'échantillon
    min_user_ratings = 10   # nombre minimal de notes par utilisateur
    min_movie_ratings = 20  # nombre minimal de notes par film
    user_counts = (
        clean1.groupBy("userId").count()
        .filter(col("count") >= min_user_ratings)
    )
    movie_counts = (
        clean1.groupBy("movieId").count()
        .filter(col("count") >= min_movie_ratings)
    )
    clean2 = clean1.join(user_counts, "userId").join(movie_counts, "movieId")

    # Suppression des nulls et des doublons
    ratings_clean = clean2.dropna(
        how="any",
        subset=["userId", "movieId", "rating", "timestamp"]
    ).dropDuplicates(["userId", "movieId", "timestamp"] )

    # Enrichissement temporel
    ratings_enriched = ratings_clean \
        .withColumn("year", year(col("timestamp"))) \
        .withColumn("month", month(col("timestamp"))) \
        .withColumn("day", dayofmonth(col("timestamp")))

    # Écriture des résultats au format CSV
    movies_raw.repartition(1) \
        .write.option("header", True) \
        .mode("overwrite") \
        .csv("hdfs://namenode:9000/movielens/processed/batch/movies_csv")

    ratings_enriched.select(
        "userId", "movieId", "rating", "timestamp", "year", "month", "day"
    ).coalesce(1) \
      .write.option("header", True) \
      .mode("overwrite") \
      .csv("hdfs://namenode:9000/movielens/processed/batch/ratings_csv")

    print("🎉 ETL batch light terminé : CSV prêts dans HDFS")
    spark.stop()

if __name__ == "__main__":
    main()
