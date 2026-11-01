import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel


load_dotenv()

client = OpenAI()


class InterviewQuestion(BaseModel):
    topic: str
    difficulty: str
    question: str
    expected_concepts: list[str]
    follow_up: str


class InterviewQuestions(BaseModel):
    questions: list[InterviewQuestion]


def generate_questions(job, profile):
    prompt = f"""
Generate exactly three technical interview questions.

JOB TITLE:
{job['job_title']}

REQUIRED SKILLS:
{job['required_skills']}

INTERVIEW TOPICS:
{job['interview_topics']}

USER EXPERIENCE:
{profile.get('experience', {})}

PREFERRED LANGUAGE:
{profile.get('preferred_language', 'Python')}

Requirements:
1. Generate questions relevant to the job.
2. Include at least one coding question.
3. Include at least one backend or system design question.
4. Use increasing difficulty.
5. Provide expected technical concepts for grading.
6. Provide one follow-up challenge per question.
7. Do not include answers in the question text.
"""

    response = client.responses.parse(
        model=os.environ["OPENAI_MODEL"],
        instructions=(
            "You are a technical interviewer. "
            "Generate clear, relevant interview questions."
        ),
        input=prompt,
        text_format=InterviewQuestions
    )

    result = response.output_parsed

    if result is None:
        raise RuntimeError(
            "Question generation failed."
        )

    return result.model_dump()["questions"]