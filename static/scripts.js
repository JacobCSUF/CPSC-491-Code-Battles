function connect(event) {
   
    const lobbyId = document.body.dataset.lobbyId;
    const nickname = document.body.dataset.nickname;

   
    const ws = new WebSocket(`ws://localhost:8000/lobby/${lobbyId}`); // connect to dynamic room

    ws.onopen = () => {
        console.log("Connected to room:", lobbyId);
        ws.send("Hello from client!"); // optional: send a message right away
    };

    ws.onmessage = (msg) => {
        console.log("Message from server:", msg.data);
    };

    ws.onclose = () => {
        console.log("Disconnected from room:", lobbyId);
    };

    ws.onerror = (err) => {
        console.error("WebSocket error:", lobbyId);
    };
}
window.addEventListener("load", connect);