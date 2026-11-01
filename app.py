import streamlit as st
from pathlib import Path
from memory.database import initialize_database
from memory.learning_memory import (
    get_recommended_articles,
    get_read_count
)
from memory.career_memory import (
    get_interview_history,
    get_session_results
)
from datetime import datetime
from workflows.daily_tech_graph import build_graph
import json
from agents.career_coach_agent import evaluate_job
from tools.question_generator import generate_questions
from tools.answer_evaluator import evaluate_answer

from memory.career_memory import (
    create_interview_session,
    save_interview_result,
    complete_interview_session
)

from reports.career_report import generate_career_report
from bs4 import BeautifulSoup
from html import unescape

from tools.opportunity_search import (
    search_greenhouse,
    search_lever
)

st.set_page_config(
    page_title="Personal AI Coworkers",
    page_icon="🤖",
    layout="wide"
)


initialize_database()

def finish_interview():
    interview = st.session_state["career_interview"]

    # Prevent saving the same interview twice.
    if interview["finished"]:
        return

    results = interview["results"]

    if not results:
        interview["finished"] = True
        return

    job = st.session_state["career_analysis"]["job"]

    session_id = create_interview_session(
        job["company"],
        job["job_title"]
    )

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

    interview["session_id"] = session_id
    interview["average_score"] = round(
        average_score,
        1
    )
    interview["finished"] = True

    generate_career_report()


st.title("Personal AI Coworkers")

st.caption(
    "Intelligent learning and career development agents"
)

st.divider()


tab1, tab2 = st.tabs([
    "Daily Tech Upgrade",
    "Personal Career Coach"
])


with tab1:
    st.header("DailyTechUpgradeAgent")

    st.write(
        "Discover technical articles, track your "
        "learning, and improve your engineering skills."
    )

    articles = get_recommended_articles()

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Recommended Articles",
            len(articles)
        )

    with col2:
        st.metric(
            "Articles Completed",
            get_read_count()
        )

    st.subheader("Latest Learning Brief")

    reports = sorted(
        Path("outputs").glob("daily_brief_*.md"),
        reverse=True
    )

    if reports:
        latest_report = reports[0]

        st.markdown(
            latest_report.read_text(
                encoding="utf-8"
            )
        )
    else:
        st.info(
            "No daily learning brief has been generated."
        )

    st.subheader("Recommendation History")

    for article in articles:
        with st.expander(article["title"]):
            st.write("Source:", article["source"])
            st.write(
                "Published:",
                article["published_date"]
            )

            st.write(
                "Reading Status:",
                "Completed"
                if article["read_status"]
                else "Not completed"
            )

            st.link_button(
                "Read Article",
                article["url"]
            )
    st.subheader("Daily Learning")

    if st.button(
        "Generate Today's Learning Brief",
        type="primary",
        key="generate_daily"
    ):
        today = datetime.now().strftime("%Y-%m-%d")

        output_file = Path(
            f"outputs/daily_brief_{today}.md"
        )

        if output_file.exists():
            st.info(
                "Today's learning brief already exists."
            )

        else:
            with st.spinner(
                "Finding and summarizing technical articles..."
            ):
                try:
                    graph = build_graph()

                    graph.invoke({
                        "profile": {},
                        "articles": [],
                        "selected_articles": [],
                        "daily_brief": ""
                    })

                    st.success(
                        "Daily learning brief generated!"
                    )

                    st.rerun()

                except Exception as error:
                    st.error(
                        f"Unable to generate brief: {error}"
                    )


