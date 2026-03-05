from pydantic import BaseModel
from typing import Dict, List, Optional
from openai import AsyncOpenAI
import asyncio
import json
import uuid
from datetime import datetime
import os


client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def clean_json(text: str) -> str:
    t = text.strip()

    # Remove markdown code fences if present
    if t.startswith("```"):
        parts = t.split("```")
        if len(parts) >= 2:
            t = parts[1]

        # remove the word json if present
        if t.startswith("json"):
            t = t.replace("json", "", 1).strip()

    return t


# ChatGPT Integration
async def generate_coding_question(language: str, difficulty: str) -> Question:
    """Generate a coding question using ChatGPT"""
    prompt = f"""
    Generate a {difficulty} level coding question for {language}.
    
    The question should test logical thinking and programming concepts.
    Provide exactly 4 multiple choice options with only one correct answer.
    
    Return the response in this exact JSON format:
    {{
        "question": "Your question here",
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "correct_answer": 0,
        "explanation": "Brief explanation of why this is correct"
    }}
    
    Make sure the question is clear, concise, and appropriate for a timed coding battle.
    Focus on concepts like algorithms, data structures, syntax, or logical reasoning.
    """
    
    try:
        response = await client.responses.create(
    model="gpt-4o-mini",
    input=[
        {"role": "system", "content": "You are an expert programming instructor creating coding quiz questions."},
        {"role": "user", "content": prompt}
    ]
)

content = response.output_text
        question_data = json.loads(clean_json(content))
        
        return Question(
            id=str(uuid.uuid4()),
            question=question_data["question"],
            options=question_data["options"],
            correct_answer=question_data["correct_answer"],
            explanation=question_data["explanation"],
            difficulty=difficulty,
            language=language
        )
    except Exception as e:
        # Fallback question if ChatGPT fails
        return Question(
            id=str(uuid.uuid4()),
            question=f"What is a common data structure used to implement a stack in {language}?",
            options=["Array/List", "Hash Table", "Binary Tree", "Graph"],
            correct_answer=0,
            explanation="Arrays or Lists are commonly used to implement stacks with push/pop operations.",
            difficulty=difficulty,
            language=language
        )
    




    


