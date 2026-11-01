from memory.database import initialize_database

from memory.learning_memory import (
    get_recommended_articles,
    get_read_count
)

initialize_database()

articles = get_recommended_articles()

print(f"Total recommended articles: {len(articles)}")
print(f"Total articles read: {get_read_count()}")

print("\nRecommendation History:\n")

for article in articles:
    print("Title:", article["title"])
    print("Source:", article["source"])
    print("Read:", bool(article["read_status"]))
    print()