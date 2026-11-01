from memory.database import initialize_database

from memory.learning_memory import (
    get_recommended_articles,
    mark_article_read,
    save_learning_progress,
    get_learning_progress,
    get_read_count
)


def record_feedback():
    initialize_database()

    articles = get_recommended_articles()

    unread = [
        article for article in articles
        if not article["read_status"]
    ]

    if not unread:
        print("No unread articles available.")
        return

    print("\nYOUR UNREAD ARTICLES\n")

    for index, article in enumerate(unread, 1):
        print(f"{index}. {article['title']}")

    try:
        choice = int(input("\nSelect an article number: "))

        if choice < 1 or choice > len(unread):
            print("Invalid selection.")
            return

        selected = unread[choice - 1]

        print(f"\nSelected: {selected['title']}")
        print(f"URL: {selected['url']}")

        completed = input(
            "\nHave you read this article? (yes/no): "
        ).strip().lower()

        if completed not in ("yes", "y"):
            print("Article remains unread.")
            return

        notes = input("\nWhat did you learn? ")

        while True:
            try:
                score = int(input(
                    "Rate your understanding (1-5): "
                ))

                if 1 <= score <= 5:
                    break

                print("Enter a number from 1 to 5.")

            except ValueError:
                print("Please enter a valid number.")

        save_learning_progress(
            selected["title"],
            score,
            notes
        )

        mark_article_read(selected["url"])

        print("\nLearning progress saved!")

    except ValueError:
        print("Please enter a valid article number.")


def show_progress():
    initialize_database()

    progress = get_learning_progress()

    print("\nYOUR LEARNING PROGRESS\n")
    print("Articles completed:", get_read_count())

    if not progress:
        print("No learning assessments recorded.")
        return

    for entry in progress:
        print("\nTopic:", entry["topic"])
        print("Understanding:", entry["score"], "/ 5")
        print("Notes:", entry["notes"])


if __name__ == "__main__":
    print("\nDAILY TECH UPGRADE AGENT")
    print("1. Record learning feedback")
    print("2. View learning progress")

    option = input("\nChoose an option: ").strip()

    if option == "1":
        record_feedback()
    elif option == "2":
        show_progress()
    else:
        print("Invalid option.")