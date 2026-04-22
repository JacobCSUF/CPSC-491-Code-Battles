from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import asyncio
#newfile with connection managers
from connection_managers import LobbyManager, GameManager
import json

from typing import Dict

app = FastAPI(title="Code Battles API")
templates = Jinja2Templates(directory="templates") 
app.mount("/static", StaticFiles(directory="static"), name="static")



@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(request, "home.html")

@app.get("/lobby")
async def lobby(request: Request, lobby_id: str, nickname: str):
    return templates.TemplateResponse(request, "lobby.html", {"lobby_id": lobby_id, "nickname": nickname})

@app.get("/game")
async def game(request: Request, lobby_id: str, nickname: str):
    return templates.TemplateResponse(request, "game.html", {"lobby_id": lobby_id, "nickname": nickname})





lobbies = {}      
games = {}


@app.websocket("/lobby/{lobby_id}")
async def websocket_lobby_endpoint(websocket: WebSocket, lobby_id):
    nickname = websocket.query_params.get("nickname")

    if lobby_id not in lobbies:
        lobbies[lobby_id] = LobbyManager()
        
    manager = lobbies[lobby_id]
    await manager.connect(websocket, nickname)
    
    # Broadcast join
    await manager.broadcast(json.dumps({
        "type": "members",
        "members": manager.get_names(),
        "last_action": f"{nickname} joined"
    }))
    
    try:
        while True:
            raw = await websocket.receive_text()
            if not raw.strip():
                continue

            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                print("Bad message:", raw)
                continue

            msg_type = data.get("type")

            if msg_type == "start":
                games[lobby_id] = await manager.start_game()

            elif msg_type == "lobby_settings":
                await manager.change_lobby({
                    "language": data["language"],
                    "difficulty": data["difficulty"],
                    "topic": data["topic"]
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(json.dumps({
            "type": "members",
            "members": manager.get_names(),
            "last_action": f"{nickname} left"
        }))



@app.websocket("/game/{lobby_id}")
async def websocket_game_endpoint(websocket: WebSocket, lobby_id):
    nickname = websocket.query_params.get("nickname")
   
    
    manager = games[lobby_id]
    await manager.connect(websocket,nickname)
    
    try:
        while True:
            data = await websocket.receive_json()

            msg_type = data.get("type")

            if msg_type == "answer":
                answer = data.get("answer")
                if answer is not None:
                    await manager.sent_answer(websocket, answer)

            else:
                print("Unknown message type:", data)

    except WebSocketDisconnect as e:
        print("Disconnected:", e.code)
        await manager.disconnect(websocket)

    except WebSocketDisconnect as e:
        print("Disconnected:", e.code)
        manager.disconnect(websocket)
        if not manager.active_connections:  # last player left
            games.pop(lobby_id, None)

