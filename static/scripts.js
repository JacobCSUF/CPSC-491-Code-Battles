function connect(event) {
   
    const lobbyId = document.body.dataset.lobbyId;
    const nickname = document.body.dataset.nickname;

    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const host = window.location.host;
    const ws = new WebSocket(`${protocol}://${host}/lobby/${lobbyId}?nickname=${encodeURIComponent(nickname)}`);

    ws.onopen = () => {
        console.log("Connected to room:", lobbyId);
        ws.send("I joined the room!"); // optional: send a message right away
    };

     ws.onmessage = (msg) => {
    const [membersText, lastAction] = msg.data.split("|"); // server sends "Alice, Bob | Bob joined"
    
    document.getElementById("members").textContent = membersText.trim();
    document.getElementById("last-action").textContent = lastAction ? lastAction.trim() : "";
};

    ws.onclose = () => {
        console.log("Disconnected from room:", lobbyId);
    };

    ws.onerror = (err) => {
        console.error("WebSocket error:", lobbyId);
    };
}
window.addEventListener("load", connect);