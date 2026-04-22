from fastapi import WebSocket
import json
from datetime import datetime  # MERGED: needed for timer

from ai_integration import retry_loop, Question


class Connection:
    def __init__(self, websocket: WebSocket, nickname: str):
        self.websocket = websocket
        self.nickname = nickname

class Lobby:
    def __init__(self):
        self.language = "python"
        self.difficulty = "easy"
        self.topic = "if statements"

class LobbyManager:
    def __init__(self):
        self.active_connections: list[Connection] = []
        self.lobby = Lobby()

    async def connect(self, websocket: WebSocket, nickname: str):
        await websocket.accept()
        self.active_connections.append(Connection(websocket, nickname))

    def disconnect(self, websocket: WebSocket):
        for i in self.active_connections:
            if i.websocket == websocket:
                self.active_connections.remove(i)

    async def broadcast(self, message: str):
        dead = []
        for connection in self.active_connections:
            try:
                await connection.websocket.send_text(message)
            except Exception:
                dead.append(connection)
        for connection in dead:
            self.active_connections.remove(connection)

    async def start_game(self):
        q = await retry_loop(self.lobby.language, self.lobby.difficulty, self.lobby.topic,10)
        game = GameManager(q,self.lobby)
        
        await self.broadcast(json.dumps({
            "type": "start_game",
            }))
    
        return game

    def get_names(self):
        return [conn.nickname for conn in self.active_connections]

    async def change_lobby(self, lobby_):
        lan = lobby_["language"]
        diff = lobby_["difficulty"]
        top = lobby_["topic"]
        self.lobby.language = lan
        self.lobby.difficulty = diff
        self.lobby.topic = top
        for connection in self.active_connections:
            await connection.websocket.send_text(
                json.dumps({"type": "lobby_settings", "language": lan, "difficulty": diff, "topic": top})
        )

class Game_Connection:
    def __init__(self, websocket: WebSocket, nickname: str):
        self.websocket = websocket
        self.nickname = nickname
        self.q_index = 0
        self.score = 0
        self.answered = False                   # MERGED: timer
        self.question_start_time = None         # MERGED: timer


class GameManager:
    def __init__(self, questions: list[Question],lobby):
        self.active_connections: list[Game_Connection] = []
        self.lobby = lobby
        self.questions = questions
        self.game_state = {
            "status": "in_progress",
            "total_questions": len(questions),
            "players": [],
            "question": "",
            "answers": [],
            "timer": 60,                        # MERGED: timer
        }

    async def connect(self, websocket: WebSocket, nickname: str):
        await websocket.accept()
        self.active_connections.append(Game_Connection(websocket, nickname))
        self.game_state["players"].append({"nickname": nickname, "score": 0})
        await self.broadcast_game_state(True)   # MERGED: timer

    def disconnect(self, websocket: WebSocket):
        for i in self.active_connections:
            if i.websocket == websocket:
                self.active_connections.remove(i)

    def _get_question(self, connection: Game_Connection) -> Question | None:
        if connection.q_index < len(self.questions):
            return self.questions[connection.q_index]
        return None

  
    def _all_finished(self):
        return all(conn.q_index >= len(self.questions) for conn in self.active_connections)

    async def broadcast_game_state(self, new_question, answered_websocket=None):
        all_done = self._all_finished()

        for connection in self.active_connections:
            q = self._get_question(connection)

            if connection.websocket == answered_websocket:
                self.game_state["new_question"] = True
                connection.question_start_time = datetime.now()
            else:
                self.game_state["new_question"] = new_question
                if new_question:
                    connection.question_start_time = datetime.now()

            if all_done:
                # Everyone finished — send game_over with winner to everyone
                sorted_players = sorted(self.game_state["players"], key=lambda p: p["score"], reverse=True)
                winner = sorted_players[0]["nickname"]
                state = {
                    **self.game_state,
                    "status": "game_over",
                    "question": "",
                    "answers": [],
                    "sorted_players": sorted_players,
                    "winner": winner,
                }
            elif q is None:
                # This player is done but others aren't
                state = {
                    **self.game_state,
                    "status": "waiting",
                    "question": "",
                    "answers": [],
                }
            else:
                state = {
                    **self.game_state,
                    "status": "in_progress",
                    "question": q.question,
                    "answers": q.options,
                }

            print(state)
            await connection.websocket.send_text(json.dumps(state))

    async def sent_answer(self, websocket: WebSocket, answer: str):
        for connection in self.active_connections:
            if connection.websocket == websocket:
                q = self._get_question(connection)

                if q is None:
                    return

                if answer == q.options[q.correct_answer]:
                    connection.q_index += 1
                    time_taken = (datetime.now() - connection.question_start_time).seconds
                    score = round(100 * (1 - (time_taken / 60)))
                    connection.score += score
                    answered_ws = connection.websocket  
                else:
                    connection.score -= 20
                    answered_ws = None  

                for player in self.game_state["players"]:
                    if player["nickname"] == connection.nickname:
                        player["score"] = connection.score

                await self.broadcast_game_state(False, answered_ws)

    def get_names(self):
        return ", ".join(conn.nickname for conn in self.active_connections)