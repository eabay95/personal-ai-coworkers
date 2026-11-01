from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from memory.learning_memory import get_topic_preferences

INTERESTS = {
    "agent": 5,
    "agentic": 5,
    "llm": 5,
    "rag": 5,
    "retrieval": 4,
    "machine learning": 4,
    "artificial intelligence": 4,
    "cloud": 3,
    "aws": 3,
    "distributed": 4,
    "backend": 4,
    "security": 3,
    "python": 3
}


def calculate_score(article):
    title = article["title"].lower()
    summary = article.get("summary", "").lower()

    score = 0

    for keyword, weight in INTERESTS.items():
        if keyword in title:
            score += weight * 2
        elif keyword in summary:
            score += weight

    # Prefer recently published articles.
    try:
        published = parsedate_to_datetime(
            article["published_date"]
        )

        if published.tzinfo is None:
            published = published.replace(tzinfo=timezone.utc)

        days_old = (
            datetime.now(timezone.utc) - published
        ).days

        if 0 <= days_old <= 7:
            score += 5
        elif 0 <= days_old <= 30:
            score += 3

    except (ValueError, TypeError, KeyError):
        pass

        # Personalize ranking using learning history.
    preferences = get_topic_preferences()

    article_text = (
        article["title"] + " " +
        article.get("summary", "")
    ).lower()

    for topic, understanding in preferences.items():
        if topic in article_text:
            if understanding >= 4:
                score += 2
            elif understanding <= 2:
                score += 3
            else:
                score += 1
                
    if "weekly roundup" in title:
        score -= 8

    return score


def rank_articles(articles):
    ranked = []

    for article in articles:
        article = article.copy()
        article["score"] = calculate_score(article)
        ranked.append(article)

    ranked.sort(
        key=lambda article: article["score"],
        reverse=True
    )

    return ranked[:3]