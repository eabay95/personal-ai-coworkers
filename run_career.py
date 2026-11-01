import json

from agents.career_coach_agent import evaluate_job
from tools.question_generator import generate_questions
from agents.career_coach_agent import (
    evaluate_job,
    conduct_interview
)
from memory.database import initialize_database
from memory.career_memory import (
    create_interview_session,
    save_interview_result,
    complete_interview_session
)

def main():
    initialize_database()
    with open("data/profile.json") as file:
        profile = json.load(file)

    print("\nPERSONAL AI CAREER COACH\n")

    print("Paste a job description below.")
    print("Type END on a new line when finished.\n")

    lines = []

    while True:
        line = input()

        if line.strip() == "END":
            break

        lines.append(line)

    job_description = "\n".join(lines)

    if not job_description.strip():
        print("No job description provided.")
        return

    result = evaluate_job(
        profile,
        job_description
    )

    job = result["job"]

    print("\nJOB ANALYSIS\n")

    print("Position:", job["job_title"])
    print("Company:", job["company"])

    print("\nRequired Skills:")
    for skill in job["required_skills"]:
        print("-", skill)

    print("\nPotential Matches:")
    for skill in result["matched_skills"]:
        print("-", skill)

    print("\nSkills Requiring Verification:")
    for skill in result["potential_gaps"]:
        print("-", skill)

    print("\nSuggested Interview Topics:")
    for topic in job["interview_topics"]:
        print("-", topic)

    questions = generate_questions(job, profile)

    print("\nPERSONALIZED INTERVIEW QUESTIONS\n")

    for index, question in enumerate(questions, 1):
        print(f"Question {index}")
        print("Topic:", question["topic"])
        print("Difficulty:", question["difficulty"])
        print("Question:", question["question"])
        print()

    start = input(
        "\nWould you like to start the interview? (yes/no): "
    ).strip().lower()

    if start in ("yes", "y"):
        session_id = create_interview_session(
            job["company"],
            job["job_title"]
        )
        results = conduct_interview(questions)

        if results:
            for result in results:
                save_interview_result(
                    session_id,
                    result
                )
            average_score = sum(
                result["evaluation"]["overall_score"]
                for result in results
            ) / len(results)

            complete_interview_session(
                session_id,
                average_score
            )

            print("\nINTERVIEW SUMMARY\n")

            print("Session ID:", session_id)

            print(
                "Questions completed:",
                len(results)
            )

            print(
                "Average score:",
                round(average_score, 1),
                "/ 100"
            )
            
            print("\nResults saved to database!")

        else:
            print("No questions were completed.")


if __name__ == "__main__":
    main()