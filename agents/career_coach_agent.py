from tools.job_analyzer import analyze_job_description
from tools.answer_evaluator import evaluate_answer

SKILL_ALIASES = {
    "python programming": "python",
    "python development": "python",
    "data structures and algorithms": "dsa",
    "rest api development": "rest api",
    "restful api": "rest api",
    "sql databases": "sql",
    "git version control": "git",
    "aws cloud experience": "aws",
    "retrieval augmented generation": "rag"
}


def normalize_skill(skill):
    skill = skill.lower().strip()

    return SKILL_ALIASES.get(skill, skill)


def evaluate_job(profile, job_description):
    job = analyze_job_description(job_description)

    demonstrated = {
        normalize_skill(skill)
        for skill in profile.get(
            "demonstrated_skills", []
        )
    }

    matched_skills = []
    potential_gaps = []

    for skill in job["required_skills"]:
        normalized = normalize_skill(skill)

        if normalized in demonstrated:
            matched_skills.append(skill)
        else:
            potential_gaps.append(skill)

    return {
        "job": job,
        "matched_skills": matched_skills,
        "potential_gaps": potential_gaps
    }

def conduct_interview(questions):
    results = []

    print("\nSTARTING TECHNICAL INTERVIEW\n")

    for index, question in enumerate(questions, 1):
        print("=" * 60)

        print(f"\nQUESTION {index}")
        print("Topic:", question["topic"])
        print("Difficulty:", question["difficulty"])

        print("\n" + question["question"])

        print("\nEnter your answer.")
        print("Type END on a new line when finished.\n")

        lines = []

        while True:
            line = input()

            if line.strip() == "END":
                break

            lines.append(line)

        answer = "\n".join(lines).strip()

        if not answer:
            print("No answer provided.")
            continue

        print("\nEvaluating your answer...\n")

        evaluation = evaluate_answer(
            question,
            answer
        )

        display_evaluation(evaluation)

        results.append({
            "question": question,
            "answer": answer,
            "evaluation": evaluation
        })

        # Ask a follow-up if the answer needs improvement.
        if evaluation["overall_score"] < 70:

            follow_up = evaluation["follow_up_question"]

            if follow_up.strip():
                print("\nFOLLOW-UP CHALLENGE\n")
                print(follow_up)

                print("\nEnter your answer.")
                print("Type END when finished.\n")

                follow_up_lines = []

                while True:
                    line = input()

                    if line.strip() == "END":
                        break

                    follow_up_lines.append(line)

                follow_up_answer = "\n".join(
                    follow_up_lines
                ).strip()

                if follow_up_answer:
                    follow_up_question = {
                        "topic": question["topic"],
                        "difficulty": question["difficulty"],
                        "question": follow_up,
                        "expected_concepts": question[
                            "expected_concepts"
                        ],
                        "follow_up": ""
                    }

                    follow_up_evaluation = evaluate_answer(
                        follow_up_question,
                        follow_up_answer
                    )

                    print("\nFOLLOW-UP EVALUATION\n")

                    display_evaluation(
                        follow_up_evaluation
                    )

                    results.append({
                        "question": follow_up_question,
                        "answer": follow_up_answer,
                        "evaluation": follow_up_evaluation
                    })

    return results

def display_evaluation(evaluation):
    print(
        "\nOverall Score:",
        evaluation["overall_score"],
        "/ 100"
    )

    print("\nStrengths:")
    for strength in evaluation["strengths"]:
        print("-", strength)

    print("\nAreas for Improvement:")
    for improvement in evaluation["improvements"]:
        print("-", improvement)

    print("\nFeedback:")
    print(evaluation["feedback"])