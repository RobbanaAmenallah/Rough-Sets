"""
Database Access Layer for RoughSet Challenge.
Supports Firebase Cloud Firestore with an automatic SQLite fallback when
Firebase credentials are not configured.
"""

import json
import os
import random
import sqlite3
import string
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from config import Config

# ==========================================================
# FIREBASE FIRESTORE INITIALIZATION
# ==========================================================
USE_FIREBASE = False
firestore_db = None

try:
    import firebase_admin
    from firebase_admin import credentials, firestore

    if not firebase_admin._apps:
        cred = None
        # Option 1: Load credentials directly from JSON string (e.g. Render/Heroku env var)
        if Config.FIREBASE_CREDENTIALS_JSON and len(Config.FIREBASE_CREDENTIALS_JSON.strip()) > 10:
            try:
                cert_dict = json.loads(Config.FIREBASE_CREDENTIALS_JSON)
                cred = credentials.Certificate(cert_dict)
            except Exception as e:
                print(f"[Firebase] Error parsing FIREBASE_CREDENTIALS_JSON: {e}")

        # Option 2: Load credentials from JSON file path or auto-detect standard filenames
        else:
            candidates = [
                Config.FIREBASE_CREDENTIALS_PATH,
                "serviceAccountKey.json",
                "firebase-key.json",
                "firebase.json"
            ]
            for path in candidates:
                if path and os.path.isfile(path):
                    try:
                        cred = credentials.Certificate(path)
                        print(f"[Firebase] Loaded credentials from file: {path}")
                        break
                    except Exception as e:
                        print(f"[Firebase] Error loading key from {path}: {e}")

        if cred:
            firebase_admin.initialize_app(cred)
            firestore_db = firestore.client()
            USE_FIREBASE = True
            print("[Firebase] Successfully connected to Firebase Cloud Firestore!")
        else:
            print("[Database] No Firebase credentials found. Running in local SQLite mode.")
    else:
        firestore_db = firestore.client()
        USE_FIREBASE = True
except Exception as e:
    print(f"[Database] Firebase initialization skipped: {e}. Running with local SQLite.")
    USE_FIREBASE = False


# ==========================================================
# SQLITE LOCAL STORAGE ENGINE (FALLBACK / OFFLINE)
# ==========================================================
SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), "roughset_local.db")


