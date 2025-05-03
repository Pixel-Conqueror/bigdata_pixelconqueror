import csv
import os
from pymongo import MongoClient  # type: ignore
from datetime import datetime
from faker import Faker  # type: ignore


def get_db():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017/movies")
    client = MongoClient(mongo_uri)
    return client.get_database()


def load_movies(db, file_path):
    movies_collection = db.movies
    movies_collection.delete_many({})

    inserted, failed = 0, 0
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        movies = []
        for row in reader:
            try:
                genres = row['genres'].split('|') if row['genres'] else []
                movie = {
                    "movieId": int(row['movieId']),
                    "title": row['title'],
                    "genres": genres
                }
                movies.append(movie)
                inserted += 1
            except Exception as e:
                print(f"[MOVIE ERROR] Ligne ignorée : {row} → {e}")
                failed += 1
        if movies:
            movies_collection.insert_many(movies)

    return {"inserted": inserted, "failed": failed}


def load_ratings(db, file_path, batch_size=10000):
    ratings_collection = db.ratings
    ratings_collection.delete_many({})

    inserted, failed = 0, 0
    batch = []

    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            try:
                rating = {
                    "userId": int(row['userId']),
                    "movieId": int(row['movieId']),
                    "rating": float(row['rating']),
                    "timestamp": datetime.strptime(row['timestamp'], "%Y-%m-%d %H:%M:%S")
                }
                batch.append(rating)
                inserted += 1
            except Exception as e:
                print(f"[RATING ERROR] Ligne ignorée : {row} → {e}")
                failed += 1

            if len(batch) >= batch_size:
                ratings_collection.insert_many(batch)
                batch = []

        if batch:
            ratings_collection.insert_many(batch)

    return {"inserted": inserted, "failed": failed}


def generate_users(db, ratings_file_path):
    fake = Faker()
    users_collection = db.users
    users_collection.delete_many({})

    user_ids = set()
    print("[USERS] Extraction des userId uniques...")

    # Lecture du CSV ligne par ligne pour rester memory-safe
    with open(ratings_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                user_id = int(row['userId'])
                user_ids.add(user_id)
            except Exception as e:
                print(f"[USER PARSE ERROR] {row} → {e}")

    print(f"[USERS] {len(user_ids)} utilisateurs uniques détectés.")

    users = []
    for uid in sorted(user_ids):
        users.append({
            "userId": uid,
            "username": fake.name()
        })

    if users:
        users_collection.insert_many(users)

    return {"inserted": len(users), "failed": 0}


def insert_data():
    db = get_db()

    try:
        movies_result = load_movies(db, "/data/datasets/movie.csv")
    except Exception as e:
        print(f"[FATAL] Movie insert failed: {e}")
        movies_result = {"inserted": 0, "failed": "FATAL"}

    try:
        users_result = generate_users(db, "/data/datasets/rating.csv")
    except Exception as e:
        print(f"[FATAL] User generation failed: {e}")
        users_result = {"inserted": 0, "failed": "FATAL"}

    try:
        ratings_result = load_ratings(db, "/data/datasets/rating.csv")
    except Exception as e:
        print(f"[FATAL] Rating insert failed: {e}")
        ratings_result = {"inserted": 0, "failed": "FATAL"}

    try:
        db.movies.create_index("title")
        db.ratings.create_index([("movieId", 1), ("rating", 1)])
        db.ratings.create_index("movieId")
    except Exception as e:
        print(f"[FATAL] Index creation failed: {e}")
        return {
            "status": "failed"
        }

    return {
        "status": "completed",
        "movies": movies_result,
        "users": users_result,
        "ratings": ratings_result
    }
