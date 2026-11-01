import json
from datetime import datetime
from pathlib import Path
from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from tools.article_search import search_articles
from tools.article_ranker import calculate_score
from tools.article_reader import read_article

from agents.daily_tech_agent import generate_daily_brief

from memory.database import initialize_database
from memory.learning_memory import (
    article_exists,
    save_article
)


class TechState(TypedDict):
    profile: dict
    articles: list[dict]
    selected_articles: list[dict]
    daily_brief: str


def load_profile(state):
    initialize_database()

    with open("data/profile.json") as file:
        profile = json.load(file)

    return {"profile": profile}


def discover_articles(state):
    articles = search_articles()

    print(f"Discovered {len(articles)} articles")

    return {"articles": articles}


def select_articles(state):
    candidates = []

    for article in state["articles"]:
        if article_exists(article["url"]):
            continue

        article = article.copy()
        article["score"] = calculate_score(article)
        candidates.append(article)

    candidates.sort(
        key=lambda article: article["score"],
        reverse=True
    )

    selected = []

    for article in candidates:
        content = read_article(article["url"])

        if len(content.strip()) < 500:
            continue

        article["content"] = content
        selected.append(article)

        if len(selected) == 3:
            break

    if len(selected) < 3:
        raise RuntimeError(
            "Insufficient new articles for today's brief."
        )

    print(f"Selected {len(selected)} articles")

    return {"selected_articles": selected}


def create_brief(state):
    brief = generate_daily_brief(
        state["selected_articles"],
        state["profile"]
    )

    return {"daily_brief": brief}


def save_results(state):
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    date = datetime.now().strftime("%Y-%m-%d")

    output_file = output_dir / f"daily_brief_{date}.md"

    output_file.write_text(
        state["daily_brief"],
        encoding="utf-8"
    )

    for article in state["selected_articles"]:
        save_article(article)

    print(f"Brief saved: {output_file}")

    return {}


def build_graph():
    graph = StateGraph(TechState)

    graph.add_node("load_profile", load_profile)
    graph.add_node("discover", discover_articles)
    graph.add_node("select", select_articles)
    graph.add_node("summarize", create_brief)
    graph.add_node("save", save_results)

    graph.add_edge(START, "load_profile")
    graph.add_edge("load_profile", "discover")
    graph.add_edge("discover", "select")
    graph.add_edge("select", "summarize")
    graph.add_edge("summarize", "save")
    graph.add_edge("save", END)

    return graph.compile()


if __name__ == "__main__":
    today = datetime.now().strftime("%Y-%m-%d")

    output_file = Path(
        f"outputs/daily_brief_{today}.md"
    )

    if output_file.exists():
        print("Today's learning brief already exists.")
        print(f"File: {output_file}")
    else:
        app = build_graph()

        result = app.invoke({
            "profile": {},
            "articles": [],
            "selected_articles": [],
            "daily_brief": ""
        })

        print("\nDailyTechUpgradeAgent completed!")