let ws;
let timeLeft = 60;
let timerId;

function startTimer(timeLimit) {
  timerElement = document.getElementById("Timer");
  timeLeft = timeLimit;
  timerElement.textContent = timeLeft;
  if (timerId != null) {
    clearInterval(timerId);
  }
  timerId = setInterval(function () {
    timeLeft = timeLeft - 1;
    timerElement.textContent = timeLeft;
    if (timeLeft == 0) {
      clearInterval(timerId);
      timerElement.textContent = "Time's up.";
    }
  }, 1000);
}

function connect() {
    const lobbyId = document.body.dataset.lobbyId;
    const nickname = document.body.dataset.nickname;

    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const host = window.location.host;

    ws = new WebSocket(
        `${protocol}://${host}/game/${lobbyId}?nickname=${encodeURIComponent(nickname)}`,
    );

    ws.onopen = () => console.log("Connected:", lobbyId);

    ws.onmessage = (msg) => {
        const state = JSON.parse(msg.data);

        if (state.status === "loading") {
            document.getElementById("question").textContent = "Loading questions...";
            return;
        }

        if (state.status === "waiting") {
            //TODO - handle player waiting for others to finish questions
            return;
        }

        if (state.status === "game_over") {
            //TODO - handle game finished (All players answered questions)
            return;
        }

        if (state.status === "in_progress") {
            document.getElementById("question").textContent = state.question;

            if (state.new_question === true) startTimer(state.timer);

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
        }
    };

    ws.onclose = () => console.log("Disconnected:", lobbyId);
    ws.onerror = (err) => console.error("WebSocket error:", err);
}

window.addEventListener("load", connect);