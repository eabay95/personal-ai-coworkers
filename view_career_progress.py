from memory.database import initialize_database

from memory.career_memory import (
    get_interview_history,
    get_session_results
)

def main():
    initialize_database()

    sessions = get_interview_history()

    print("\nCAREER COACH PROGRESS\n")

    if not sessions:
        print("No completed interviews yet.")
        return

    for session in sessions:
        print("=" * 50)

        print("Session:", session["id"])
        print("Company:", session["company"])
        print("Position:", session["job_title"])

        print(
            "Average Score:",
            session["average_score"]
        )

        results = get_session_results(
            session["id"]
        )

        for result in results:
            print("\nTopic:", result["topic"])
            print("Score:", result["score"])
            print("Feedback:", result["feedback"])


if __name__ == "__main__":
    main()