
import os
import json
import uuid
import asyncio
import logging
from typing import Any, Dict, List

import openai
from openai import AsyncOpenAI

from models import Question

logger = logging.getLogger(__name__)

client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    timeout=20.0,
)

MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def clean_json(text: str) -> str:
    t = (text or "").strip()

    if t.startswith("```"):
        parts = t.split("```")
        if len(parts) >= 2:
            t = parts[1].strip()
        if t.lower().startswith("json"):
            t = t[4:].strip()

    return t


def _fallback_question(language: str, difficulty: str) -> Question:
    return Question(
        id=str(uuid.uuid4()),
        question=f"What is a common data structure used to implement a stack in {language}?",
        options=["Array/List", "Hash Table", "Binary Tree", "Graph"],
        correct_answer=0,
        explanation="Arrays or lists are commonly used to implement stacks with push and pop operations.",
        difficulty=difficulty,
        language=language,
    )


def _normalize_and_validate_question_data(data: Dict[str, Any]) -> Dict[str, Any]:
    required_keys = {"question", "options", "correct_answer", "explanation"}
    missing = required_keys - set(data.keys())
    if missing:
        raise ValueError(f"Missing keys in model response: {missing}")

    question = str(data["question"]).strip()
    explanation = str(data["explanation"]).strip()

    if not isinstance(data["options"], list):
        raise ValueError("options must be a list")

    options = [str(option).strip() for option in data["options"]]

    try:
        correct_answer = int(data["correct_answer"])
    except (TypeError, ValueError) as exc:
        raise ValueError("correct_answer must be an integer") from exc

    if not question:
        raise ValueError("question cannot be empty")

    if len(options) != 4:
        raise ValueError("options must contain exactly 4 items")

    if any(not option for option in options):
        raise ValueError("all options must be non empty strings")

    if correct_answer < 0 or correct_answer > 3:
        raise ValueError("correct_answer must be between 0 and 3")

    if not explanation:
        raise ValueError("explanation cannot be empty")

    return {
        "question": question,
        "options": options,
        "correct_answer": correct_answer,
        "explanation": explanation,
    }


async def generate_coding_question(language: str, difficulty: str) -> Question:
    language = (language or "Python").strip()
    difficulty = (difficulty or "easy").strip()

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
""".strip()

    try:
        response = await client.responses.create(
            model=MODEL_NAME,
            input=[
                {
                    "role": "system",
                    "content": "You are an expert programming instructor creating coding quiz questions. Return only valid JSON.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        raw_text = (response.output_text or "").strip()
        if not raw_text:
            raise ValueError("Model returned empty output_text")

        question_data = json.loads(clean_json(raw_text))
        question_data = _normalize_and_validate_question_data(question_data)

        return Question(
            id=str(uuid.uuid4()),
            question=question_data["question"],
            options=question_data["options"],
            correct_answer=question_data["correct_answer"],
            explanation=question_data["explanation"],
            difficulty=difficulty,
            language=language,
        )

    except (
        openai.APIError,
        json.JSONDecodeError,
        KeyError,
        TypeError,
        ValueError,
    ) as exc:
        logger.exception("Failed to generate coding question: %s", exc)
        return _fallback_question(language, difficulty)


async def generate_multiple_questions(
    language: str,
    difficulty: str,
    count: int = 3,
) -> List[Question]:
    if count <= 0:
        return []

    tasks = [
        generate_coding_question(language, difficulty)
        for _ in range(count)
    ]
    return await asyncio.gather(*tasks)
