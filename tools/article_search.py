import feedparser
from tools.article_ranker import rank_articles
from tools.article_reader import read_article

SOURCES = {
    "AWS": "https://aws.amazon.com/blogs/aws/feed/",
    "Google Research": "https://research.google/blog/rss/",
    "Microsoft Research": "https://www.microsoft.com/en-us/research/feed/"
}


def search_articles():
    articles = []

    for source, url in SOURCES.items():
        feed = feedparser.parse(url)

        for entry in feed.entries[:10]:
            article = {
                "title": entry.get("title", ""),
                "source": source,
                "url": entry.get("link", ""),
                "published_date": entry.get("published", ""),
                "summary": entry.get("summary", "")
            }

            articles.append(article)

    return articles


if __name__ == "__main__":
    articles = search_articles()

    top_articles = rank_articles(articles)

    for article in top_articles:
        print("\n" + "=" * 60)
        print("Title:", article["title"])
        print("Source:", article["source"])

        content = read_article(article["url"])

        article["content"] = content

        print("Content length:", len(content))
        print("Preview:", content[:300])