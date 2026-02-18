from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware


import json
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



#game page
@app.get("/game")
async def game(request: Request):
    return templates.TemplateResponse("game.html", {"request": request})






#websocket plus nickname associated with that websocket
class Connection:
    def __init__(self, websocket: WebSocket, nickname: str):
        self.websocket = websocket
        self.nickname = nickname
        

#handles connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[Connection] = []

    async def connect(self, websocket: WebSocket, nickname: str):
        await websocket.accept()

        self.active_connections.append(Connection(websocket,nickname))

    def disconnect(self, websocket: WebSocket):
        for i in self.active_connections:
            if i.websocket == websocket:
                self.active_connections.remove(i)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.websocket.send_text(message)

    def get_names(self):
         return ", ".join(conn.nickname for conn in self.active_connections)



#each websocket will have its own Connection Manager
lobbies = {}


import asyncio
@app.websocket("/lobby/{lobby_id}")
async def websocket_endpoint(websocket: WebSocket, lobby_id):
    nickname = websocket.query_params.get("nickname")
    #ADD username to that lobby 
    #Signal over websockets the new user that joined

    if lobby_id not in lobbies:
        lobbies[lobby_id] = ConnectionManager()
        
    
    manager = lobbies[lobby_id]

    await manager.connect(websocket,nickname)

     # Broadcast join
    members = manager.get_names()
    await manager.broadcast(f"{members} | {nickname} joined")

    try:
        while True:
            # Wait for any message (optional)
            data = await websocket.receive_text()
          

    except WebSocketDisconnect:
        # Remove user and broadcast leave
        manager.disconnect(websocket)
        members = manager.get_names()
        await manager.broadcast(f"{members} | {nickname} left")