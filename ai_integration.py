import os
import json
import uuid
from typing import List

from openai import AsyncOpenAI
from models import Question

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def clean_json(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        parts = t.split("```")
        if len(parts) >= 2:
            t = parts[1].strip()
        if t.startswith("json"):
            t = t[4:].strip()
    return t


async def generate_coding_question(language: str, difficulty: str) -> Question:
    prompt = f"""
Generate a {difficulty} level coding question for {language}.

The question should test logical thinking and programming concepts.
Provide exactly 4 multiple choice options with only one correct answer.

Return ONLY valid JSON in this exact format:
{{
  "question": "Your question here",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "correct_answer": 0,
  "explanation": "Brief explanation of why this is correct"
}}
"""

    try:
        response = await client.responses.create(
            model=MODEL_NAME,
            input=[
                {
                    "role": "system",
                    "content": "You are an expert programming instructor creating coding quiz questions. Output only JSON.",
                },
                {"role": "user", "content": prompt},
            ],
        )

        question_data = json.loads(clean_json(response.output_text))

        return Question(
            id=str(uuid.uuid4()),
            question=question_data["question"],
            options=question_data["options"],
            correct_answer=int(question_data["correct_answer"]),
            explanation=question_data["explanation"],
            difficulty=difficulty,
            language=language,
        )

    except Exception:
        return Question(
            id=str(uuid.uuid4()),
            question=f"What is a common data structure used to implement a stack in {language}?",
            options=["Array/List", "Hash Table", "Binary Tree", "Graph"],
            correct_answer=0,
            explanation="Arrays or Lists are commonly used to implement stacks with push/pop operations.",
            difficulty=difficulty,
            language=language,
        )


async def generate_multiple_questions(language: str, difficulty: str, count: int = 3) -> List[Question]:
    questions: List[Question] = []
    for _ in range(count):
        questions.append(await generate_coding_question(language, difficulty))
    return questions
