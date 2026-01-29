function sendMessage(event) {
    event.preventDefault(); // prevent page reload
    
    const room = document.getElementById("roomInput").value; // get room name
    const ws = new WebSocket(`ws://localhost:8000/lobby/${room}`); // connect to dynamic room

    ws.onopen = () => {
        console.log("Connected to room:", room);
        ws.send("Hello from client!"); // optional: send a message right away
    };

    ws.onmessage = (msg) => {
        console.log("Message from server:", msg.data);
    };

    ws.onclose = () => {
        console.log("Disconnected from room:", room);
    };

    ws.onerror = (err) => {
        console.error("WebSocket error:", err);
    };
}
