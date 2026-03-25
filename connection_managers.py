from fastapi import WebSocket
import json

# CHANGED: also importing Question dataclass so we can type hint it below
from ai_integration import generate_multiple_questions, Question


# websocket plus nickname associated with that websocket
class Connection:
    def __init__(self, websocket: WebSocket, nickname: str):
        self.websocket = websocket
        self.nickname = nickname


# Handles all lobbies
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
        for connection in self.active_connections:
            await connection.websocket.send_text(message)

    async def start_game(self, message: str):
        q = await generate_multiple_questions("python", "hard", 10)
        game = GameManager(q)
        for connection in self.active_connections:
            await connection.websocket.send_text(message)
        return game

    def get_names(self):
        return ", ".join(conn.nickname for conn in self.active_connections)


class Game_Connection:
    def __init__(self, websocket: WebSocket, nickname: str):
        self.websocket = websocket
        self.nickname = nickname

        # CHANGED: renamed q_id -> q_index because questions are now a list
        self.q_index = 0
        self.score = 0


# Handles all Games
class GameManager:
    # CHANGED: typed questions as list[Question] instead of an untyped dict
    def __init__(self, questions: list[Question]):
        self.active_connections: list[Game_Connection] = []
        self.lobby = Lobby()
        self.questions = questions
        self.game_state = {
            "status": "in_progress",
            # CHANGED: was hardcoded to 10 — now derived from the actual list length
            "total_questions": len(questions),
            "players": [],
            "question": "",
            "answers": [],
        }

    async def connect(self, websocket: WebSocket, nickname: str):
        await websocket.accept()
        self.active_connections.append(Game_Connection(websocket, nickname))
        self.game_state["players"].append({"nickname": nickname, "score": 0})
        await self.broadcast_game_state()

    def disconnect(self, websocket: WebSocket):
        for i in self.active_connections:
            if i.websocket == websocket:
                self.active_connections.remove(i)

    # CHANGED: new helper method — safely fetches the current Question object for a
    # connection using q_index, returns None if the player has finished all questions
    def _get_question(self, connection: Game_Connection) -> Question | None:
        if connection.q_index < len(self.questions):
            return self.questions[connection.q_index]
        return None

    async def broadcast_game_state(self):
        for connection in self.active_connections:
            q = self._get_question(connection)

            # CHANGED: was self.questions[str(connection.q_id)]["code"] / ["choices"]
            if q is None:
                state = {**self.game_state, "status": "finished", "question": "", "answers": []}
            else:
                state = {
                    **self.game_state,
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

                # CHANGED: was self.questions[str(connection.q_id)]["answer"] == answer
                # now checks answer against q.options[q.correct_answer] from the Question dataclass
                if answer == q.options[q.correct_answer]:
                    # CHANGED: was connection.q_id += 1, now connection.q_index += 1
                    connection.q_index += 1
                    connection.score += 100
                else:
                    connection.score -= 20

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