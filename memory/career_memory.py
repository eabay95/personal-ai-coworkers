import json
from datetime import datetime, timezone

from memory.database import get_connection


def create_interview_session(company, job_title):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO interview_sessions (
            company,
            job_title,
            session_date
        )
        VALUES (?, ?, ?)
    """, (
        company,
        job_title,
        datetime.now(timezone.utc).isoformat()
    ))

    session_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return session_id


def save_interview_result(session_id, result):
    connection = get_connection()
    cursor = connection.cursor()

    question = result["question"]
    evaluation = result["evaluation"]

    cursor.execute("""
        INSERT INTO interview_results (
            session_id,
            topic,
            difficulty,
            question,
            user_answer,
            score,
            feedback,
            strengths,
            improvements
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session_id,
        question["topic"],
        question["difficulty"],
        question["question"],
        result["answer"],
        evaluation["overall_score"],
        evaluation["feedback"],
        json.dumps(evaluation["strengths"]),
        json.dumps(evaluation["improvements"])
    ))

    connection.commit()
    connection.close()


def complete_interview_session(session_id, average_score):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE interview_sessions
        SET average_score = ?
        WHERE id = ?
    """, (
        average_score,
        session_id
    ))

    connection.commit()
    connection.close()


def get_interview_history():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM interview_sessions
        ORDER BY session_date DESC
    """)

    sessions = [
        dict(row) for row in cursor.fetchall()
    ]

    connection.close()

    return sessions


def get_session_results(session_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM interview_results
        WHERE session_id = ?
        ORDER BY id
    """, (session_id,))

    results = [
        dict(row) for row in cursor.fetchall()
    ]

    connection.close()

    return results