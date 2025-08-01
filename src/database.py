import sqlite3
from typing import Any, Optional


def init_database():
    """Initialize the SQLite database with required tables"""
    conn = sqlite3.connect("bjj_app.db")
    cursor = conn.cursor()

    # Create students table with new fields
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            belt_color TEXT,
            no_gi_level TEXT,
            weight INTEGER,
            goals TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Create game_plans table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS game_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            tournament_name TEXT,
            division TEXT,
            weight_class TEXT,
            opponent_style TEXT,
            game_plan TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES students (id)
        )
    """
    )

    # Create progress_tracking table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS progress_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            technique TEXT NOT NULL,
            level TEXT NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES students (id)
        )
    """
    )

    # Create evaluation_results table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS evaluation_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_type TEXT,
            input_text TEXT,
            output_text TEXT,
            score REAL,
            feedback TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    conn.commit()
    conn.close()


def save_data_to_sqlite(table: str, data: dict[str, Any]) -> bool:
    """Save data to SQLite database"""
    try:
        conn = sqlite3.connect("bjj_app.db")
        cursor = conn.cursor()

        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data])
        values = list(data.values())

        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        cursor.execute(query, values)

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False


def update_data_in_sqlite(
    table: str, data: dict[str, Any], where_clause: str, where_args: tuple
) -> bool:
    """Update data in SQLite database"""
    try:
        conn = sqlite3.connect("bjj_app.db")
        cursor = conn.cursor()

        set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
        values = list(data.values()) + list(where_args)

        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        cursor.execute(query, values)

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating data: {e}")
        return False


def view_all_rows(table_name: str) -> list[tuple]:
    """View all rows from a table"""
    try:
        conn = sqlite3.connect("bjj_app.db")
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        conn.close()
        return rows
    except Exception as e:
        print(f"Error viewing data: {e}")
        return []


def get_student_by_id(student_id: int) -> Optional[dict[str, Any]]:
    """Get student information by ID"""
    try:
        conn = sqlite3.connect("bjj_app.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
        row = cursor.fetchone()

        conn.close()

        if row:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, row))
        return None
    except Exception as e:
        print(f"Error getting student: {e}")
        return None


def get_game_plans_by_user(user_id: int) -> list[dict[str, Any]]:
    """Get all game plans for a specific user"""
    try:
        conn = sqlite3.connect("bjj_app.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM game_plans WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        )
        rows = cursor.fetchall()

        conn.close()

        if rows:
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        return []
    except Exception as e:
        print(f"Error getting game plans: {e}")
        return []


def get_progress_by_user(user_id: int) -> list[dict[str, Any]]:
    """Get all progress tracking entries for a specific user"""
    try:
        conn = sqlite3.connect("bjj_app.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM progress_tracking WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        )
        rows = cursor.fetchall()

        conn.close()

        if rows:
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        return []
    except Exception as e:
        print(f"Error getting progress: {e}")
        return []


def save_evaluation_result(
    agent_type: str, input_text: str, output_text: str, score: float, feedback: str = ""
) -> bool:
    """Save evaluation results"""
    data = {
        "agent_type": agent_type,
        "input_text": input_text,
        "output_text": output_text,
        "score": score,
        "feedback": feedback,
    }
    return save_data_to_sqlite("evaluation_results", data)


def save_student_profile(student_data: dict[str, Any]) -> int:
    """Save or update student profile and return student ID"""
    try:
        conn = sqlite3.connect("bjj_app.db")
        cursor = conn.cursor()

        # Check if student already exists by name
        cursor.execute(
            "SELECT id FROM students WHERE name = ?", (student_data.get("name"),)
        )
        existing_student = cursor.fetchone()

        if existing_student:
            # Update existing student
            student_id = existing_student[0]
            set_clause = ", ".join(
                [f"{key} = ?" for key in student_data.keys() if key != "name"]
            )
            values = [
                student_data[key] for key in student_data.keys() if key != "name"
            ] + [student_id]

            query = f"UPDATE students SET {set_clause} WHERE id = ?"
            cursor.execute(query, values)
        else:
            # Insert new student
            columns = ", ".join(student_data.keys())
            placeholders = ", ".join(["?" for _ in student_data])
            values = list(student_data.values())

            query = f"INSERT INTO students ({columns}) VALUES ({placeholders})"
            cursor.execute(query, values)
            student_id = cursor.lastrowid

        conn.commit()
        conn.close()
        return student_id
    except Exception as e:
        print(f"Error saving student profile: {e}")
        return -1


def get_student_by_name(name: str) -> Optional[dict[str, Any]]:
    """Get student information by name"""
    try:
        conn = sqlite3.connect("bjj_app.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM students WHERE name = ?", (name,))
        row = cursor.fetchone()

        conn.close()

        if row:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, row))
        return None
    except Exception as e:
        print(f"Error getting student by name: {e}")
        return None


def get_all_students() -> list[dict[str, Any]]:
    """Get all students"""
    try:
        conn = sqlite3.connect("bjj_app.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM students ORDER BY name")
        rows = cursor.fetchall()

        conn.close()

        if rows:
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        return []
    except Exception as e:
        print(f"Error getting all students: {e}")
        return []
