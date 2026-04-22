let ws;
let timeLeft = 60;
let timerId;

function startTimer(timeLimit) {
  const timerElement = document.getElementById("Timer");
  timeLeft = timeLimit;
  timerElement.textContent = timeLeft;
  if (timerId != null) clearInterval(timerId);
  timerId = setInterval(function () {
    timeLeft -= 1;
    timerElement.textContent = timeLeft;
    if (timeLeft === 0) {
      clearInterval(timerId);
      timerElement.textContent = "Time's up.";
    }
  }, 1000);
}

function showGameOver(sortedPlayers) {
  clearInterval(timerId);
  const medals = ["🥇", "🥈", "🥉"];
  const lobbyId = document.body.dataset.lobbyId;
  const nickname = document.body.dataset.nickname;
  document.querySelector(".game-layout").innerHTML = `
    <div class="game-over-screen">
      <h2 class="game-over-title">Game Over!</h2>
      <ul class="scoreboard">
        ${sortedPlayers.map((p, i) => `
          <li class="scoreboard-entry ${i === 0 ? 'first-place' : ''}">
            <span class="medal">${medals[i] || i + 1}</span>
            <span class="player-name">${p.nickname}</span>
            <span class="player-score">${p.score} pts</span>
          </li>
        `).join("")}
      </ul>
      <button class="choice-btn" onclick="window.location.href='/lobby?lobby_id=${lobbyId}&nickname=${nickname}'">Back to Lobby</button>
    </div>
  `;
}

function updatePlayers(players) {
  const playersList = document.getElementById("players");
  playersList.innerHTML = "";
  players.forEach(player => {
    const li = document.createElement("li");
    li.innerHTML = `
      <span class="player-nickname">${player.nickname}</span>
      <span class="player-score-inline">${player.score}</span>
      ${player.waiting ? '<span class="waiting-badge">✓ Done</span>' : ''}
    `;
    playersList.appendChild(li);
  });
}

function connect() {
  const lobbyId = document.body.dataset.lobbyId;
  const nickname = document.body.dataset.nickname;
  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  const host = window.location.host;

  ws = new WebSocket(`${protocol}://${host}/game/${lobbyId}?nickname=${encodeURIComponent(nickname)}`);

  ws.onopen = () => console.log("Connected:", lobbyId);

  ws.onmessage = (msg) => {
    const state = JSON.parse(msg.data);

    if (state.status === "loading") {
      document.getElementById("question").textContent = "Loading questions...";
      return;
    }

    if (state.status === "waiting") {
      document.querySelectorAll(".choice-btn").forEach(btn => {
        btn.disabled = true;
        btn.classList.add("disabled");
      });
      document.getElementById("question").textContent = "Waiting for other players...";
      document.getElementById("question").removeAttribute("data-highlighted");
      updatePlayers(state.players);
      return;
    }

    if (state.status === "game_over") {
      showGameOver(state.sorted_players);
      return;
    }

    if (state.status === "in_progress") {
      document.querySelectorAll(".choice-btn").forEach(btn => {
        btn.disabled = false;
        btn.classList.remove("disabled");
      });

      const questionElement = document.getElementById("question");
      questionElement.textContent = state.question;
      questionElement.removeAttribute("data-highlighted");
      hljs.highlightElement(questionElement);

      if (state.new_question === true) startTimer(state.timer);

      document.querySelector(".question-title").textContent =
        `Question ${state.question_number} of ${state.total_questions}`;

      const choices = state.answers;
      for (let i = 0; i < 4; i++) {
        const btn = document.getElementById(`choice${i + 1}`);
        btn.textContent = choices[i];
        btn.onclick = () => ws.send(JSON.stringify({ type: "answer", answer: choices[i] }));
      }

      updatePlayers(state.players);
    }
  };

  ws.onclose = () => console.log("Disconnected:", lobbyId);
  ws.onerror = (err) => console.error("WebSocket error:", err);
}

window.addEventListener("load", connect);