def init_sqlite_db():
    """Initializes local SQLite tables with the schema."""
    conn = sqlite3.connect(SQLITE_DB_PATH, timeout=15)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS classroom_sessions (
        id TEXT PRIMARY KEY,
        code TEXT UNIQUE NOT NULL,
        active INTEGER DEFAULT 1,
        joining_open INTEGER DEFAULT 1,
        created_at TEXT NOT NULL,
        ended_at TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS players (
        id TEXT PRIMARY KEY,
        classroom_session_id TEXT NOT NULL,
        first_name TEXT NOT NULL,
        nickname TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (classroom_session_id) REFERENCES classroom_sessions(id)
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS game_progress (
        id TEXT PRIMARY KEY,
        player_id TEXT UNIQUE NOT NULL,
        current_level INTEGER DEFAULT 1,
        score INTEGER DEFAULT 0,
        started_at TEXT,
        completed_at TEXT,
        completed INTEGER DEFAULT 0,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (player_id) REFERENCES players(id)
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS level_results (
        id TEXT PRIMARY KEY,
        player_id TEXT NOT NULL,
        level_number INTEGER NOT NULL,
        score INTEGER DEFAULT 0,
        attempts INTEGER DEFAULT 1,
        completed_at TEXT NOT NULL,
        UNIQUE(player_id, level_number),
        FOREIGN KEY (player_id) REFERENCES players(id)
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS quiz_answers (
        id TEXT PRIMARY KEY,
        player_id TEXT NOT NULL,
        question_number INTEGER NOT NULL,
        correct INTEGER DEFAULT 0,
        points INTEGER DEFAULT 0,
        answered_at TEXT NOT NULL,
        UNIQUE(player_id, question_number),
        FOREIGN KEY (player_id) REFERENCES players(id)
    )
    """)
    conn.commit()
    conn.close()


# Always initialize SQLite tables so the fallback is always ready
init_sqlite_db()


def _get_sqlite_conn():
    conn = sqlite3.connect(SQLITE_DB_PATH, timeout=15)
    conn.row_factory = sqlite3.Row
    return conn


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ==========================================================
# CLASSROOM SESSION MANAGEMENT
# ==========================================================

def generate_classroom_code() -> str:
    """Generates a random 6-character code such as RS4821."""
    digits = "".join(random.choices(string.digits, k=4))
    return f"RS{digits}"


def create_classroom(code: Optional[str] = None) -> Dict[str, Any]:
    """Creates a new active classroom session or returns existing one if code matches."""
    session_code = (code or generate_classroom_code()).upper()
    existing = get_classroom_by_code(session_code)
    if existing:
        return existing

    session_id = str(uuid.uuid4())
    now = _now_iso()

    data = {
        "id": session_id,
        "code": session_code,
        "active": True,
        "joining_open": True,
        "created_at": now,
        "ended_at": None
    }

    if USE_FIREBASE and firestore_db:
        try:
            firestore_db.collection("classroom_sessions").document(session_id).set(data)
            return data
        except Exception as e:
            print(f"[Firebase] Write error ({e}). Falling back to local SQLite.")

    conn = _get_sqlite_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO classroom_sessions (id, code, active, joining_open, created_at) VALUES (?, ?, 1, 1, ?)",
        (session_id, session_code, now)
    )
    conn.commit()
    conn.close()
    return data


def get_classroom_by_code(code: str) -> Optional[Dict[str, Any]]:
    """Retrieves a classroom session by code (case-insensitive)."""
    clean_code = code.strip().upper()

    if USE_FIREBASE and firestore_db:
        try:
            docs = firestore_db.collection("classroom_sessions").where("code", "==", clean_code).limit(1).stream()
            for doc in docs:
                d = doc.to_dict()
                d["id"] = doc.id
                return d
            return None
        except Exception as e:
            print(f"[Firebase] Query error ({e}). Falling back to local SQLite.")

    conn = _get_sqlite_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM classroom_sessions WHERE UPPER(code) = ?", (clean_code,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def get_classroom_by_id(classroom_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a classroom session by ID."""
    if USE_FIREBASE and firestore_db:
        try:
            doc = firestore_db.collection("classroom_sessions").document(classroom_id).get()
            if doc.exists:
                d = doc.to_dict()
                d["id"] = doc.id
                return d
            return None
        except Exception as e:
            print(f"[Firebase] get_classroom_by_id error: {e}")

    conn = _get_sqlite_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM classroom_sessions WHERE id = ?", (classroom_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def toggle_classroom_joining(classroom_id: str, joining_open: bool) -> bool:
    """Opens or closes joining for a classroom."""
    if USE_FIREBASE and firestore_db:
        try:
            firestore_db.collection("classroom_sessions").document(classroom_id).update({
                "joining_open": joining_open
            })
            return True
        except Exception as e:
            print(f"[Firebase] toggle_classroom_joining error: {e}")

    conn = _get_sqlite_conn()
    cur = conn.cursor()
    cur.execute("UPDATE classroom_sessions SET joining_open = ? WHERE id = ?", (1 if joining_open else 0, classroom_id))
    conn.commit()
    conn.close()
    return True


def end_classroom(classroom_id: str) -> bool:
    """Ends a challenge session."""
    now = _now_iso()
    if USE_FIREBASE and firestore_db:
        try:
            firestore_db.collection("classroom_sessions").document(classroom_id).update({
                "active": False,
                "joining_open": False,
                "ended_at": now
            })
            return True
        except Exception as e:
            print(f"[Firebase] end_classroom error: {e}")

    conn = _get_sqlite_conn()
    cur = conn.cursor()
    cur.execute("UPDATE classroom_sessions SET active = 0, joining_open = 0, ended_at = ? WHERE id = ?", (now, classroom_id))
    conn.commit()
    conn.close()
    return True


# ==========================================================
# PLAYER & PROGRESS MANAGEMENT
# ==========================================================

def create_player(classroom_session_id: str, first_name: str, nickname: str) -> Dict[str, Any]:
    """Creates a player and initializes game progress."""
    player_id = str(uuid.uuid4())
    progress_id = str(uuid.uuid4())
    now = _now_iso()

    clean_first_name = first_name.strip()[:50]
    clean_nickname = (nickname.strip() if nickname else first_name.strip())[:50]

    player_data = {
        "id": player_id,
        "classroom_session_id": classroom_session_id,
        "first_name": clean_first_name,
        "nickname": clean_nickname,
        "created_at": now
    }

    progress_data = {
        "id": progress_id,
        "player_id": player_id,
        "current_level": 1,
        "score": 0,
        "started_at": None,
        "completed_at": None,
        "completed": False,
        "updated_at": now
    }

    if USE_FIREBASE and firestore_db:
        try:
            firestore_db.collection("players").document(player_id).set(player_data)
            firestore_db.collection("game_progress").document(player_id).set(progress_data)
            return player_data
        except Exception as e:
            print(f"[Firebase] create_player error: {e}")

    conn = _get_sqlite_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO players (id, classroom_session_id, first_name, nickname, created_at) VALUES (?, ?, ?, ?, ?)",
        (player_id, classroom_session_id, clean_first_name, clean_nickname, now)
    )
    cur.execute(
        "INSERT INTO game_progress (id, player_id, current_level, score, started_at, completed_at, completed, updated_at) VALUES (?, ?, 1, 0, NULL, NULL, 0, ?)",
        (progress_id, player_id, now)
    )
    conn.commit()
    conn.close()
    return player_data


def get_player(player_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves player information and their current progress."""
    if USE_FIREBASE and firestore_db:
        try:
            p_doc = firestore_db.collection("players").document(player_id).get()
            if p_doc.exists:
                player = p_doc.to_dict()
                player["id"] = p_doc.id

                prog_doc = firestore_db.collection("game_progress").document(player_id).get()
                player["progress"] = prog_doc.to_dict() if prog_doc.exists else None
                return player
            return None
        except Exception as e:
            print(f"[Firebase] get_player error: {e}")

    conn = _get_sqlite_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM players WHERE id = ?", (player_id,))
    p_row = cur.fetchone()
    if not p_row:
        conn.close()
        return None
    player = dict(p_row)
    cur.execute("SELECT * FROM game_progress WHERE player_id = ?", (player_id,))
    prog_row = cur.fetchone()
    player["progress"] = dict(prog_row) if prog_row else None
    conn.close()
    return player


def start_player_mission(player_id: str) -> bool:
    """Sets the official started_at server timestamp when Accept Mission is clicked."""
    now = _now_iso()
    if USE_FIREBASE and firestore_db:
        try:
            prog_ref = firestore_db.collection("game_progress").document(player_id)
            prog_doc = prog_ref.get()
            if prog_doc.exists:
                current_data = prog_doc.to_dict()
                if not current_data.get("started_at"):
                    prog_ref.update({"started_at": now, "updated_at": now})
            return True
        except Exception as e:
            print(f"[Firebase] start_player_mission error: {e}")

    conn = _get_sqlite_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE game_progress SET started_at = COALESCE(started_at, ?), updated_at = ? WHERE player_id = ?",
        (now, now, player_id)
    )
    conn.commit()
    conn.close()
    return True


def update_score_and_level(player_id: str, added_xp: int, next_level: Optional[int] = None) -> Dict[str, Any]:
    """Safely increments the player score and updates their current level."""
    now = _now_iso()
    player = get_player(player_id)
    if not player or not player.get("progress"):
        return {"success": False, "score": 0}

    curr_score = player["progress"].get("score", 0)
    curr_level = player["progress"].get("current_level", 1)
    
    new_score = max(0, curr_score + added_xp)
    new_level = max(curr_level, next_level) if next_level else curr_level

    if USE_FIREBASE and firestore_db:
        try:
            firestore_db.collection("game_progress").document(player_id).update({
                "score": new_score,
                "current_level": new_level,
                "updated_at": now
            })
            return {"success": True, "score": new_score, "current_level": new_level}
        except Exception as e:
            print(f"[Firebase] update_score_and_level error: {e}")

    conn = _get_sqlite_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE game_progress SET score = ?, current_level = ?, updated_at = ? WHERE player_id = ?",
        (new_score, new_level, now, player_id)
    )
    conn.commit()
    conn.close()
    return {"success": True, "score": new_score, "current_level": new_level}


def save_level_result(player_id: str, level_number: int, points_awarded: int, attempts: int = 1) -> Dict[str, Any]:
    """
    Saves the level completion result.
    Enforces uniqueness per (player_id, level_number) so points cannot be farmed.
    """
    doc_key = f"{player_id}_{level_number}"
    now = _now_iso()

    if USE_FIREBASE and firestore_db:
        try:
            doc_ref = firestore_db.collection("level_results").document(doc_key)
            doc = doc_ref.get()
            if doc.exists:
                return {"already_completed": True, "points_awarded": 0}
            
            doc_ref.set({
                "id": doc_key,
                "player_id": player_id,
                "level_number": level_number,
                "score": points_awarded,
                "attempts": attempts,
                "completed_at": now
            })
            update_score_and_level(player_id, points_awarded, next_level=level_number + 1)
            return {"already_completed": False, "points_awarded": points_awarded}
        except Exception as e:
            print(f"[Firebase] save_level_result error: {e}")

    conn = _get_sqlite_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO level_results (id, player_id, level_number, score, attempts, completed_at) VALUES (?, ?, ?, ?, ?, ?)",
            (doc_key, player_id, level_number, points_awarded, attempts, now)
        )
        conn.commit()
        conn.close()
        update_score_and_level(player_id, points_awarded, next_level=level_number + 1)
        return {"already_completed": False, "points_awarded": points_awarded}
    except sqlite3.IntegrityError:
        conn.close()
        return {"already_completed": True, "points_awarded": 0}


def save_quiz_answer(player_id: str, question_number: int, correct: bool, points: int) -> Dict[str, Any]:
    """
    Saves a quiz answer.
    Enforces uniqueness per (player_id, question_number).
    """
    doc_key = f"{player_id}_{question_number}"
    now = _now_iso()
    awarded = points if correct else 0

    if USE_FIREBASE and firestore_db:
        try:
            doc_ref = firestore_db.collection("quiz_answers").document(doc_key)
            doc = doc_ref.get()
            if doc.exists:
                return {"already_answered": True, "correct": correct, "points_awarded": 0}
            
            doc_ref.set({
                "id": doc_key,
                "player_id": player_id,
                "question_number": question_number,
                "correct": correct,
                "points": awarded,
                "answered_at": now
            })
            if awarded > 0:
                update_score_and_level(player_id, awarded)
            return {"already_answered": False, "correct": correct, "points_awarded": awarded}
        except Exception as e:
            print(f"[Firebase] save_quiz_answer error: {e}")

    conn = _get_sqlite_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO quiz_answers (id, player_id, question_number, correct, points, answered_at) VALUES (?, ?, ?, ?, ?, ?)",
            (doc_key, player_id, question_number, 1 if correct else 0, awarded, now)
        )
        conn.commit()
        conn.close()
        if awarded > 0:
            update_score_and_level(player_id, awarded)
        return {"already_answered": False, "correct": correct, "points_awarded": awarded}
    except sqlite3.IntegrityError:
        conn.close()
        return {"already_answered": True, "correct": correct, "points_awarded": 0}


def complete_game(player_id: str) -> Dict[str, Any]:
    """Marks the player's game as complete with official completed_at timestamp."""
    now = _now_iso()
    if USE_FIREBASE and firestore_db:
        try:
            firestore_db.collection("game_progress").document(player_id).update({
                "completed": True,
                "completed_at": now,
                "updated_at": now
            })
            return {"completed": True, "completed_at": now}
        except Exception as e:
            print(f"[Firebase] complete_game error: {e}")

    conn = _get_sqlite_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE game_progress SET completed = 1, completed_at = ?, updated_at = ? WHERE player_id = ?",
        (now, now, player_id)
    )
    conn.commit()
    conn.close()
    return {"completed": True, "completed_at": now}


# ==========================================================
# LEADERBOARD & ANALYTICS
# ==========================================================

def format_duration(seconds: Optional[float]) -> str:
    """Formats seconds into MM:SS string."""
    if seconds is None or seconds < 0:
        return "--:--"
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"


def get_leaderboard(classroom_session_id: str) -> List[Dict[str, Any]]:
    """
    Returns the leaderboard for the classroom session:
    1. Highest final score
    2. Shortest completion time (as tiebreaker)
    """
    rows = []
    if USE_FIREBASE and firestore_db:
        try:
            players_docs = firestore_db.collection("players").where("classroom_session_id", "==", classroom_session_id).stream()
            for p_doc in players_docs:
                p_data = p_doc.to_dict()
                player_id = p_doc.id

                prog_doc = firestore_db.collection("game_progress").document(player_id).get()
                prog = prog_doc.to_dict() if prog_doc.exists else {}

                started = prog.get("started_at")
                completed_at = prog.get("completed_at")
                duration_secs = None
                if started and completed_at:
                    try:
                        s_dt = datetime.fromisoformat(started.replace("Z", "+00:00"))
                        c_dt = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
                        duration_secs = max(0, (c_dt - s_dt).total_seconds())
                    except Exception:
                        duration_secs = None

                rows.append({
                    "player_id": player_id,
                    "first_name": p_data.get("first_name", "Student"),
                    "nickname": p_data.get("nickname", "Student"),
                    "score": prog.get("score", 0),
                    "level": prog.get("current_level", 1),
                    "completed": bool(prog.get("completed", False)),
                    "duration_seconds": duration_secs,
                    "duration_formatted": format_duration(duration_secs)
                })
        except Exception as e:
            print(f"[Firebase] get_leaderboard error: {e}")

    if not rows:
        conn = _get_sqlite_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT p.id, p.first_name, p.nickname, g.score, g.current_level, g.started_at, g.completed_at, g.completed
            FROM players p
            LEFT JOIN game_progress g ON p.id = g.player_id
            WHERE p.classroom_session_id = ?
        """, (classroom_session_id,))
        for r in cur.fetchall():
            started = r["started_at"]
            completed_at = r["completed_at"]
            duration_secs = None
            if started and completed_at:
                try:
                    s_dt = datetime.fromisoformat(started.replace("Z", "+00:00"))
                    c_dt = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
                    duration_secs = max(0, (c_dt - s_dt).total_seconds())
                except Exception:
                    duration_secs = None

            rows.append({
                "player_id": r["id"],
                "first_name": r["first_name"],
                "nickname": r["nickname"],
                "score": r["score"] or 0,
                "level": r["current_level"] or 1,
                "completed": bool(r["completed"]),
                "duration_seconds": duration_secs,
                "duration_formatted": format_duration(duration_secs)
            })
        conn.close()

    # Sort leaderboard: score DESC, duration ASC
    def sort_key(item):
        dur = item["duration_seconds"] if (item["completed"] and item["duration_seconds"] is not None) else 999999
        return (-item["score"], dur)

    rows.sort(key=sort_key)
    for rank, item in enumerate(rows, start=1):
        item["rank"] = rank

    return rows


def get_classroom_stats(classroom_session_id: str) -> Dict[str, Any]:
    """Calculates summary metrics for the instructor admin view."""
    leaderboard = get_leaderboard(classroom_session_id)
    total_players = len(leaderboard)
    completed_players = sum(1 for p in leaderboard if p["completed"])
    
    if total_players > 0:
        avg_score = round(sum(p["score"] for p in leaderboard) / total_players)
    else:
        avg_score = 0

    completed_durations = [p["duration_seconds"] for p in leaderboard if p["completed"] and p["duration_seconds"] is not None]
    if completed_durations:
        avg_duration = round(sum(completed_durations) / len(completed_durations))
    else:
        avg_duration = None

    return {
        "total_players": total_players,
        "completed_players": completed_players,
        "average_score": avg_score,
        "average_time": format_duration(avg_duration),
        "leaderboard": leaderboard
    }
