from flask import Blueprint, jsonify, request  # type: ignore
from app.services.data_loader import insert_data

bp = Blueprint('routes', __name__)


@bp.route('/api/insert', methods=['GET'])
def insert_route():
    result = insert_data()
    return jsonify(result)


@bp.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello depuis Flask API 🚀"})


@bp.route('/api/data', methods=['POST'])
def receive_data():
    data = request.json
    return jsonify({"received": data})
