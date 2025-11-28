from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from database import get_db, init_db

app = Flask(__name__)
CORS(app)

# Inicjalizacja bazy przy starcie
init_db()

# --------------------------------------
# GENERATOR ID
# --------------------------------------
def generate_case_id():
    year = datetime.now().year
    prefix = f"SA-{year}-"

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT id FROM schedule WHERE id LIKE ?", (f"{prefix}%",))
    ids = c.fetchall()

    nums = []
    for row in ids:
        try:
            nums.append(int(row["id"].split("-")[-1]))
        except:
            pass

    next_number = max(nums) + 1 if nums else 1
    return f"{prefix}{next_number:04d}"


# --------------------------------------
# API: ADD NEW SCHEDULE ENTRY
# --------------------------------------
@app.post("/api/add_schedule")
def add_schedule():
    data = request.json
    case_id = generate_case_id()

    conn = get_db()
    c = conn.cursor()

    c.execute("""
        INSERT INTO schedule
        (id, name, judge, prosecutor, defendant, lawyer, witnesses, room, date, time, parties, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        case_id,
        data.get("name"),
        data.get("judge"),
        data.get("prosecutor"),
        data.get("defendant"),
        data.get("lawyer"),
        data.get("witnesses"),
        data.get("room"),
        data.get("date"),
        data.get("time"),
        data.get("parties"),
        data.get("description")
    ))

    conn.commit()

    return jsonify({"status": "ok", "added": { "id": case_id, **data }})


# --------------------------------------
# API: GET SCHEDULE
# --------------------------------------
@app.get("/schedule.json")
def get_schedule():
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM schedule ORDER BY date, time")
    rows = [dict(row) for row in c.fetchall()]

    return jsonify(rows)


# --------------------------------------
# API: DELETE SCHEDULE ENTRY
# --------------------------------------
@app.post("/api/delete_schedule")
def delete_schedule():
    case_id = request.json.get("id")

    conn = get_db()
    c = conn.cursor()

    c.execute("DELETE FROM schedule WHERE id = ?", (case_id,))
    conn.commit()

    return jsonify({"status": "deleted"})


# --------------------------------------
# API: ARCHIVE CASE
# --------------------------------------
@app.post("/api/archive_case")
def archive_case():
    data = request.json
    case_id = data.get("id")

    conn = get_db()
    c = conn.cursor()

    # Pobierz sprawę
    c.execute("SELECT * FROM schedule WHERE id = ?", (case_id,))
    row = c.fetchone()

    if not row:
        return jsonify({"status": "not_found"}), 404

    case = dict(row)

    # Usuń z aktywnych
    c.execute("DELETE FROM schedule WHERE id = ?", (case_id,))

    # Zapisz do archiwum
    c.execute("""
        INSERT INTO archive
        (id, name, judge, prosecutor, defendant, lawyer, witnesses, room, date, time,
         parties, description, result, verdict, document)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        case_id,
        case["name"],
        case["judge"],
        case["prosecutor"],
        case["defendant"],
        case["lawyer"],
        case["witnesses"],
        case["room"],
        case["date"],
        case["time"],
        case["parties"],
        case["description"],
        data.get("result"),
        data.get("verdict"),
        data.get("document")
    ))

    conn.commit()

    return jsonify({"status": "archived"})


# --------------------------------------
# API: GET ARCHIVE
# --------------------------------------
@app.get("/archive.json")
def get_archive():
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM archive ORDER BY date, time")
    rows = [dict(row) for row in c.fetchall()]

    return jsonify(rows)


# --------------------------------------
# RUN
# --------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
