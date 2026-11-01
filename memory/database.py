import sqlite3
from pathlib import Path


DB_PATH = Path("data/learning_memory.db")


def get_connection():
    DB_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            source TEXT,
            url TEXT UNIQUE NOT NULL,
            published_date TEXT,
            relevance_score REAL,
            recommended_date TEXT,
            read_status INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS learning_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            score REAL,
            notes TEXT,
            completed_date TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interview_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            job_title TEXT,
            session_date TEXT,
            average_score REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interview_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            topic TEXT,
            difficulty TEXT,
            question TEXT,
            user_answer TEXT,
            score REAL,
            feedback TEXT,
            strengths TEXT,
            improvements TEXT,
            FOREIGN KEY (session_id)
                REFERENCES interview_sessions(id)
        )
    """)

    connection.commit()
    connection.close()


if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully!")