import os
import time
import random
import json
from pymongo import MongoClient
from kafka import KafkaProducer

# === CONFIGURATION ===
USER_ID = 118205 # ID de l'utilisateur pour lequel on va envoyer des notes
NUM_RATINGS = 10
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017/movies")
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
TOPIC = "movielens_ratings"

# === INITIALISATION DU PRODUCTEUR KAFKA ===
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def get_movie_ids():
    """Récupère tous les movieId présent dans la collection movies."""
    client = MongoClient(MONGO_URI)
    db = client.get_default_database()
    ids = [doc["movieId"] for doc in db.movies.find({}, {"movieId": 1})]
    client.close()
    return ids

def produce_to_kafka(message: dict):
    """Envoie un message JSON au topic Kafka."""
    producer.send(TOPIC, message)
    producer.flush()

def main():
    # 1) Récupération des films
    movies = get_movie_ids()
    print(f"Nombre total de films : {len(movies)}")
    print(f"Nombre de notes à envoyer : {NUM_RATINGS}")

    # 2) Tirage aléatoire
    sample = random.sample(movies, min(NUM_RATINGS, len(movies)))
    print(f"Envoi de {len(sample)} notes pour l'utilisateur {USER_ID}…")

    # 3) Publication sur Kafka
    for mid in sample:
        msg = {
            "userId": USER_ID,
            "movieId": mid,
            "rating": round(random.uniform(1.0, 5.0), 1),
            "timestamp": int(time.time())
        }
        produce_to_kafka(msg)
        print("→ envoyé :", msg)
        time.sleep(0.1)

    # 4) Attente pour que le streaming traite les nouvelles notes
    print("⏳ Attente de la mise à jour des recommandations…")
    time.sleep(5)

    # 5) Lecture des recommandations mises à jour dans MongoDB
    client = MongoClient(MONGO_URI)
    db = client.get_default_database()
    rec = db.recommendations.find_one({"userId": USER_ID})
    print("✅ Recommandations mises à jour :", rec)
    client.close()

if __name__ == "__main__":
    main()
