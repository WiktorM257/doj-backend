from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json, os
from datetime import datetime

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "schedule.json")

ARCHIVE_FILE = os.path.join(BASE_DIR, "archive.json")

# jeśli plik archiwum nie istnieje – utwórz
if not os.path.exists(ARCHIVE_FILE):
    with open(ARCHIVE_FILE, "w", encoding="utf8") as f:
        json.dump([], f, indent=4)


# ────────────────────────────────────────────────
#  JEŚLI schedule.json NIE ISTNIEJE → UTWÓRZ
# ────────────────────────────────────────────────
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf8") as f:
        json.dump([], f, indent=4)


# ────────────────────────────────────────────────
#  GENERATOR ID: SA-2025-0001 -> SA-2025-9999
# ────────────────────────────────────────────────
def generate_case_id(existing_cases):
    year = datetime.now().year
    prefix = f"SA-{year}-"

    nums = []
    for c in existing_cases:
        cid = c.get("id", "")
        if cid.startswith(prefix):
            try:
                nums.append(int(cid.split("-")[-1]))
            except:
                pass

    next_number = max(nums) + 1 if nums else 1

    return f"{prefix}{next_number:04d}"


# ────────────────────────────────────────────────
#  API: DODAWANIE NOWEJ ROZPRAWY
# ────────────────────────────────────────────────
@app.post("/api/add_schedule")
def add_schedule():
    data = request.json

    # wczytaj istniejące rozprawy
    try:
        with open(DATA_FILE, "r", encoding="utf8") as f:
            schedule = json.load(f)
    except:
        schedule = []

    # utwórz nowy wpis
    entry = {
        "id": generate_case_id(schedule),
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
        "description": data.get("description"),
    }

    schedule.append(entry)

    # zapis
    with open(DATA_FILE, "w", encoding="utf8") as f:
        json.dump(schedule, f, indent=4)

    return jsonify({"status": "ok", "added": entry})


# ────────────────────────────────────────────────
#  API: POBIERANIE WSZYSTKICH ROZPRAW
# ────────────────────────────────────────────────
@app.get("/schedule.json")
def serve_schedule():
    return send_file(DATA_FILE)


# ────────────────────────────────────────────────
#  API: USUWANIE ROZPRAWY PO ID (do slash command)
# ────────────────────────────────────────────────
@app.post("/api/delete_schedule")
def delete_schedule():
    data = request.json
    case_id = data.get("id")

    if not case_id:
        return jsonify({"status": "error", "info": "missing id"}), 400

    with open(DATA_FILE, "r", encoding="utf8") as f:
        schedule = json.load(f)

    new_schedule = [s for s in schedule if s["id"] != case_id]

    # brak takiego ID
    if len(new_schedule) == len(schedule):
        return jsonify({"status": "not_found"}), 404

    # zapisz po usunięciu
    with open(DATA_FILE, "w", encoding="utf8") as f:
        json.dump(new_schedule, f, indent=4)

    return jsonify({"status": "deleted", "id": case_id})

@app.post("/api/archive_case")
def archive_case():
    data = request.json
    case_id = data.get("id")

    if not case_id:
        return jsonify({"status": "error", "info": "missing id"}), 400

    # Wczytaj aktywne rozprawy
    with open(DATA_FILE, "r", encoding="utf8") as f:
        schedule = json.load(f)

    # Znajdź sprawę
    found = None
    new_schedule = []
    for s in schedule:
        if s["id"] == case_id:
            found = s
        else:
            new_schedule.append(s)

    if not found:
        return jsonify({"status": "not_found"}), 404

    # Wczytaj archiwum
    with open(ARCHIVE_FILE, "r", encoding="utf8") as f:
        archive = json.load(f)

    archive.append(found)

    # Zapisz archiwum
    with open(ARCHIVE_FILE, "w", encoding="utf8") as f:
        json.dump(archive, f, indent=4)

    # Zapisz aktywne bez tej sprawy
    with open(DATA_FILE, "w", encoding="utf8") as f:
        json.dump(new_schedule, f, indent=4)

    return jsonify({"status": "archived", "id": case_id})


# ────────────────────────────────────────────────
#  URUCHOMIENIE
# ────────────────────────────────────────────────
if __name__ == "__main__":
    # lokalnie
    app.run(host="0.0.0.0", port=5000)
