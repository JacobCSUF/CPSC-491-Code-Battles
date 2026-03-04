from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

#newfile with connection managers
from connection_managers import LobbyManager, GameManager


from typing import Dict

app = FastAPI(title="Code Battles API")
templates = Jinja2Templates(directory="templates") 
app.mount("/static", StaticFiles(directory="static"), name="static")



@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

#lobby page
@app.get("/lobby")
async def lobby(request: Request, lobby_id: str, nickname: str):
    print("User: "+ nickname +" joined room: "+ lobby_id)
    
    return templates.TemplateResponse("lobby.html", {"request": request,"lobby_id": lobby_id,"nickname": nickname})


#lobby page
@app.get("/game")
async def game(request: Request, lobby_id: str, nickname: str):
    print("User: "+ nickname +" joined game: "+ lobby_id)
    
    return templates.TemplateResponse("game.html", {"request": request,"lobby_id": lobby_id,"nickname": nickname})





lobbies = {}      
games = {}

import asyncio
@app.websocket("/lobby/{lobby_id}")
async def websocket_lobby_endpoint(websocket: WebSocket, lobby_id):
    nickname = websocket.query_params.get("nickname")
    #ADD username to that lobby 
    #Signal over websockets the new user that joined

    if lobby_id not in lobbies:
        lobbies[lobby_id] = LobbyManager()
        
    
    manager = lobbies[lobby_id]
    
    await manager.connect(websocket,nickname)
    
     # Broadcast join
    members = manager.get_names()
    await manager.broadcast(f"{members} | {nickname} joined")
    
    try:
        while True:
            
            # Wait for any message (optional)
            data = await websocket.receive_text()
            
           
            #if the message is start game, broadcast to all members of lobby that the game is starting
            #in javascript this will trigger the game page to open
            #TODO destroy the lobby key in the dictonary
            if data == "start_game":
                await  manager.broadcast("start_game")


            #TODO
            #elif data == "lobby":
                #manager.change_lobby()

    except WebSocketDisconnect:
        # Remove user and broadcast leave
        manager.disconnect(websocket)
        members = manager.get_names()
        await manager.broadcast(f"{members} | {nickname} left")




@app.websocket("/game/{lobby_id}")
async def websocket_game_endpoint(websocket: WebSocket, lobby_id):
    nickname = websocket.query_params.get("nickname")
    if lobby_id not in games:
        games[lobby_id] = GameManager()  
    
    manager = games[lobby_id]
    await manager.connect(websocket,nickname)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data["type"] == "answer":
                await manager.sent_answer(websocket, data["answer"])

    except WebSocketDisconnect:
        manager.disconnect(websocket)



