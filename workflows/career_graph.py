import json
from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from agents.career_coach_agent import (
    evaluate_job,
    conduct_interview
)

from tools.question_generator import generate_questions

from memory.database import initialize_database

from memory.career_memory import (
    create_interview_session,
    save_interview_result,
    complete_interview_session
)

from reports.career_report import generate_career_report


class CareerState(TypedDict):
    profile: dict
    job_description: str
    job_analysis: dict
    questions: list[dict]
    results: list[dict]
    session_id: int
    average_score: float


def load_profile(state):
    initialize_database()

    with open("data/profile.json") as file:
        profile = json.load(file)

    return {"profile": profile}


def analyze_job(state):
    analysis = evaluate_job(
        state["profile"],
        state["job_description"]
    )

    print("\nJOB ANALYSIS COMPLETE")
    print("Position:", analysis["job"]["job_title"])
    print("Company:", analysis["job"]["company"])

    return {"job_analysis": analysis}


def prepare_questions(state):
    questions = generate_questions(
        state["job_analysis"]["job"],
        state["profile"]
    )

    print(f"\nGenerated {len(questions)} questions")

    return {"questions": questions}


def run_interview(state):
    results = conduct_interview(
        state["questions"]
    )

    return {"results": results}


def save_assessment(state):
    job = state["job_analysis"]["job"]

    session_id = create_interview_session(
        job["company"],
        job["job_title"]
    )

    results = state["results"]

    for result in results:
        save_interview_result(
            session_id,
            result
        )

    average = 0.0

    if results:
        average = sum(
            result["evaluation"]["overall_score"]
            for result in results
        ) / len(results)

    complete_interview_session(
        session_id,
        average
    )

    print("\nAssessment saved!")
    print("Session ID:", session_id)
    print("Average Score:", round(average, 1))

    return {
        "session_id": session_id,
        "average_score": average
    }


def create_report(state):
    if not state["results"]:
        print("No completed answers; report skipped.")
        return {}

    generate_career_report()

    return {}


def build_career_graph():
    graph = StateGraph(CareerState)

    graph.add_node("load_profile", load_profile)
    graph.add_node("analyze_job", analyze_job)
    graph.add_node("prepare_questions", prepare_questions)
    graph.add_node("interview", run_interview)
    graph.add_node("save_assessment", save_assessment)
    graph.add_node("create_report", create_report)

    graph.add_edge(START, "load_profile")
    graph.add_edge("load_profile", "analyze_job")
    graph.add_edge("analyze_job", "prepare_questions")
    graph.add_edge("prepare_questions", "interview")
    graph.add_edge("interview", "save_assessment")
    graph.add_edge("save_assessment", "create_report")
    graph.add_edge("create_report", END)

    return graph.compile()