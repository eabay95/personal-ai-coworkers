from collections import defaultdict

from memory.database import initialize_database

from memory.career_memory import (
    get_interview_history,
    get_session_results
)


def evaluate_career_agent():
    initialize_database()

    sessions = get_interview_history()

    if not sessions:
        print("No interview sessions available.")
        return

    total_sessions = len(sessions)
    all_results = []
    topic_scores = defaultdict(list)

    for session in sessions:
        results = get_session_results(
            session["id"]
        )

        for result in results:
            all_results.append(result)

            topic = normalize_topic(result["topic"])
            topic_scores[topic].append(
                result["score"]
            )

    total_answers = len(all_results)

    print("\nCAREER COACH EVALUATION\n")

    print(
        "Total Interview Sessions:",
        total_sessions
    )

    print(
        "Total Evaluated Answers:",
        total_answers
    )

    if total_answers == 0:
        print("No evaluated answers available.")
        return

    average_score = sum(
        result["score"]
        for result in all_results
    ) / total_answers

    print(
        "Overall Average Score:",
        round(average_score, 2)
    )

    print("\nTOPIC PERFORMANCE\n")

    for topic, scores in topic_scores.items():
        average = sum(scores) / len(scores)

        print(
            f"{topic}: {average:.1f}/100 "
            f"({len(scores)} assessments)"
        )

    print("\nSESSION HISTORY\n")

    for session in reversed(sessions):
        print(
            f"Session {session['id']}: "
            f"{session['average_score']}/100"
        )

def normalize_topic(topic):
    topic = topic.lower()

    if "python" in topic:
        return "Python Programming"

    if "data structures" in topic:
        return "Data Structures and Algorithms"

    if "rest api" in topic:
        return "REST API Development"

    if "backend" in topic:
        return "Backend Architecture"

    if "sql" in topic:
        return "SQL Databases"

    return topic.title()

if __name__ == "__main__":
    evaluate_career_agent()