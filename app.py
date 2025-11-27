from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json, os, time

app = Flask(__name__)
CORS(app)   # 🔥 Dopiero tutaj!

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "schedule.json")

# Jeśli nie ma pliku -> utwórz pusty
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf8") as f:
        json.dump([], f, indent=4)


@app.post("/api/add_schedule")
def add_schedule():
    data = request.json

    try:
        with open(DATA_FILE, "r", encoding="utf8") as f:
            schedule = json.load(f)
    except:
        schedule = []

    entry = {
        "id": int(time.time()),
        "name": data.get("name"),
        "judge": data.get("judge"),
        "prosecutor": data.get("prosecutor"),
        "defendant": data.get("defendant"),
        "lawyer": data.get("lawyer"),
        "witnesses": data.get("witnesses"),
        "room": data.get("room"),
        "date": data.get("date"),
        "time": data.get("time"),
        "parties": data.get("parties"),
        "description": data.get("description")
    }

    schedule.append(entry)

    with open(DATA_FILE, "w", encoding="utf8") as f:
        json.dump(schedule, f, indent=4)

    return jsonify({"status": "ok", "added": entry})


@app.get("/schedule.json")
def serve_schedule():
    return send_file(DATA_FILE)


# WYMAGANE PRZEZ RENDER
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
