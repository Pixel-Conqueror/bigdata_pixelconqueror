import os
import json
from pymongo import MongoClient
from kafka import KafkaConsumer
from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALSModel

# === CONFIGURATION ===
MONGO_URI       = os.getenv("MONGO_URI", "mongodb://mongo:27017/movies")
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
TOPIC           = "movielens_ratings"
MODEL_PATH      = os.getenv("ALS_MODEL_PATH", "hdfs://namenode:9000/models/als")  
# Chemin HDFS (ou local) vers votre modèle ALS déjà entraîné

def save_rating_to_mongo(rating: dict):
    client = MongoClient(MONGO_URI)
    db = client.get_default_database()
    db.ratings.insert_one(rating)
    client.close()

def recompute_recommendations(user_id: int):
    # 1) On (re)charge Spark et le modèle ALS
    spark = SparkSession.builder \
        .appName("StreamingRecs") \
        .getOrCreate()

    # Charge toutes les notes (historiques + nouvelles) depuis MongoDB via Spark
    ratings_df = spark.read \
        .format("mongo") \
        .option("uri", MONGO_URI) \
        .option("collection", "ratings") \
        .load()
    
    # Charge le modèle ALS pré-entraîné
    model = ALSModel.load(MODEL_PATH)
    
    # Génère les Top-N recommandations pour TOUS les utilisateurs
    user_recs = model.recommendForAllUsers(10)
    
    # Filtre celles de notre utilisateur
    subset = user_recs.filter(f"userId = {user_id}") \
                      .select("recommendations") \
                      .collect()
    
    # Extrait la liste [(movieId, rating), …]
    recs = []
    if subset:
        recs = [(r.movieId, float(r.rating)) for r in subset[0].recommendations]
    
    spark.stop()
    
    # 2) On push en base les nouvelles recommandations
    client = MongoClient(MONGO_URI)
    db = client.get_default_database()
    db.recommendations.update_one(
        {"userId": user_id},
        {"$set": {"userId": user_id, "topN": recs}},
        upsert=True
    )
    client.close()
    print(f"✅ Recos mises à jour pour userId={user_id} : {recs}")

def main():
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=[KAFKA_BOOTSTRAP],
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="recs-streaming-group"
    )
    print("▶️ En attente de messages sur le topic", TOPIC)
    
    for msg in consumer:
        rating = msg.value
        print("← Reçu :", rating)
        
        # 1) Sauvegarde la note brute
        save_rating_to_mongo(rating)
        
        # 2) Relance le calcul des recommandations pour cet user
        recompute_recommendations(rating["userId"])

if __name__ == "__main__":
    main()
