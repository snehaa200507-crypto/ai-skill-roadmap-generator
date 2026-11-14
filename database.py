import sqlite3
import json
import hashlib
import hmac
import secrets
from datetime import datetime

DB_NAME = "roadmap_database.db"
PBKDF2_ITERATIONS = 240_000


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_password(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS
    )
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password, stored_hash):
    try:
        algorithm, iterations, salt_hex, digest_hex = stored_hash.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        candidate = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt_hex),
            int(iterations),
        )
        return hmac.compare_digest(candidate.hex(), digest_hex)
    except (ValueError, TypeError, AttributeError):
        return False


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                preferred_language TEXT DEFAULT 'English',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        user_columns = {
            row["name"]
            for row in cursor.execute("PRAGMA table_info(users)").fetchall()
        }
        if "email" not in user_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
        if "password_hash" not in user_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")

        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email_unique
            ON users(email COLLATE NOCASE)
            WHERE email IS NOT NULL AND email <> ''
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS roadmaps (
                roadmap_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                career_goal TEXT NOT NULL,
                skill_level TEXT,
                daily_time TEXT,
                budget TEXT,
                roadmap_title TEXT,
                roadmap_json TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
                    ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                roadmap_id INTEGER NOT NULL,
                week_number INTEGER,
                topic TEXT,
                description TEXT,
                assignment TEXT,
                mini_project TEXT,
                FOREIGN KEY (roadmap_id) REFERENCES roadmaps(roadmap_id)
                    ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_progress (
                progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER UNIQUE NOT NULL,
                is_completed INTEGER DEFAULT 0,
                completed_at TEXT,
                FOREIGN KEY (task_id) REFERENCES tasks(task_id)
                    ON DELETE CASCADE
            )
        """)

        profile_columns = {
            row["name"]
            for row in cursor.execute(
                "PRAGMA table_info(student_profiles)"
            ).fetchall()
        }
        if profile_columns and "user_id" not in profile_columns:
            legacy = cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                ("student_profiles_legacy",),
            ).fetchone()
            if not legacy:
                cursor.execute(
                    "ALTER TABLE student_profiles RENAME TO student_profiles_legacy"
                )
            else:
                cursor.execute("DROP TABLE student_profiles")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_profiles (
                user_id INTEGER PRIMARY KEY,
                full_name TEXT NOT NULL,
                email TEXT DEFAULT '',
                education TEXT DEFAULT '',
                career_goal TEXT DEFAULT '',
                skill_level TEXT DEFAULT 'Beginner',
                daily_time TEXT DEFAULT '1 hour',
                budget TEXT DEFAULT 'Free',
                preferred_language TEXT DEFAULT 'English',
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
                    ON DELETE CASCADE
            )
        """)
        conn.commit()
    finally:
        conn.close()


def register_user(full_name, email, password):
    full_name = (full_name or "").strip()
    email = (email or "").strip().lower()
    password = password or ""

    if not full_name:
        raise ValueError("Please enter your full name.")
    if not email or "@" not in email or "." not in email.split("@")[-1]:
        raise ValueError("Please enter a valid email address.")
    if len(password) < 8:
        raise ValueError("Password must contain at least 8 characters.")

    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT user_id FROM users WHERE lower(email)=lower(?)",
            (email,),
        ).fetchone()
        if existing:
            raise ValueError("An account with this email already exists.")

        cursor = conn.execute(
            """
            INSERT INTO users (full_name, email, password_hash)
            VALUES (?, ?, ?)
            """,
            (full_name, email, hash_password(password)),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def authenticate_user(email, password):
    email = (email or "").strip().lower()
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT user_id, full_name, email, password_hash
            FROM users WHERE lower(email)=lower(?)
            """,
            (email,),
        ).fetchone()
        if not row or not row["password_hash"]:
            return None
        if not verify_password(password or "", row["password_hash"]):
            return None
        return {
            "user_id": row["user_id"],
            "full_name": row["full_name"],
            "email": row["email"],
        }
    finally:
        conn.close()


def get_user_by_id(user_id):
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT user_id, full_name, email FROM users WHERE user_id=?",
            (user_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def save_student_profile(user_id, profile):
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO student_profiles (
                user_id, full_name, email, education, career_goal,
                skill_level, daily_time, budget, preferred_language, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                full_name=excluded.full_name,
                email=excluded.email,
                education=excluded.education,
                career_goal=excluded.career_goal,
                skill_level=excluded.skill_level,
                daily_time=excluded.daily_time,
                budget=excluded.budget,
                preferred_language=excluded.preferred_language,
                updated_at=excluded.updated_at
        """, (
            user_id,
            (profile.get("full_name") or "").strip(),
            (profile.get("email") or "").strip().lower(),
            (profile.get("education") or "").strip(),
            (profile.get("career_goal") or "").strip(),
            profile.get("skill_level", "Beginner"),
            profile.get("daily_time", "1 hour"),
            profile.get("budget", "Free"),
            profile.get("preferred_language", "English"),
            datetime.now().isoformat(),
        ))
        conn.commit()
        return True
    finally:
        conn.close()


