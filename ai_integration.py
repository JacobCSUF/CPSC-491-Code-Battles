from pydantic import BaseModel
from typing import Dict, List, Optional
import openai
import asyncio
import json
import uuid
from datetime import datetime
import os


openai.api_key = os.getenv("OPENAI_API_KEY")  # Set this environment variable



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
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert programming instructor creating coding quiz questions."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        question_data = json.loads(content)
        
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
    




    

