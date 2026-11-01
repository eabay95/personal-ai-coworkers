import requests
from bs4 import BeautifulSoup


def read_article(url):
    try:
        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": "PersonalAICoworkers/1.0"
            }
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove elements unrelated to article content.
        for element in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "aside"
        ]):
            element.decompose()

        article = soup.find("article")

        if article is None:
            article = soup.find("main")

        if article is None:
            return ""

        paragraphs = article.find_all(
            ["p", "h2", "h3"]
        )

        content = "\n".join(
            element.get_text(" ", strip=True)
            for element in paragraphs
        )

        return content[:15000]

    except requests.RequestException as error:
        print(f"Failed to retrieve {url}: {error}")
        return ""