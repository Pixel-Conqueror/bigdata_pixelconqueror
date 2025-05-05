from datetime import datetime
from flask import Blueprint, jsonify, request  # type: ignore
from app.enums.genres import GENRES
from pymongo import MongoClient  # type: ignore
import os

bp = Blueprint('routes', __name__)


def get_db():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017/movies")
    client = MongoClient(mongo_uri)
    return client.get_database()


@bp.route('/api/health', methods=['GET'])
def status():
    db = get_db()
    try:
        test_db = db.command("ping")
    except Exception as e:
        return jsonify({"error": "Database connection failed", "details": str(e)}), 500
    return jsonify({"status": "API is up ✅", "db_status": test_db}), 200


@bp.route('/api/shape', methods=['GET'])
def get_db_shape():
    db = get_db()

    # Récupérer les genres uniques

    total_movies = db.movies.count_documents({})
    total_ratings = db.ratings.count_documents({})
    total_users = db.users.count_documents({})

    return jsonify({
        "genres": GENRES,
        "total_movies": total_movies,
        "total_ratings": total_ratings,
        "total_users": total_users
    })


@bp.route('/api/movies', methods=['GET'])
def get_paginated_movies():
    db = get_db()
    try:
        page = int(request.args.get('page', 1))
        if page < 1:
            raise ValueError
    except ValueError:
        return jsonify({"error": "Invalid page number"}), 400

    title = request.args.get('title')
    genre = request.args.get('genre')

    if title and genre:
        return jsonify({"error": "Please use either 'title' or 'genre', not both."}), 400

    query = {}

    if title:
        # i = case-insensitive
        query['title'] = {"$regex": title, "$options": "i"}

    elif genre:
        if genre not in GENRES:
            return jsonify({"error": f"Genre '{genre}' is not valid."}), 400
        query['genres'] = genre

    page_size = 50
    skip_count = (page - 1) * page_size

    total_movies = db.movies.count_documents(query)
    total_pages = (total_movies + page_size - 1) // page_size

    cursor = db.movies.find(
        query,
        {"_id": 0, "movieId": 1, "title": 1, "genres": 1}
    ).sort("title", 1).skip(skip_count).limit(page_size)

    movies = list(cursor)

    return jsonify({
        "page": page,
        "page_size": page_size,
        "total_movies": total_movies,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
        "movies": movies
    })


@bp.route('/api/movies/<int:movie_id>', methods=['GET'])
def get_movie_details(movie_id):
    db = get_db()

    # 1. Récupérer le film
    movie = db.movies.find_one({"movieId": movie_id}, {
                               "_id": 0, "title": 1, "genres": 1})
    if not movie:
        return jsonify({"error": "Movie not found"}), 404

    # 2. Agrégation pour moyenne et total
    rating_stats = list(db.ratings.aggregate([
        {"$match": {"movieId": movie_id}},
        {
            "$group": {
                "_id": "$movieId",
                "avg_rating": {"$avg": "$rating"},
                "total_ratings": {"$sum": 1}
            }
        }
    ]))

    if not rating_stats:
        return jsonify({
            "movieId": movie_id,
            "title": movie["title"],
            "genres": movie["genres"],
            "avg_rating": None,
            "total_ratings": 0,
            "top_reviews": [],
            "worst_reviews": []
        })

    stats = rating_stats[0]
    avg_rating = round(stats["avg_rating"], 2)
    total_ratings = stats["total_ratings"]

    # 3. Top 5 ratings
    top_reviews = list(db.ratings.find(
        {"movieId": movie_id},
        {"_id": 0, "userId": 1, "rating": 1}
    ).sort("rating", -1).limit(5))

    # 4. Worst 5 ratings
    worst_reviews = list(db.ratings.find(
        {"movieId": movie_id},
        {"_id": 0, "userId": 1, "rating": 1}
    ).sort("rating", 1).limit(5))

    # 5. Récupération des users (batch)
    user_ids = {r["userId"] for r in top_reviews + worst_reviews}
    users = db.users.find({"userId": {"$in": list(user_ids)}}, {
                          "_id": 0, "userId": 1, "username": 1})
    user_map = {u["userId"]: u["username"] for u in users}

    def format_review(r):
        return {
            "userId": r["userId"],
            "username": user_map.get(r["userId"], "Unknown"),
            "rating": r["rating"]
        }
    # 6. Distribution des notes (0.5 → 5.0)
    distribution_pipeline = [
        {"$match": {"movieId": movie_id}},
        {"$group": {
            "_id": "$rating",
            "count": {"$sum": 1}
        }}
    ]
    dist_raw = db.ratings.aggregate(distribution_pipeline)

    # Init toutes les notes à 0
    rating_distribution = {f"{x/2:.1f}": 0 for x in range(1, 11)}

    for item in dist_raw:
        key = f"{item['_id']:.1f}"
        rating_distribution[key] = item["count"]

    return jsonify({
        "movieId": movie_id,
        "title": movie["title"],
        "genres": movie["genres"],
        "avg_rating": avg_rating,
        "total_ratings": total_ratings,
        "top_reviews": [format_review(r) for r in top_reviews],
        "worst_reviews": [format_review(r) for r in worst_reviews],
        "rating_distribution": rating_distribution
    })


@bp.route('/api/users/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    db = get_db()

    try:
        page = int(request.args.get('page', 1))
        if page < 1:
            raise ValueError
    except ValueError:
        return jsonify({"error": "Invalid page number"}), 400

    page_size = 50
    skip_count = (page - 1) * page_size

    user = db.users.find_one({"userId": user_id}, {
                             "_id": 0, "userId": 1, "username": 1})
    if not user:
        return jsonify({"error": "User not found"}), 404

    total_ratings = db.ratings.count_documents({"userId": user_id})
    total_pages = (total_ratings + page_size - 1) // page_size

    ratings_cursor = db.ratings.find(
        {"userId": user_id},
        {"_id": 0, "movieId": 1, "rating": 1, "timestamp": 1}
    ).sort("timestamp", -1).skip(skip_count).limit(page_size)

    ratings = list(ratings_cursor)
    movie_ids = [r["movieId"] for r in ratings]

    movies_info = db.movies.find(
        {"movieId": {"$in": movie_ids}},
        {"_id": 0, "movieId": 1, "title": 1, "genres": 1}
    )
    movie_map = {m["movieId"]: m for m in movies_info}

    enriched_ratings = []
    for r in ratings:
        movie = movie_map.get(r["movieId"])
        if movie:
            enriched_ratings.append({
                "movieId": r["movieId"],
                "title": movie["title"],
                "genres": movie["genres"],
                "rating": r["rating"],
                "timestamp": r["timestamp"].isoformat() if isinstance(r["timestamp"], datetime) else str(r["timestamp"])
            })

    reco_doc = db.recommendations.find_one(
        {"userId": user_id}, {"_id": 0, "recommendations": 1})
    recommended_movie_ids = reco_doc["recommendations"] if reco_doc else []

    recommended_movies_cursor = db.movies.find(
        {"movieId": {"$in": recommended_movie_ids}},
        {"_id": 0, "movieId": 1, "title": 1, "genres": 1}
    )
    recommended_movies = list(recommended_movies_cursor)

    return jsonify({
        "userId": user["userId"],
        "username": user["username"],
        "total_ratings": total_ratings,
        "ratings_page": page,
        "ratings_total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
        "ratings": enriched_ratings,
        "recommendations": recommended_movies
    })
