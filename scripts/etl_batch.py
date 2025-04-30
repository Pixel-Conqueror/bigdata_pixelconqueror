# Cellule 1 – Imports & SparkSession
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, year, month, dayofmonth, count, mean, stddev
from pyspark.sql.window import Window
from pyspark.sql.functions import avg, stddev, expr
spark = SparkSession.builder \
    .appName("BatchETLPipelineEnhanced") \
    .master("local[*]") \
    .config("spark.driver.memory", "4g") \
    .config("spark.driver.maxResultSize", "1g") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
    .getOrCreate()

movies_raw = spark.read.csv(
    "hdfs://namenode:9000/movielens/raw/movies/movies.csv",
    header=True, inferSchema=True
)
ratings_raw = spark.read.csv(
    "hdfs://namenode:9000/movielens/raw/ratings/ratings.csv",
    header=True, inferSchema=True
)

print(f"🔍 Raw films  : {movies_raw.count()}")
print(f"🔍 Raw notes  : {ratings_raw.count()}")

movies_raw.show(5, truncate=False)
ratings_raw.show(5, truncate=False)
stats = ratings_raw.select(
    mean("rating").alias("mean"),
    stddev("rating").alias("stddev")
).first()
mean_rating, stddev_rating = stats["mean"], stats["stddev"]
print(f"Mean={mean_rating:.3f}, StdDev={stddev_rating:.3f}")

ratings_raw.groupBy("rating").count().orderBy("rating").show()


# 1. Stats globales
stats = ratings_raw.select(mean("rating").alias("μ"), stddev("rating").alias("σ")).first()
μ, σ = stats["μ"], stats["σ"]

# 2. Z-score par utilisateur
user_stats = ratings_raw.groupBy("userId") \
    .agg(avg("rating").alias("μ_u"), stddev("rating").alias("σ_u"))

ratings_z = ratings_raw.join(user_stats, "userId") \
    .withColumn("z_score", (col("rating") - col("μ_u"))/col("σ_u"))

# 3. Filtrage z-score et global
clean1 = ratings_z.filter((col("z_score").between(-3,3))) \
    .filter((col("rating") >= μ - 3*σ) & (col("rating") <= μ + 3*σ))

# 4. Compter interactions nettes
user_counts = clean1.groupBy("userId").count().alias("user_count")
movie_counts = clean1.groupBy("movieId").count().alias("movie_count")

# 5. Exclure les petits volumes
clean2 = clean1.join(user_counts.filter(col("count")>=20), "userId") \
               .join(movie_counts.filter(col("count")>=50), "movieId")

# 6. Suppression nulls/doublons
ratings_clean = clean2 \
    .dropna(how="any", subset=["userId","movieId","rating","timestamp"]) \
    .dropDuplicates(["userId","movieId","timestamp"]) \
    .cache()

count_after = ratings_clean.count()
print(f"📊 Notes après nettoyage : {count_after}")
ratings_clean.show(3, truncate=False)
ratings_enriched = (ratings_clean
    .withColumn("year",  year(col("timestamp")))
    .withColumn("month", month(col("timestamp")))
    .withColumn("day",   dayofmonth(col("timestamp")))
)
ratings_enriched.show(5, truncate=False)
ratings_final = ratings_enriched.select(
    "userId","movieId","rating","timestamp","year","month","day"
)

# Vérif
print("Champs finaux :", ratings_final.columns)
ratings_final.show(3, truncate=False)
# Movies en 1 unique CSV
movies_raw.repartition(1) \
    .write \
    .option("header", True) \
    .mode("overwrite") \
    .csv("hdfs://namenode:9000/movielens/processed/batch/movies_csv")

# Ratings en 1 unique CSV
ratings_final.coalesce(1) \
    .write \
    .option("header", True) \
    .mode("overwrite") \
    .csv("hdfs://namenode:9000/movielens/processed/batch/ratings_csv")

print("🎉 Écriture CSV terminée")
# Lecture des movies depuis CSV
df_movies = spark.read.csv(
    "hdfs://namenode:9000/movielens/processed/batch/movies_csv",
    header=True, inferSchema=True
)

# Lecture des ratings depuis CSV
df_ratings = spark.read.csv(
    "hdfs://namenode:9000/movielens/processed/batch/ratings_csv",
    header=True, inferSchema=True
)

print(f"✔️ Films CSV   : {df_movies.count()}")
print(f"✔️ Notes CSV   : {df_ratings.count()}")

df_movies.show(5, truncate=False)
df_ratings.show(5, truncate=False)
