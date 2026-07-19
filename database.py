"""
Database module for AI Resume Analyzer.
Handles SQLite connection, schema initialization, user auth, and analysis history.
"""

import hashlib
import json
import os
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

# Database file path
DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database")
DB_PATH = os.path.join(DB_DIR, "resume_analyzer.db")


def _ensure_db_dir() -> None:
    """Create database directory if it does not exist."""
    os.makedirs(DB_DIR, exist_ok=True)


@contextmanager
def get_connection():
    """Context manager for SQLite connections with row factory."""
    _ensure_db_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Initialize database tables if they do not exist."""
    _ensure_db_dir()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                resume_filename TEXT NOT NULL,
                job_description TEXT NOT NULL,
                ats_score REAL NOT NULL,
                match_percentage REAL NOT NULL,
                resume_skills TEXT NOT NULL,
                jd_skills TEXT NOT NULL,
                missing_skills TEXT NOT NULL,
                matched_skills TEXT NOT NULL,
                strengths TEXT NOT NULL,
                improvements TEXT NOT NULL,
                suggestions TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_analyses_user_id ON analyses(user_id)"
        )


def _hash_password(password: str, salt: str) -> str:
    """Hash password with SHA-256 and salt."""
    return hashlib.sha256(f"{salt}{password}".encode("utf-8")).hexdigest()


def register_user(username: str, email: str, password: str) -> tuple[bool, str]:
    """
    Register a new user.
    Returns (success, message).
    """
    username = username.strip()
    email = email.strip().lower()

    if not username or not email or not password:
        return False, "All fields are required."
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    if "@" not in email or "." not in email:
        return False, "Please enter a valid email address."

    salt = secrets.token_hex(16)
    password_hash = _hash_password(password, salt)
    created_at = datetime.utcnow().isoformat()

    try:
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO users (username, email, password_hash, salt, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (username, email, password_hash, salt, created_at),
            )
        return True, "Registration successful! Please log in."
    except sqlite3.IntegrityError:
        return False, "Username or email already exists."


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate user credentials.
    Returns user dict on success, None on failure.
    """
    username = username.strip()
    if not username or not password:
        return None

    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()

    if row is None:
        return None

    expected_hash = _hash_password(password, row["salt"])
    if expected_hash != row["password_hash"]:
        return None

    return {
        "id": row["id"],
        "username": row["username"],
        "email": row["email"],
        "created_at": row["created_at"],
    }


def save_analysis(user_id: int, data: Dict[str, Any]) -> int:
    """Save analysis result and return the new record ID."""
    created_at = datetime.utcnow().isoformat()
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO analyses (
                user_id, resume_filename, job_description, ats_score,
                match_percentage, resume_skills, jd_skills, missing_skills,
                matched_skills, strengths, improvements, suggestions, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                data["resume_filename"],
                data["job_description"],
                data["ats_score"],
                data["match_percentage"],
                json.dumps(data["resume_skills"]),
                json.dumps(data["jd_skills"]),
                json.dumps(data["missing_skills"]),
                json.dumps(data["matched_skills"]),
                json.dumps(data["strengths"]),
                json.dumps(data["improvements"]),
                json.dumps(data["suggestions"]),
                created_at,
            ),
        )
        return cursor.lastrowid


def get_user_analyses(user_id: int) -> List[Dict[str, Any]]:
    """Fetch all analyses for a user, newest first."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM analyses
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,),
        ).fetchall()

    return [_deserialize_analysis(row) for row in rows]


def get_analysis_by_id(analysis_id: int, user_id: int) -> Optional[Dict[str, Any]]:
    """Fetch a single analysis record belonging to the user."""
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT * FROM analyses
            WHERE id = ? AND user_id = ?
            """,
            (analysis_id, user_id),
        ).fetchone()

    if row is None:
        return None
    return _deserialize_analysis(row)


def get_user_stats(user_id: int) -> Dict[str, Any]:
    """Return aggregate statistics for the analytics dashboard."""
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                COUNT(*) AS total_analyses,
                AVG(ats_score) AS avg_ats_score,
                AVG(match_percentage) AS avg_match_percentage,
                MAX(ats_score) AS best_ats_score
            FROM analyses
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()

    return {
        "total_analyses": row["total_analyses"] or 0,
        "avg_ats_score": round(row["avg_ats_score"] or 0, 1),
        "avg_match_percentage": round(row["avg_match_percentage"] or 0, 1),
        "best_ats_score": round(row["best_ats_score"] or 0, 1),
    }


def _deserialize_analysis(row: sqlite3.Row) -> Dict[str, Any]:
    """Convert a database row into a Python dictionary."""
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "resume_filename": row["resume_filename"],
        "job_description": row["job_description"],
        "ats_score": row["ats_score"],
        "match_percentage": row["match_percentage"],
        "resume_skills": json.loads(row["resume_skills"]),
        "jd_skills": json.loads(row["jd_skills"]),
        "missing_skills": json.loads(row["missing_skills"]),
        "matched_skills": json.loads(row["matched_skills"]),
        "strengths": json.loads(row["strengths"]),
        "improvements": json.loads(row["improvements"]),
        "suggestions": json.loads(row["suggestions"]),
        "created_at": row["created_at"],
    }