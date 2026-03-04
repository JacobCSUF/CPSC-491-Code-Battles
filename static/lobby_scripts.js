
let ws; //change

function connect(event) {

    const lobbyId = document.body.dataset.lobbyId;
    const nickname = document.body.dataset.nickname;


    ws = new WebSocket(`ws://localhost:8000/lobby/${lobbyId}?nickname=${encodeURIComponent(nickname)}`); //change

    ws.onopen = () => {
        console.log("Connected to room:", lobbyId);
        ws.send("I joined the room!"); // optional: send a message right away
    };

    ws.onmessage = (msg) => {
    if (msg.data == "start_game") {
        window.location.href = `/game?lobby_id=${lobbyId}&nickname=${encodeURIComponent(nickname)}`;
    } else {
        const [membersText, lastAction] = msg.data.split("|");
        const members = membersText.trim().split(",").map(m => m.trim()).filter(Boolean);

        
        document.getElementById("playerCount").textContent = `Players (${members.length})`;

        
        document.getElementById("playersList").innerHTML = members.map(name =>
            name === nickname
                ? `<li><strong>${name}</strong> <span class="tag">You</span></li>`
                : `<li>${name}</li>`
        ).join("");

        document.getElementById("last-action").textContent = lastAction ? lastAction.trim() : "";
    }
};

    ws.onclose = () => {
        console.log("Disconnected from room:", lobbyId);
    };

    ws.onerror = (err) => {
        console.error("WebSocket error:", lobbyId);
    };
}
window.addEventListener("load", connect);





//change
function startGame() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send("start_game"); // send start_game message
        console.log("Start game sent!");
    } else {
        console.error("WebSocket not open");
    }
}