def get_student_profile(user_id):
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM student_profiles WHERE user_id=?",
            (user_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def save_roadmap(user_id, full_name, career_goal, skill_level,
                 daily_time, budget, roadmap):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO roadmaps (
                user_id, career_goal, skill_level, daily_time, budget,
                roadmap_title, roadmap_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            career_goal,
            skill_level,
            daily_time,
            budget,
            roadmap.get("title", "My Learning Roadmap"),
            json.dumps(roadmap),
        ))
        roadmap_id = cursor.lastrowid

        for week in roadmap.get("weeks", []):
            for topic in week.get("topics", []):
                cursor.execute("""
                    INSERT INTO tasks (
                        roadmap_id, week_number, topic, description,
                        assignment, mini_project
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    roadmap_id,
                    week.get("week_number", 1),
                    topic,
                    week.get("theme", ""),
                    week.get("practical_assignment", ""),
                    week.get("mini_project", ""),
                ))
                cursor.execute(
                    "INSERT INTO task_progress (task_id) VALUES (?)",
                    (cursor.lastrowid,),
                )

        conn.commit()
        return roadmap_id
    finally:
        conn.close()


def get_all_roadmaps(user_id):
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM roadmaps WHERE user_id=? ORDER BY roadmap_id DESC",
            (user_id,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_roadmap(roadmap_id, user_id):
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM roadmaps WHERE roadmap_id=? AND user_id=?",
            (roadmap_id, user_id),
        ).fetchone()
        if row is None:
            return None
        result = dict(row)
        result["roadmap"] = json.loads(result["roadmap_json"])
        return result
    finally:
        conn.close()


def get_tasks(roadmap_id, user_id):
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT t.*, tp.is_completed, tp.completed_at
            FROM tasks t
            JOIN roadmaps r ON r.roadmap_id=t.roadmap_id
            LEFT JOIN task_progress tp ON tp.task_id=t.task_id
            WHERE t.roadmap_id=? AND r.user_id=?
            ORDER BY t.week_number, t.task_id
        """, (roadmap_id, user_id)).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def update_task_progress(task_id, user_id, is_completed):
    conn = get_connection()
    try:
        cursor = conn.execute("""
            UPDATE task_progress
            SET is_completed=?, completed_at=?
            WHERE task_id=? AND task_id IN (
                SELECT t.task_id
                FROM tasks t
                JOIN roadmaps r ON r.roadmap_id=t.roadmap_id
                WHERE r.user_id=?
            )
        """, (
            1 if is_completed else 0,
            datetime.now().isoformat() if is_completed else None,
            task_id,
            user_id,
        ))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def get_progress_summary(roadmap_id, user_id):
    conn = get_connection()
    try:
        row = conn.execute("""
            SELECT COUNT(*) AS total,
                   SUM(CASE WHEN tp.is_completed=1 THEN 1 ELSE 0 END) AS completed
            FROM tasks t
            JOIN roadmaps r ON r.roadmap_id=t.roadmap_id
            LEFT JOIN task_progress tp ON tp.task_id=t.task_id
            WHERE t.roadmap_id=? AND r.user_id=?
        """, (roadmap_id, user_id)).fetchone()
        total = row["total"] or 0
        completed = row["completed"] or 0
        return {
            "total": total,
            "completed": completed,
            "remaining": total - completed,
            "percentage": round(completed / total * 100, 1) if total else 0,
        }
    finally:
        conn.close()


def delete_roadmap(roadmap_id, user_id):
    conn = get_connection()
    try:
        cursor = conn.execute(
            "DELETE FROM roadmaps WHERE roadmap_id=? AND user_id=?",
            (roadmap_id, user_id),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
