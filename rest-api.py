# ==== Cloud-side Flask API (Only Storage + Retrieval) ====

from flask import Flask, request, jsonify, abort
from datetime import datetime
import json
import os

app = Flask(__name__)

# ==== Configuration ==== #
API_TOKEN = "450ccb569f6b31d7b1a8d31f4871925295ffaf5879696d04f096cdc875c98643"
DATA_FILE = "iot_data.jsonl"  # Each line is a JSON object

# ==== Helper Functions ==== #
def save_data(entry):
    with open(DATA_FILE, 'a') as f:
        json.dump(entry, f)
        f.write("\n")

def read_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE) as f:
        return [json.loads(line) for line in f if line.strip()]

# ==== API ==== #

@app.route("/upload", methods=["POST"])
def upload_data():
    token = request.headers.get("Authorization")
    if token != f"Bearer {API_TOKEN}":
        abort(401, "Unauthorized")

    try:
        entry = request.get_json()
        if 'timestamp' not in entry:
            entry['timestamp'] = datetime.utcnow().isoformat()

        save_data(entry)
        return jsonify({"status": "success"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/get-data", methods=["GET"])
def get_data():
    token = request.headers.get("Authorization")
    if token != f"Bearer {API_TOKEN}":
        abort(401, "Unauthorized")