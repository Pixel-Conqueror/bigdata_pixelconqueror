import os
from pyspark.sql import SparkSession
from pymongo import MongoClient
from faker import Faker

def get_db():
    """
    Récupère la base configurée via l'URI MONGO_URI.
    Par défaut mongodb://mongo:27017/movies ⇒ base 'movies'.
    """
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017/movies")
    client = MongoClient(mongo_uri)
    return client.get_default_database()

def write_movies(partition):
    db = get_db()
    coll = db.movies
    docs = []
    for row in partition:
        raw_genres = row.genres or ""
        cleaned = "unknown" if raw_genres.strip() == "(no genres listed)" else raw_genres
        genres_list = cleaned.split("|") if cleaned else ["unknown"]
        docs.append({
            "movieId": int(row.movieId),
            "title":    row.title,
            "genres":   genres_list
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

def write_users(user_ids):
    """
    Génère une entrée userId/username factice pour chaque userId.
    """
    db = get_db()
    coll = db.users
    coll.delete_many({})  # on vide avant
    fake = Faker()
    docs = [{"userId": int(uid), "username": fake.name()} for uid in sorted(user_ids)]
    if docs:
        coll.insert_many(docs)

def main():
    spark = SparkSession.builder \
        .appName("IngestToMongo") \
        .master("local[*]") \
        .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
        .getOrCreate()

    # 1. Chargement des CSV depuis HDFS
    movies = spark.read.csv(
        "hdfs://namenode:9000/movielens/processed/batch/movies_csv",
        header=True, inferSchema=True
    ).select("movieId","title","genres")

    ratings = spark.read.csv(
        "hdfs://namenode:9000/movielens/processed/batch/ratings_csv",
        header=True, inferSchema=True
    ).select("userId","movieId","rating","timestamp","year","month","day")

    db = get_db()
    # 2. Vider d'abord les collections
    db.movies.delete_many({})
    db.ratings.delete_many({})
    db.users.delete_many({})

    # 3. Écriture par partition
    movies.rdd.foreachPartition(write_movies)
    ratings.rdd.foreachPartition(write_ratings)

    # 4. Génération des users factices
    user_ids = ratings.select("userId").distinct().rdd.map(lambda r: r.userId).collect()
    write_users(user_ids)

    # 5. Création d'index pour accélérer les requêtes
    db.movies.create_index("title")
    db.ratings.create_index([("movieId", 1), ("rating", 1)])
    db.ratings.create_index("movieId")
    db.users.create_index("userId", unique=True)

    spark.stop()
    print("✅ Chargement Spark → MongoDB terminé")

if __name__ == "__main__":
    main()
