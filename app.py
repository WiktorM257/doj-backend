from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import sqlite3
import os

DB_PATH = "database.db"

app = Flask(__name__)
CORS(app)


# ------------------------------------------------
# DB CONNECTION
# ------------------------------------------------
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ------------------------------------------------
# INIT DB
# ------------------------------------------------
def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS schedule (
                id TEXT PRIMARY KEY,
                name TEXT,
                judge TEXT,
                prosecutor TEXT,
                defendant TEXT,
                lawyer TEXT,
                witnesses TEXT,
                room TEXT,
                date TEXT,
                time TEXT,
                parties TEXT,
                description TEXT,
                created_at TEXT
            );
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS archive (
                id TEXT PRIMARY KEY,
                name TEXT,
                judge TEXT,
                prosecutor TEXT,
                defendant TEXT,
                lawyer TEXT,
                witnesses TEXT,
                room TEXT,
                date TEXT,
                time TEXT,
                parties TEXT,
                description TEXT,
                result TEXT,
                verdict TEXT,
                document TEXT,
                created_at TEXT
            );
        """)

        conn.commit()


init_db()


# ------------------------------------------------
# GENERATE CASE ID
# ------------------------------------------------
def generate_case_id():
    year = datetime.now().year
    prefix = f"SA-{year}-"

    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id FROM schedule WHERE id LIKE ?",
            (f"{prefix}%",)
        ).fetchall()

    nums = []
    for r in rows:
        try:
            nums.append(int(r["id"].split("-")[-1]))
        except:
            pass

    n = max(nums) + 1 if nums else 1
    return f"{prefix}{n:04d}"


# ------------------------------------------------
# ADD SCHEDULE
# ------------------------------------------------
@app.post("/api/add_schedule")
def add_schedule():
    data = request.json
    case_id = generate_case_id()

    with get_conn() as conn:
        conn.execute("""
            INSERT INTO schedule (
                id, name, judge, prosecutor, defendant, lawyer,
                witnesses, room, date, time, parties, description, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            data.get("description"),
            datetime.now().isoformat()
        ))

        conn.commit()

    return jsonify({"status": "ok", "added": {"id": case_id, **data}})


# ------------------------------------------------
# GET SCHEDULE
# ------------------------------------------------
@app.get("/schedule.json")
def get_schedule():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM schedule ORDER BY date, time"
        ).fetchall()

    return jsonify([dict(r) for r in rows])


# ------------------------------------------------
# DELETE SCHEDULE
# ------------------------------------------------
@app.post("/api/delete_schedule")
def delete_schedule():
    case_id = request.json.get("id")

    with get_conn() as conn:
        conn.execute("DELETE FROM schedule WHERE id = ?", (case_id,))
        conn.commit()

    return jsonify({"status": "deleted"})


# ------------------------------------------------
# ARCHIVE CASE
# ------------------------------------------------
@app.post("/api/archive_case")
def archive_case():
    data = request.json
    case_id = data["id"]

    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM schedule WHERE id = ?",
            (case_id,)
        ).fetchone()

        if not row:
            return jsonify({"status": "not_found"}), 404

        case = dict(row)

        conn.execute("DELETE FROM schedule WHERE id = ?", (case_id,))

        conn.execute("""
            INSERT INTO archive (
                id, name, judge, prosecutor, defendant, lawyer,
                witnesses, room, date, time, parties, description,
                result, verdict, document, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            data.get("document"),
            datetime.now().isoformat()
        ))

        conn.commit()

    return jsonify({"status": "archived"})


# ------------------------------------------------
# GET ARCHIVE
# ------------------------------------------------
@app.get("/archive.json")
def get_archive():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM archive ORDER BY date, time"
        ).fetchall()

    return jsonify([dict(r) for r in rows])


# ------------------------------------------------
# RUN
# ------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
