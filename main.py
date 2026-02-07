from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import openai
import asyncio
import json
import uuid
from datetime import datetime
import os

app = FastAPI(title="Code Battles API")
templates = Jinja2Templates(directory="templates") 
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
openai.api_key = os.getenv("OPENAI_API_KEY")  # Set this environment variable


lobbies = []





#home page
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


#lobby page
@app.get("/lobby")
async def lobby(request: Request, lobby_id: str, nickname: str):
    print("User: "+ nickname +" joined room: "+ lobby_id)
    
    return templates.TemplateResponse("lobby.html", {"request": request,"lobby_id": lobby_id,"nickname": nickname})


#game page
@app.get("/game")
async def game(request: Request):
    return templates.TemplateResponse("game.html", {"request": request})





@app.websocket("/lobby/{lobby_id}")
async def websocket_endpoint(websocket: WebSocket, lobby_id: str):
   #TODO Check if that room exists and if not add it to "lobbies" variable
    #ADD username to that lobby
    #Signal over websockets the new user that joined
    print(lobby_id)
    await websocket.accept()





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
    




    

