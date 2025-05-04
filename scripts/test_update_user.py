import os
import time
import random
import subprocess
import json
from pymongo import MongoClient

# === CONFIGURATION ===
USER_ID = 123  # Modifier ici
NUM_RATINGS = 10
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017/movies")
TOPIC = "movielens_ratings"


def get_movie_ids():
    client = MongoClient(MONGO_URI)
    db = client.get_default_database()
    ids = [doc["movieId"] for doc in db.movies.find({}, {"movieId": 1})]
    client.close()
    return ids


def produce_to_kafka(message: dict):
    # Envoie un seul message JSON au topic via kafka-console-producer
    p = subprocess.Popen(
        ["docker-compose", "exec", "-T", "kafka", "kafka-console-producer.sh",
         "--broker-list", "kafka:9092", "--topic", TOPIC],
        stdin=subprocess.PIPE
    )
    p.communicate(json.dumps(message).encode('utf-8'))


def main():
    movies = get_movie_ids()
    sample = random.sample(movies, min(NUM_RATINGS, len(movies)))
    print(f"Envoi de {len(sample)} notes pour l'utilisateur {USER_ID}... ")

    for mid in sample:
        msg = {
            "userId": USER_ID,
            "movieId": mid,
            "rating": round(random.uniform(1.0, 5.0), 1),
            "timestamp": int(time.time())
        }
        produce_to_kafka(msg)
        print("-> envoyé:", msg)
        time.sleep(0.1)

    print("Attente de la mise à jour des recommandations...")
    time.sleep(5)
    client = MongoClient(MONGO_URI)
    rec = client.get_default_database().recommendations.find_one({"userId": USER_ID})
    print("Recommandations mises à jour:", rec)
    client.close()


if __name__ == "__main__":
    main()
