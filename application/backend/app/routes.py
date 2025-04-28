from flask import Blueprint, jsonify, request

bp = Blueprint('routes', __name__)

# Simple route pour tester
@bp.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello depuis Flask API 🚀"})

# Exemple de POST
@bp.route('/api/data', methods=['POST'])
def receive_data():
    data = request.json
    return jsonify({"received": data})
