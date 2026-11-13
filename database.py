
import sqlite3
import json
from datetime import datetime

DB_NAME = "roadmap_database.db"


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# --------------------------------------------------
# DATABASE INITIALIZATION
# --------------------------------------------------

def init_db():

    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            preferred_language TEXT DEFAULT 'English',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Roadmaps table
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

    # Tasks table
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

    # Task progress table
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

    # NEW: Student profile table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_profiles (
            profile_id INTEGER PRIMARY KEY CHECK (profile_id = 1),
            full_name TEXT NOT NULL,
            email TEXT DEFAULT '',
            education TEXT DEFAULT '',
            career_goal TEXT DEFAULT '',
            skill_level TEXT DEFAULT 'Beginner',
            daily_time TEXT DEFAULT '1 hour',
            budget TEXT DEFAULT 'Free',
            preferred_language TEXT DEFAULT 'English',
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# --------------------------------------------------
# STUDENT PROFILE FUNCTIONS
# --------------------------------------------------

def save_student_profile(profile):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO student_profiles (
            profile_id,
            full_name,
            email,
            education,
            career_goal,
            skill_level,
            daily_time,
            budget,
            preferred_language,
            updated_at
        )
        VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?)

        ON CONFLICT(profile_id) DO UPDATE SET
            full_name = excluded.full_name,
            email = excluded.email,
            education = excluded.education,
            career_goal = excluded.career_goal,
            skill_level = excluded.skill_level,
            daily_time = excluded.daily_time,
            budget = excluded.budget,
            preferred_language = excluded.preferred_language,
            updated_at = excluded.updated_at
    """, (
        profile.get("full_name", "").strip(),
        profile.get("email", "").strip(),
        profile.get("education", "").strip(),
        profile.get("career_goal", "").strip(),
        profile.get("skill_level", "Beginner"),
        profile.get("daily_time", "1 hour"),
        profile.get("budget", "Free"),
        profile.get("preferred_language", "English"),
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()

    return True


def get_student_profile():

    conn = get_connection()

    row = conn.execute("""
        SELECT * FROM student_profiles
        WHERE profile_id = 1
    """).fetchone()

    conn.close()

    return dict(row) if row else None


# --------------------------------------------------
# SAVE ROADMAP
# --------------------------------------------------

def save_roadmap(full_name, career_goal, skill_level,
                 daily_time, budget, roadmap):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO users (full_name) VALUES (?)",
        (full_name,)
    )

    user_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO roadmaps
        (user_id, career_goal, skill_level, daily_time,
         budget, roadmap_title, roadmap_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        career_goal,
        skill_level,
        daily_time,
        budget,
        roadmap.get("title", "My Learning Roadmap"),
        json.dumps(roadmap)
    ))

    roadmap_id = cursor.lastrowid

    for week in roadmap.get("weeks", []):

        for topic in week.get("topics", []):

            cursor.execute("""
                INSERT INTO tasks
                (roadmap_id, week_number, topic, description,
                 assignment, mini_project)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                roadmap_id,
                week.get("week_number", 1),
                topic,
                week.get("theme", ""),
                week.get("practical_assignment", ""),
                week.get("mini_project", "")
            ))

            task_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO task_progress (task_id)
                VALUES (?)
            """, (task_id,))

    conn.commit()
    conn.close()

    return roadmap_id


# --------------------------------------------------
# GET ALL ROADMAPS
# --------------------------------------------------

def get_all_roadmaps():

    conn = get_connection()

    rows = conn.execute("""
        SELECT * FROM roadmaps
        ORDER BY roadmap_id DESC
    """).fetchall()

    conn.close()

    return [dict(row) for row in rows]


# --------------------------------------------------
# GET SINGLE ROADMAP
# --------------------------------------------------

def get_roadmap(roadmap_id):

    conn = get_connection()

    row = conn.execute("""
        SELECT * FROM roadmaps
        WHERE roadmap_id = ?
    """, (roadmap_id,)).fetchone()

    conn.close()

    if row is None:
        return None

    result = dict(row)
    result["roadmap"] = json.loads(result["roadmap_json"])

    return result


# --------------------------------------------------
# GET TASKS
# --------------------------------------------------

def get_tasks(roadmap_id):

    conn = get_connection()

    rows = conn.execute("""
        SELECT tasks.*, task_progress.is_completed,
               task_progress.completed_at
        FROM tasks
        LEFT JOIN task_progress
        ON tasks.task_id = task_progress.task_id
        WHERE tasks.roadmap_id = ?
        ORDER BY tasks.week_number, tasks.task_id
    """, (roadmap_id,)).fetchall()

    conn.close()

    return [dict(row) for row in rows]


# --------------------------------------------------
# UPDATE TASK PROGRESS
# --------------------------------------------------

def update_task_progress(task_id, is_completed):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE task_progress
        SET is_completed = ?, completed_at = ?
        WHERE task_id = ?
    """, (
        1 if is_completed else 0,
        datetime.now().isoformat() if is_completed else None,
        task_id
    ))

    conn.commit()

    updated = cursor.rowcount > 0

    conn.close()

    return updated


# --------------------------------------------------
# PROGRESS SUMMARY
# --------------------------------------------------

def get_progress_summary(roadmap_id):

    conn = get_connection()

    row = conn.execute("""
        SELECT COUNT(*) AS total,
               SUM(
                   CASE WHEN tp.is_completed = 1
                   THEN 1 ELSE 0 END
               ) AS completed
        FROM tasks t
        LEFT JOIN task_progress tp
        ON t.task_id = tp.task_id
        WHERE t.roadmap_id = ?
    """, (roadmap_id,)).fetchone()

    conn.close()

    total = row["total"] or 0
    completed = row["completed"] or 0

    return {
        "total": total,
        "completed": completed,
        "remaining": total - completed,
        "percentage": round(completed / total * 100, 1)
        if total else 0
    }


# --------------------------------------------------
# DELETE ROADMAP
# --------------------------------------------------

def delete_roadmap(roadmap_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM roadmaps
        WHERE roadmap_id = ?
    """, (roadmap_id,))

    conn.commit()

    deleted = cursor.rowcount > 0

    conn.close()

    return deleted


# --------------------------------------------------
# MAIN
# --------------------------------------------------
   
if __name__ == "__main__":

    init_db()

    print("Database initialized successfully!")
    print("Student Profile table is ready!")

    profile = {
        "full_name": "Test Student",
        "email": "test@example.com",
        "education": "BCA",
        "career_goal": "Digital Marketing",
        "skill_level": "Beginner",
        "daily_time": "1 hour",
        "budget": "Free",
        "preferred_language": "English"
    }

    save_student_profile(profile)

    print("PROFILE SAVED SUCCESSFULLY!")
    print(get_student_profile())

