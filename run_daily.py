import json
from pathlib import Path

from tools.article_search import search_articles
from tools.article_ranker import calculate_score
from tools.article_reader import read_article

from agents.daily_tech_agent import generate_daily_brief

from memory.database import initialize_database
from memory.learning_memory import (
    article_exists,
    save_article
)


def main():
    # Step 1: Initialize persistent memory
    initialize_database()

    # Step 2: Load user profile
    with open("data/profile.json") as file:
        profile = json.load(file)

    # Step 3: Discover articles
    articles = search_articles()

    print(f"Found {len(articles)} articles")

    # Step 4: Exclude previously recommended articles
    new_articles = []

    for article in articles:
        if not article_exists(article["url"]):
            new_articles.append(article)

    print(f"Found {len(new_articles)} new articles")

    # Step 5: Rank all new candidates
    ranked_articles = []

    for article in new_articles:
        article = article.copy()
        article["score"] = calculate_score(article)
        ranked_articles.append(article)

    ranked_articles.sort(
        key=lambda article: article["score"],
        reverse=True
    )

    # Step 6: Retrieve the best three readable articles
    selected_articles = []

    for article in ranked_articles:
        content = read_article(article["url"])

        if len(content.strip()) < 500:
            continue

        article["content"] = content
        selected_articles.append(article)

        if len(selected_articles) == 3:
            break

    if len(selected_articles) < 3:
        print(
            "Not enough new articles with readable content. "
            "Try again when more articles are published."
        )
        return

    # Step 7: Generate the daily learning brief
    brief = generate_daily_brief(
        selected_articles,
        profile
    )

    # Step 8: Save the brief
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "daily_brief.md"

    output_file.write_text(
        brief,
        encoding="utf-8"
    )

    # Step 9: Record recommendations in memory
    for article in selected_articles:
        save_article(article)

    print("\nDaily learning brief generated!")
    print(f"Saved to: {output_file}")


if __name__ == "__main__":
    main()