with tab2:
    st.header("Personal Career Coach")

    st.write(
        "Prepare for internships through personalized "
        "technical interviews and career assessments."
    )

    sessions = get_interview_history()

    st.metric(
        "Interview Sessions",
        len(sessions)
    )

    st.subheader("Interview History")

    if not sessions:
        st.info(
            "No interview assessments recorded."
        )

    for session in sessions:
        label = (
            f"{session['company']} - "
            f"{session['job_title']}"
        )

        with st.expander(label):
            st.write(
                "Session ID:",
                session["id"]
            )

            st.write(
                "Average Score:",
                session["average_score"]
            )

            results = get_session_results(
                session["id"]
            )

            for result in results:
                st.markdown(
                    f"**{result['topic']}**"
                )

                st.write(
                    "Score:",
                    result["score"]
                )

                st.write(
                    "Feedback:",
                    result["feedback"]
                )

    st.subheader("Latest Career Readiness Report")

    career_reports = sorted(
        Path("outputs").glob(
            "career_readiness_session_*.md"
        ),
        key=lambda path: int(
            path.stem.rsplit("_", 1)[-1]
        ),
        reverse=True
    )

    if career_reports:
        latest = career_reports[0]

        st.markdown(
            latest.read_text(
                encoding="utf-8"
            )
        )
    else:
        st.info(
            "No career readiness report available."
        )

    st.divider()

    st.subheader("Discover Career Opportunities")

    st.write(
        "Search public company job boards for "
        "technical internships and research programs."
    )

    provider = st.selectbox(
        "Job Board Provider",
        ["Greenhouse", "Lever"]
    )

    company = st.text_input(
        "Company Name",
        placeholder="Example: Anthropic"
    )

    board_token = st.text_input(
        "Board Token",
        placeholder="Example: anthropic"
    )

    if st.button(
        "Search Opportunities",
        key="search_opportunities"
    ):
        if not company.strip() or not board_token.strip():
            st.warning(
                "Enter a company name and board token."
            )

        else:
            with st.spinner(
                "Searching published job opportunities..."
            ):
                try:
                    if provider == "Greenhouse":
                        jobs = search_greenhouse(
                            board_token.strip(),
                            company.strip()
                        )

                    else:
                        jobs = search_lever(
                            board_token.strip(),
                            company.strip()
                        )

                    st.session_state[
                        "discovered_opportunities"
                    ] = jobs

                    if jobs:
                        st.success(
                            f"Found {len(jobs)} opportunities!"
                        )
                    else:
                        st.info(
                            "No matching opportunities found."
                        )

                except Exception as error:
                    st.error(
                        f"Opportunity search failed: {error}"
                    )

    # Render results independently of the search button.
    # Streamlit reruns the script after every widget interaction.
    if "discovered_opportunities" in st.session_state:
        jobs = st.session_state["discovered_opportunities"]

        if jobs:
            st.subheader("Available Opportunities")

            selected_index = st.selectbox(
                "Choose an opportunity",
                list(range(len(jobs))),
                format_func=lambda i: (
                    f"{jobs[i]['title']} — "
                    f"{jobs[i]['location']}"
                )
            )

            selected_job = jobs[selected_index]

            st.write("**Company:**", selected_job["company"])
            st.write("**Category:**", selected_job["category"])
            st.write("**Location:**", selected_job["location"])

            st.link_button(
                "View Official Job Posting",
                selected_job["url"]
            )

            if st.button(
                "Analyze Selected Opportunity",
                key="analyze_selected_job"
            ):
                description = unescape(
                    selected_job.get("description", "")
                )

                description = BeautifulSoup(
                    description,
                    "html.parser"
                ).get_text("\n", strip=True)

                if not description:
                    st.warning(
                        "No job description was returned. "
                        "Open the official posting and "
                        "paste its description manually."
                    )
                else:
                    st.session_state["job_description_input"] = (
                        f"Company: {selected_job['company']}\n"
                        f"Position: {selected_job['title']}\n"
                        f"Location: {selected_job['location']}\n\n"
                        f"{description}"
                    )

                    for key in (
                        "career_analysis",
                        "interview_questions",
                        "career_interview"
                    ):
                        st.session_state.pop(key, None)

                    st.rerun()

    st.subheader("Analyze a Career Opportunity")

    job_description = st.text_area(
        "Paste a job description",
        height=250,
        key="job_description_input",
        placeholder=(
            "Paste an internship or software "
            "engineering job description here..."
        )
    )

    # Step 1: Analyze the job description
    if st.button(
        "Analyze Job",
        type="primary",
        key="analyze_job"
    ):
        if not job_description.strip():
            st.warning(
                "Please paste a job description first."
            )

        else:
            with st.spinner(
                "Analyzing job requirements..."
            ):
                try:
                    with open("data/profile.json") as file:
                        profile = json.load(file)

                    analysis = evaluate_job(
                        profile,
                        job_description
                    )

                    st.session_state["career_analysis"] = analysis
                    st.session_state["career_profile"] = profile

                    # Clear questions from any previous job
                    st.session_state.pop(
                        "interview_questions",
                        None
                    )

                    st.success(
                        "Job description analyzed!"
                    )

                except Exception as error:
                    st.error(
                        f"Job analysis failed: {error}"
                    )

    # Step 2: Display saved job analysis
    if "career_analysis" in st.session_state:

        analysis = st.session_state["career_analysis"]
        job = analysis["job"]

        st.subheader("Job Analysis Results")

        col1, col2 = st.columns(2)

        with col1:
            st.write(
                "**Position:**",
                job["job_title"]
            )

        with col2:
            st.write(
                "**Company:**",
                job["company"]
            )

        st.markdown("### Required Skills")

        for skill in job["required_skills"]:
            st.write("-", skill)

        st.markdown("### Potential Matches")

        for skill in analysis["matched_skills"]:
            st.write("-", skill)

        st.markdown("### Skills to Verify")

        for skill in analysis["potential_gaps"]:
            st.write("-", skill)

        # Step 3: Generate questions
        if st.button(
            "Generate Interview Questions",
            key="generate_questions"
        ):
            with st.spinner(
                "Preparing technical questions..."
            ):
                try:
                    questions = generate_questions(
                        job,
                        st.session_state["career_profile"]
                    )

                    st.session_state[
                        "interview_questions"
                    ] = questions

                    st.session_state.pop(
                        "career_interview",
                        None
                    )

                    st.success(
                        "Interview questions generated!"
                    )

                except Exception as error:
                    st.error(
                        f"Question generation failed: {error}"
                    )

    # Step 4: Interactive interview
    if "interview_questions" in st.session_state:

        questions = st.session_state["interview_questions"]

        st.subheader("Technical Interview")

        if "career_interview" not in st.session_state:

            st.write(
                f"{len(questions)} questions are ready."
            )

            if st.button(
                "Start Interview",
                type="primary"
            ):
                st.session_state["career_interview"] = {
                    "index": 0,
                    "phase": "main",
                    "results": [],
                    "follow_up": None,
                    "last_feedback": None,
                    "finished": False,
                    "session_id": None,
                    "average_score": None
                }

                st.rerun()

        else:
            interview = st.session_state[
                "career_interview"
            ]

            # Completed interview
            if interview["finished"]:

                st.success(
                    "Interview completed!"
                )

                if interview["session_id"] is not None:
                    st.metric(
                        "Average Assessment Score",
                        f"{interview['average_score']}/100"
                    )

                    st.write(
                        "Session ID:",
                        interview["session_id"]
                    )

                    st.info(
                        "Results saved. Your Career Readiness "
                        "Report has been generated."
                    )
                else:
                    st.info(
                        "No answers were evaluated."
                    )

            else:
                index = interview["index"]

                # Finish after the final question
                if index >= len(questions):

                    try:
                        finish_interview()
                        st.rerun()

                    except Exception as error:
                        st.error(
                            f"Could not save interview: {error}"
                        )

                else:
                    question = questions[index]

                    st.progress(
                        index / len(questions)
                    )

                    st.write(
                        f"Question {index + 1} "
                        f"of {len(questions)}"
                    )

                    st.write(
                        "**Topic:**",
                        question["topic"]
                    )

                    st.write(
                        "**Difficulty:**",
                        question["difficulty"]
                    )

                    # Display the latest evaluation
                    if interview["last_feedback"]:

                        with st.expander(
                            "Previous Answer Feedback",
                            expanded=True
                        ):
                            feedback = interview[
                                "last_feedback"
                            ]

                            st.metric(
                                "Score",
                                f"{feedback['overall_score']}/100"
                            )

                            st.write(
                                feedback["feedback"]
                            )

                            st.markdown(
                                "**Areas for improvement**"
                            )

                            for improvement in feedback[
                                "improvements"
                            ]:
                                st.write("-", improvement)

                    # Select current question
                    if interview["phase"] == "followup":

                        current_question = {
                            "topic": question["topic"],
                            "difficulty": question["difficulty"],
                            "question": interview["follow_up"],
                            "expected_concepts": question[
                                "expected_concepts"
                            ],
                            "follow_up": ""
                        }

                        st.warning(
                            "Follow-up Challenge"
                        )

                    else:
                        current_question = question

                    st.markdown(
                        current_question["question"]
                    )

                    # Answer form
                    with st.form(
                        key=(
                            f"answer_form_"
                            f"{index}_"
                            f"{interview['phase']}"
                        )
                    ):
                        answer = st.text_area(
                            "Your Answer",
                            height=180,
                            placeholder=(
                                "Explain your approach or "
                                "write your solution here..."
                            )
                        )

                        submitted = st.form_submit_button(
                            "Submit Answer",
                            type="primary"
                        )

                    if submitted:

                        answer = answer.strip()

                        if not answer:
                            st.warning(
                                "Enter an answer before submitting."
                            )

                        else:
                            with st.spinner(
                                "Evaluating your answer..."
                            ):
                                try:
                                    evaluation = evaluate_answer(
                                        current_question,
                                        answer
                                    )

                                    interview["results"].append({
                                        "question": current_question,
                                        "answer": answer,
                                        "evaluation": evaluation
                                    })

                                    interview["last_feedback"] = (
                                        evaluation
                                    )

                                    # Follow-up after a weak original answer
                                    if (
                                        interview["phase"] == "main"
                                        and evaluation["overall_score"] < 70
                                        and evaluation[
                                            "follow_up_question"
                                        ].strip()
                                    ):

                                        interview["phase"] = "followup"

                                        interview["follow_up"] = (
                                            evaluation[
                                                "follow_up_question"
                                            ]
                                        )

                                    else:
                                        interview["index"] += 1
                                        interview["phase"] = "main"
                                        interview["follow_up"] = None

                                    st.rerun()

                                except Exception as error:
                                    st.error(
                                        f"Evaluation failed: {error}"
                                    )

                    # Allow users to skip
                    if st.button(
                        "Skip Question",
                        key=(
                            f"skip_{index}_"
                            f"{interview['phase']}"
                        )
                    ):

                        if interview["phase"] == "followup":
                            interview["phase"] = "main"
                            interview["follow_up"] = None
                            interview["index"] += 1

                        else:
                            interview["index"] += 1

                        interview["last_feedback"] = None

                        st.rerun()
