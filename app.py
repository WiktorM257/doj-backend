from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json, os
from datetime import datetime

# --------------------------------------
#  FLASK APP
# --------------------------------------
app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "schedule.json")
ARCHIVE_FILE = os.path.join(BASE_DIR, "archive.json")

# --------------------------------------
#  BACKUP DIRECTORY
# --------------------------------------
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
os.makedirs(BACKUP_DIR, exist_ok=True)

def save_backup():
    """Tworzy kopię zapasową schedule.json w osobnym pliku."""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_path = os.path.join(BACKUP_DIR, f"schedule_backup_{timestamp}.json")

        with open(DATA_FILE, "r", encoding="utf8") as src:
            data = json.load(src)

        with open(backup_path, "w", encoding="utf8") as dst:
            json.dump(data, dst, indent=4)

        print(f"[BACKUP] Utworzono kopię: {backup_path}")

    except Exception as e:
        print("[BACKUP ERROR]", e)


# --------------------------------------
#  INITIALIZE FILES IF MISSING
# --------------------------------------
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf8") as f:
        json.dump([], f, indent=4)

if not os.path.exists(ARCHIVE_FILE):
    with open(ARCHIVE_FILE, "w", encoding="utf8") as f:
        json.dump([], f, indent=4)


# --------------------------------------
#  GENERATOR ID: SA-2025-0001 →
# --------------------------------------
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


# --------------------------------------
#  API: ADD NEW SCHEDULE ENTRY
# --------------------------------------
@app.post("/api/add_schedule")
def add_schedule():
    data = request.json

    try:
        with open(DATA_FILE, "r", encoding="utf8") as f:
            schedule = json.load(f)
    except:
        schedule = []

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

    # save main schedule
    with open(DATA_FILE, "w", encoding="utf8") as f:
        json.dump(schedule, f, indent=4)

    save_backup()  # ⬅ AUTOMATYCZNY BACKUP

    return jsonify({"status": "ok", "added": entry})


# --------------------------------------
#  API: GET ALL SCHEDULE ENTRIES
# --------------------------------------
@app.get("/schedule.json")
def serve_schedule():
    return send_file(DATA_FILE)


# --------------------------------------
#  API: DELETE SCHEDULE ENTRY BY ID
# --------------------------------------
@app.post("/api/delete_schedule")
def delete_schedule():
    data = request.json
    case_id = data.get("id")

    if not case_id:
        return jsonify({"status": "error", "info": "missing id"}), 400

    with open(DATA_FILE, "r", encoding="utf8") as f:
        schedule = json.load(f)

    new_schedule = [s for s in schedule if s["id"] != case_id]

    if len(new_schedule) == len(schedule):
        return jsonify({"status": "not_found"}), 404

    with open(DATA_FILE, "w", encoding="utf8") as f:
        json.dump(new_schedule, f, indent=4)

    save_backup()  # ⬅ BACKUP PO USUNIĘCIU

    return jsonify({"status": "deleted", "id": case_id})


# --------------------------------------
#  API: ARCHIVE CASE
# --------------------------------------
@app.post("/api/archive_case")
def archive_case():
    data = request.json
    case_id = data.get("id")

    if not case_id:
        return jsonify({"status": "error", "info": "missing id"}), 400

    # Load active schedule
    with open(DATA_FILE, "r", encoding="utf8") as f:
        schedule = json.load(f)

    found = None
    new_schedule = []
    for s in schedule:
        if s["id"] == case_id:
            found = s
        else:
            new_schedule.append(s)

    if not found:
        return jsonify({"status": "not_found"}), 404

    # Load archive
    with open(ARCHIVE_FILE, "r", encoding="utf8") as f:
        archive = json.load(f)

    # Add extra fields for archive
    found["result"] = data.get("result")
    found["verdict"] = data.get("verdict")
    found["document"] = data.get("document")

    archive.append(found)

    # Save archive
    with open(ARCHIVE_FILE, "w", encoding="utf8") as f:
        json.dump(archive, f, indent=4)

    # Save schedule
    with open(DATA_FILE, "w", encoding="utf8") as f:
        json.dump(new_schedule, f, indent=4)

    save_backup()  # ⬅ BACKUP PO ARCHIWIZACJI

    return jsonify({"status": "archived", "id": case_id})


# --------------------------------------
#  API: GET ARCHIVE
# --------------------------------------
@app.get("/archive.json")
def serve_archive():
    return send_file(ARCHIVE_FILE)


# --------------------------------------
#  RUN LOCAL OR ON RENDER
# --------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
