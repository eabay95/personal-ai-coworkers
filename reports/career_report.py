from datetime import datetime
from pathlib import Path
from collections import defaultdict

from memory.database import initialize_database
from memory.career_memory import (
    get_interview_history,
    get_session_results
)


LEARNING_RESOURCES = {
    "python": [
        "Python Official Tutorial",
        "LeetCode Easy Python Problems"
    ],
    "data structures": [
        "NeetCode Practice Problems",
        "VisuAlgo"
    ],
    "rest api": [
        "FastAPI Documentation",
        "MDN HTTP Documentation"
    ],
    "sql": [
        "PostgreSQL Documentation",
        "SQLBolt"
    ],
    "system design": [
        "AWS Architecture Center",
        "System Design Primer"
    ]
}


def recommend_resources(topic):
    topic = topic.lower()

    for keyword, resources in LEARNING_RESOURCES.items():
        if keyword in topic:
            return resources

    return [
        "Official technical documentation",
        "Relevant coding exercises"
    ]


def generate_career_report():
    initialize_database()

    sessions = get_interview_history()

    if not sessions:
        print("No interview history found.")
        return

    latest = sessions[0]

    results = get_session_results(
        latest["id"]
    )

    topic_scores = defaultdict(list)

    for result in results:
        topic_scores[result["topic"]].append(
            result["score"]
        )

    averages = {
        topic: sum(scores) / len(scores)
        for topic, scores in topic_scores.items()
    }

    report = "# Personalized Career Readiness Report\n\n"

    report += (
        f"**Generated:** "
        f"{datetime.now().strftime('%Y-%m-%d')}\n\n"
    )

    report += f"**Company:** {latest['company']}\n\n"
    report += f"**Position:** {latest['job_title']}\n\n"

    report += "## Assessment Overview\n\n"

    report += (
        f"- Interview session: {latest['id']}\n"
        f"- Questions completed: {len(results)}\n"
        f"- Average assessment score: "
        f"{latest['average_score']}/100\n\n"
    )

    report += "## Technical Assessment Results\n\n"

    report += "| Topic | Score |\n"
    report += "|---|---:|\n"

    for topic, score in averages.items():
        report += f"| {topic} | {score:.1f}/100 |\n"

    report += "\n## Strengths and Improvement Areas\n\n"

    for topic, score in averages.items():
        if score >= 75:
            label = "Demonstrated strength in this session"
        elif score >= 50:
            label = "Developing understanding"
        else:
            label = "Needs further assessment and practice"

        report += f"- **{topic}:** {label}\n"

    report += "\n## Recommended Learning Resources\n\n"

    for topic in averages:
        report += f"### {topic}\n\n"

        for resource in recommend_resources(topic):
            report += f"- {resource}\n"

        report += "\n"

    report += "## Seven-Day Preparation Plan\n\n"

    plan = [
        "Review assessment feedback and identify mistakes.",
        "Practice Python fundamentals and one easy coding problem.",
        "Practice linked lists and pointer manipulation.",
        "Review REST API design and HTTP methods.",
        "Study SQL queries and database fundamentals.",
        "Complete a timed technical practice session.",
        "Retake an assessment and compare results."
    ]

    for day, task in enumerate(plan, 1):
        report += f"- **Day {day}:** {task}\n"

    report += "\n## Next Steps\n\n"
    report += (
        "Complete the recommended exercises, "
        "record your learning progress, and "
        "take another technical assessment to "
        "measure improvement.\n"
    )

    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    output_file = (
        output_dir /
        f"career_readiness_session_{latest['id']}.md"
    )

    output_file.write_text(
        report,
        encoding="utf-8"
    )

    print(f"Report generated: {output_file}")


if __name__ == "__main__":
    generate_career_report()