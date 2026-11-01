from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from memory.database import initialize_database
from memory.learning_memory import (
    get_recommended_articles,
    get_read_count
)


def evaluate():
    initialize_database()

    articles = get_recommended_articles()

    if not articles:
        print("No articles available for evaluation.")
        return

    total = len(articles)

    unique_urls = len({
        article["url"] for article in articles
    })

    sources = {
        article["source"] for article in articles
    }

    valid_metadata = sum(
        1 for article in articles
        if article["title"]
        and article["source"]
        and article["url"]
        and article["published_date"]
    )

    recent = 0
    now = datetime.now(timezone.utc)

    for article in articles:
        try:
            published = parsedate_to_datetime(
                article["published_date"]
            )

            age = (now - published).days

            if 0 <= age <= 30:
                recent += 1

        except (ValueError, TypeError):
            pass

    print("\nDAILY TECH AGENT EVALUATION\n")

    print("Total recommendations:", total)

    print(
        "Unique article rate:",
        f"{unique_urls / total * 100:.1f}%"
    )

    print(
        "Metadata completeness:",
        f"{valid_metadata / total * 100:.1f}%"
    )

    print(
        "Articles published within 30 days:",
        f"{recent / total * 100:.1f}%"
    )

    print("Distinct publishers:", len(sources))

    print("Articles completed:", get_read_count())


if __name__ == "__main__":
    evaluate()