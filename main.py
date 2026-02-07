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

    
