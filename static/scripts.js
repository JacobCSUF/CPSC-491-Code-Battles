
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
            const lobbyId = document.body.dataset.lobbyId;
            const nickname = document.body.dataset.nickname;

            // redirect to game page
            window.location.href = `/game?lobby_id=${lobbyId}&nickname=${encodeURIComponent(nickname)}`;
        }

        else {
            const [membersText, lastAction] = msg.data.split("|"); // server sends "Alice, Bob | Bob joined"

            document.getElementById("members").textContent = membersText.trim();
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