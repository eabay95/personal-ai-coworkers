from datetime import datetime, timezone

from memory.database import get_connection


def save_article(article):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO articles (
            title,
            source,
            url,
            published_date,
            relevance_score,
            recommended_date
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        article["title"],
        article["source"],
        article["url"],
        article["published_date"],
        article.get("score", 0),
        datetime.now(timezone.utc).isoformat()
    ))

    saved = cursor.rowcount > 0

    connection.commit()
    connection.close()

    return saved


def article_exists(url):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id FROM articles WHERE url = ?",
        (url,)
    )

    result = cursor.fetchone()

    connection.close()

    return result is not None


def get_recommended_articles():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM articles
        ORDER BY recommended_date DESC
    """)

    articles = [
        dict(row) for row in cursor.fetchall()
    ]

    connection.close()

    return articles


def mark_article_read(url):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE articles
        SET read_status = 1
        WHERE url = ?
    """, (url,))

    connection.commit()
    connection.close()


def get_read_count():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM articles
        WHERE read_status = 1
    """)

    count = cursor.fetchone()[0]

    connection.close()

    return count

def save_learning_progress(topic, score, notes):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO learning_progress (
            topic,
            score,
            notes,
            completed_date
        )
        VALUES (?, ?, ?, ?)
    """, (
        topic,
        score,
        notes,
        datetime.now(timezone.utc).isoformat()
    ))

    connection.commit()
    connection.close()


def get_learning_progress():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM learning_progress
        ORDER BY completed_date DESC
    """)

    progress = [
        dict(row) for row in cursor.fetchall()
    ]

    connection.close()

    return progress

def get_topic_preferences():
    progress = get_learning_progress()

    preferences = {}

    topics = [
        "agent",
        "llm",
        "rag",
        "retrieval",
        "cloud",
        "aws",
        "security",
        "python",
        "distributed",
        "machine learning"
    ]

    for entry in progress:
        title = entry["topic"].lower()
        score = entry["score"]

        for topic in topics:
            if topic in title:
                if topic not in preferences:
                    preferences[topic] = []

                preferences[topic].append(score)

    return {
        topic: sum(scores) / len(scores)
        for topic, scores in preferences.items()
    }