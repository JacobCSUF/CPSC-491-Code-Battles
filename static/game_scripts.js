let ws;

function connect() {
    const lobbyId = document.body.dataset.lobbyId;
    const nickname = document.body.dataset.nickname;

    ws = new WebSocket(`ws://localhost:8000/game/${lobbyId}?nickname=${encodeURIComponent(nickname)}`);

    ws.onopen = () => console.log("Connected:", lobbyId);

    ws.onmessage = (msg) => {
        const state = JSON.parse(msg.data);
        
        //state.question -> exact question: What is 4 + 4
        //state.answer -> list of answers: ["124", "144", "132", "112"] 
        //state.players -> list of players and their score: {"nickname": nickname, "score": 0}
        //TODO add state.time -> a timer from the backend
        //...
        document.getElementById("question").textContent = state.question;

        const choices = state.answers;
        document.getElementById("choice1").textContent = choices[0];
        document.getElementById("choice2").textContent = choices[1];
        document.getElementById("choice3").textContent = choices[2];
        document.getElementById("choice4").textContent = choices[3];

        document.getElementById("choice1").onclick = () => ws.send(JSON.stringify({ type: "answer", answer: choices[0] }));
        document.getElementById("choice2").onclick = () => ws.send(JSON.stringify({ type: "answer", answer: choices[1] }));
        document.getElementById("choice3").onclick = () => ws.send(JSON.stringify({ type: "answer", answer: choices[2] }));
        document.getElementById("choice4").onclick = () => ws.send(JSON.stringify({ type: "answer", answer: choices[3] }));

        const playersList = document.getElementById("players");
        while (playersList.firstChild) {
            playersList.removeChild(playersList.firstChild);
        }
        state.players.forEach(player => {
            const li = document.createElement("li");
            li.textContent = `${player.nickname}: ${player.score}`;
            playersList.appendChild(li);
        });
    };

    ws.onclose = () => console.log("Disconnected:", lobbyId);
    ws.onerror = (err) => console.error("WebSocket error:", err);
}

window.addEventListener("load", connect);