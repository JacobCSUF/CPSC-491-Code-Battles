from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()
templates = Jinja2Templates(directory="templates") 
app.mount("/static", StaticFiles(directory="static"), name="static")


lobbies = []


#home page
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


#lobby page
@app.get("/lobby")
async def lobby(request: Request, lobby_id: str, nickname: str):
    print("User: "+ nickname +" joined room: "+ lobby_id)
    #TODO Check if that room exists and if not add it to "lobbies" variable
    #ADD username to that lobby
    #Signal over websockets the new user that joined
    return templates.TemplateResponse("lobby.html", {"request": request,"lobby_id": lobby_id,"nickname": nickname})


#game page
@app.get("/game")
async def game(request: Request):
    return templates.TemplateResponse("game.html", {"request": request})





@app.websocket("/lobby/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
   #TODO ADD a bunch of stuff
    print(room_id)
    await websocket.accept()
    