from workflows.career_graph import build_career_graph


def main():
    print("\nPERSONAL AI CAREER COACH")
    print("Powered by LangGraph\n")

    print("Paste a job description.")
    print("Type END when finished.\n")

    lines = []

    while True:
        line = input()

        if line.strip() == "END":
            break

        lines.append(line)

    job_description = "\n".join(lines).strip()

    if not job_description:
        print("No job description provided.")
        return

    app = build_career_graph()

    result = app.invoke({
        "profile": {},
        "job_description": job_description,
        "job_analysis": {},
        "questions": [],
        "results": [],
        "session_id": 0,
        "average_score": 0.0
    })

    print("\nCAREER COACH WORKFLOW COMPLETE")

    print("Session:", result["session_id"])

    print(
        "Average Score:",
        round(result["average_score"], 1)
    )


if __name__ == "__main__":
    main()