#!/usr/bin/env python3
# scripts/generate_all_recommendations.py

import os
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType
from pyspark.ml.recommendation import ALSModel
from pymongo import MongoClient

def get_db():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017/movies")
    client = MongoClient(mongo_uri)
    return client.get_default_database()

def main():
    # 1. Démarrer Spark
    spark = SparkSession.builder \
        .appName("GenerateAllRecs") \
        .master("local[*]") \
        .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
        .getOrCreate()

    # 2. Charger le modèle ALS
    model = ALSModel.load("hdfs://namenode:9000/movielens/models/als_best")

    # 3. Récupérer tous les userId en base Mongo
    db = get_db()
    user_ids = [doc["userId"] for doc in db.users.find({}, {"userId": 1})]
    if not user_ids:
        print("Aucun utilisateur trouvé en base.")
        spark.stop()
        return

    # 4. Créer un DataFrame Spark
    users_df = spark.createDataFrame(
        [(int(uid),) for uid in user_ids],
        schema=StructType([StructField("userId", IntegerType(), False)])
    )

    # 5. Calculer top-5 recommandations
    recs_df = model.recommendForUserSubset(users_df, 5) \
                   .selectExpr("userId", "transform(recommendations, x -> x.movieId) as recommendations")

    # 6. Écrire les recommandations en base
    for row in recs_df.collect():
        rec = {"userId": int(row.userId), "recommendations": [int(x) for x in row.recommendations]}
        db.recommendations.replace_one({"userId": rec["userId"]}, rec, upsert=True)

    print(f"✅ Recommandations recalculées pour {len(user_ids)} utilisateurs.")
    spark.stop()

if __name__ == "__main__":
    main()
