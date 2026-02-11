from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from models import Player, Lobby, Question
from ai_service import generate_coding_question, generate_multiple_questions

import json
from typing import Dict

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

lobbies: Dict[str, Lobby] = {} # Dict, ask team for confirmation
                               # dict with typing incorperated, more clarity
print(type(lobbies))
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
   
    #ADD username to that lobby 
    #Signal over websockets the new user that joined

    await websocket.accept() #websocket connection

    data = await websocket.receive_text() # keep waiting until they send message,
                                          # message contains username 
                                          # else throw exception ?

    message = json.loads(data) # Format: {"username": "Kevin"..etc}
    username = message.get("username")
    
    print(f"{username} is joining {lobby_id}") # ?
    
    #TODO Check if that room exists and if not add it to "lobbies" variable DONE
    if lobby_id not in lobbies:
        print(f"Creating new lobby: {lobby_id}")
        lobbies[lobby_id] = Lobby(id=lobby_id, players=[])

    # delete debug
    print(f"lobbies in session: {lobbies}")
