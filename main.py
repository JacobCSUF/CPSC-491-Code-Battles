from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import asyncio
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
            
           
           
            #AI11 CHANGED TO CALL START GAME
            if data == "start_game":
               games[lobby_id] = await manager.start_game("start_game")
                 

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

    except Exception as e:
        print("Unexpected error:", e)
        await manager.disconnect(websocket)


