from fastapi import WebSocket
import json

#websocket plus nickname associated with that websocket
class Connection:
    def __init__(self, websocket: WebSocket, nickname: str):
        self.websocket = websocket
        self.nickname = nickname
        

#Handles all lobbies
class LobbyManager:
    def __init__(self):
        self.active_connections: list[Connection] = []
        self.lobby = Lobby()

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





class Game_Connection:
    def __init__(self, websocket: WebSocket, nickname: str):
        self.websocket = websocket
        self.nickname = nickname
        self.q_id = 1
        self.score = 0




#Handles all Games
class GameManager:
    def __init__(self):
        self.active_connections: list[Game_Connection] = []
        self.lobby = Lobby()
        self.game_state = {
            "status": "in_progress",
            "total_questions": 10,
            "players": [],  # start empty, add as they connect
            "question": "",
            "answers": "",
            "timer": 60
        }
        self.questions = questions  

    async def connect(self, websocket: WebSocket, nickname: str):
        await websocket.accept()
        self.active_connections.append(Game_Connection(websocket,nickname))
        #TODO change to
        self.game_state["players"].append({"nickname": nickname, "score": 0})
        await self.broadcast_game_state()

    def disconnect(self, websocket: WebSocket):
        for i in self.active_connections:
            if i.websocket == websocket:
                self.active_connections.remove(i)

    async def broadcast_game_state(self):
        for connection in self.active_connections:
            self.game_state["question"] = self.questions[connection.q_id]["code"]
            self.game_state["answers"] = self.questions[connection.q_id]["choices"]
            print(self.game_state)
            await connection.websocket.send_text(json.dumps(self.game_state))


    async def sent_answer(self, websocket: WebSocket, answer):
        for connection in self.active_connections:
            if connection.websocket == websocket:
                if self.questions[connection.q_id]["answer"] == answer:
                    connection.q_id += 1
                    connection.score += 100
                else:
                    connection.score -= 20

                # sync score to game_state
                for player in self.game_state["players"]:
                    if player["nickname"] == connection.nickname:
                        player["score"] = connection.score

                await self.broadcast_game_state()


    def get_names(self):
         return ", ".join(conn.nickname for conn in self.active_connections)




class Lobby:
     def __init__(self):
        self.language = "python"
        self.difficulty = "easy"
        self.topic = "if statements"




#will be from ai and random later
questions = {
    1:  {"code": "What is 12 x 12?",
         "choices": ["124", "144", "132", "112"],
         "answer": "144"},
    2:  {"code": "What planet is closest to the sun?",
         "choices": ["Venus", "Earth", "Mars", "Mercury"],
         "answer": "Mercury"},
    3:  {"code": "What is the square root of 144?",
         "choices": ["14", "11", "12", "13"],
         "answer": "12"},
    4:  {"code": "How many sides does a hexagon have?",
         "choices": ["5", "7", "8", "6"],
         "answer": "6"},
    5:  {"code": "What is the chemical symbol for water?",
         "choices": ["WO", "H2O", "HO2", "OW"],
         "answer": "H2O"},
    6:  {"code": "What is 15% of 200?",
         "choices": ["25", "35", "20", "30"],
         "answer": "30"},
    7:  {"code": "How many bones are in the human body?",
         "choices": ["195", "206", "215", "198"],
         "answer": "206"},
    8:  {"code": "What is the speed of light in km/s?",
         "choices": ["200,000", "250,000", "300,000", "350,000"],
         "answer": "300,000"},
    9:  {"code": "What is 7 squared?",
         "choices": ["42", "49", "56", "14"],
         "answer": "49"},
    10: {"code": "What gas do plants absorb from the air?",
         "choices": ["Oxygen", "Nitrogen", "Carbon Dioxide", "Hydrogen"],
         "answer": "Carbon Dioxide"},
}