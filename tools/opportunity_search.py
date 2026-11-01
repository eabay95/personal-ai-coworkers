import requests
import re

INTERNSHIP_KEYWORDS = [
    "intern",
    "internship"
]

RESEARCH_KEYWORDS = [
    "fellow",
    "fellows",
    "fellowship",
    "research program"
]

TECHNICAL_KEYWORDS = [
    "software",
    "engineering",
    "machine learning",
    "artificial intelligence",
    "ai",
    "research",
    "backend",
    "infrastructure",
    "platform",
    "systems",
    "reinforcement learning",
    "security"
]

def contains_keyword(text, keyword):
    pattern = r"\b" + re.escape(keyword) + r"\b"

    return re.search(
        pattern,
        text,
        re.IGNORECASE
    ) is not None


def classify_opportunity(title):
    technical = any(
        contains_keyword(title, keyword)
        for keyword in TECHNICAL_KEYWORDS
    )

    if not technical:
        return None

    internship = any(
        contains_keyword(title, keyword)
        for keyword in INTERNSHIP_KEYWORDS
    )

    if internship:
        return "Internship"

    research = any(
        contains_keyword(title, keyword)
        for keyword in RESEARCH_KEYWORDS
    )

    if research:
        return "Research / Fellowship"

    return None


def is_relevant(title):
    return classify_opportunity(title) is not None

def search_greenhouse(board_token, company):
    url = (
        "https://boards-api.greenhouse.io/"
        f"v1/boards/{board_token}/jobs"
    )

    response = requests.get(
        url,
        timeout=15,
        params={"content": "true"}
    )

    response.raise_for_status()

    jobs = response.json().get("jobs", [])

    opportunities = []

    for job in jobs:
        title = job.get("title", "")

        if not is_relevant(title):
            continue

        opportunities.append({
            "company": company,
            "title": title,
            "location": job.get(
                "location", {}
            ).get("name", "Unknown"),
            "url": job.get("absolute_url", ""),
            "description": job.get("content", ""),
            "source": "Greenhouse",
            "category": classify_opportunity(title),
        })

    return opportunities


def search_lever(site, company):
    url = (
        f"https://api.lever.co/v0/postings/{site}"
    )

    response = requests.get(
        url,
        timeout=15,
        params={"mode": "json"}
    )

    response.raise_for_status()

    jobs = response.json()

    opportunities = []

    for job in jobs:
        title = job.get("text", "")

        if not is_relevant(title):
            continue

        categories = job.get("categories", {})

        opportunities.append({
            "company": company,
            "title": title,
            "location": categories.get(
                "location", "Unknown"
            ),
            "url": job.get("hostedUrl", ""),
            "description": job.get(
                "descriptionPlain", ""
            ),
            "source": "Lever",
            "category": classify_opportunity(title),
        })

    return opportunities