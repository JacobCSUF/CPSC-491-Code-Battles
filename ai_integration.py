import os
import json
import uuid
import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Dict, List

import openai
from openai import AsyncOpenAI


@dataclass
class Question:
    id: str
    question: str
    options: List[str]
    correct_answer: int
    explanation: str


logger = logging.getLogger(__name__)

MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-5.4-nano")

_client: AsyncOpenAI | None = None


def get_client() -> AsyncOpenAI | None:
    global _client
    if _client is not None:
        return _client
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY is not set — question generation will use fallback questions")
        return None
    _client = AsyncOpenAI(api_key=api_key, timeout=20.0)
    return _client


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


async def generate_multiple_questions(language: str, difficulty: str, topic: str, count: int = 10) -> list[Question]:
    language = (language or "Python").strip()
    difficulty = (difficulty or "easy").strip()

    client = get_client()
    if client is None:
        return [_fallback_question(language, difficulty) for _ in range(count)]

    prompt = f"""
        Generate {count} {difficulty} level coding questions for {language} and the topic is {topic}.

        Each question should include a code snippet where the user guesses the output.
        Provide exactly 4 multiple choice options with only one correct answer.
        No matter the difficulty use beginner friendly syntax so favor using newlines over bunching stuff in one line.
        For example return statements shouldn't include any calculations.
        ### EXAMPLE OF WHAT NEVER TO DO WITH RETURN STATEMENTS#########
        def custom_range(start, end):
            return [x for x in range(start, end)]
        #################################################
        Make sure the {count} questions have variety.

        Return ONLY valid JSON as a list in this exact format:
        [
        {{
            "question": "Your question here",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": 0,
            "explanation": "Brief explanation of why this is correct"
        }},
        ...
        ]
        """.strip()

    try:
        response = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert programming instructor creating coding quiz questions. Return only valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
        )

        raw_text = (response.choices[0].message.content or "").strip()
        if not raw_text:
            raise ValueError("Model returned empty content")

        parsed = json.loads(clean_json(raw_text))

        if not isinstance(parsed, list):
            raise ValueError("Expected a JSON array at the top level")

        questions: list[Question] = []
        for i, item in enumerate(parsed):
            try:
                question_data = _normalize_and_validate_question_data(item)
                questions.append(
                    Question(
                        id=str(uuid.uuid4()),
                        question=question_data["question"],
                        options=question_data["options"],
                        correct_answer=question_data["correct_answer"],
                        explanation=question_data["explanation"],
                    )
                )
            except (KeyError, TypeError, ValueError) as exc:
                logger.exception("Skipping invalid question at index %d: %s", i, exc)
                questions.append(_fallback_question(language, difficulty))

        if not questions:
            raise ValueError("No valid questions could be parsed from the model response")

        return questions

    except (openai.APIError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        logger.exception("Failed to generate multiple questions: %s", exc)
        return [_fallback_question(language, difficulty) for _ in range(count)]


if __name__ == "__main__":
    questions = asyncio.run(generate_multiple_questions("python", "easy", "general", 10))
    for i in questions:
        print(i)