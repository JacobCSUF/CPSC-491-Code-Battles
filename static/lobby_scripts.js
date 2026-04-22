let ws; //change


function connect(event) {
  const lobbyId = document.body.dataset.lobbyId;
  const nickname = document.body.dataset.nickname;

  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  const host = window.location.host;

  ws = new WebSocket(
    `${protocol}://${host}/lobby/${lobbyId}?nickname=${encodeURIComponent(nickname)}`,
  );


    ws.onopen = () => {
        console.log("Connected to room:", lobbyId);
        
  
    };

   ws.onmessage = (msg) => {
    
    const data = JSON.parse(msg.data);

    console.log("RAW DATA:", data); // 👈 add this
    switch (data.type) {
        case "start_game":
            window.location.href = `/game?lobby_id=${lobbyId}&nickname=${encodeURIComponent(nickname)}`;
            break;

        case "members":
           
            document.getElementById("playerCount").textContent = `Players (${data.members.length})`;
            document.getElementById("playersList").innerHTML = data.members.map(name =>
                name === nickname
                    ? `<li><strong>${name}</strong> <span class="tag">You</span></li>`
                    : `<li>${name}</li>`
            ).join("");
           
            break;

       case "lobby_settings":
    document.getElementById("language").value = data.language;

    // NEW: regenerate topics based on the new language
    updateTopicDropdown();

    document.getElementById("difficulty").value = data.difficulty;
    document.getElementById("topic").value = data.topic;
    break;
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




function startGame() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        document.getElementById("overlay").style.display = "flex";
        ws.send(JSON.stringify({type: "start", message: "Start Game"}));
    } else {
        console.error("WebSocket not open");
    }
}


function updateSettings() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: "lobby_settings",
            language: document.getElementById("language").value,
            difficulty: document.getElementById("difficulty").value,
            topic: document.getElementById("topic").value,
        }));
    }
}

const topicOptions = {
    Python: ["Lists", "Loops", "Dictionaries", "Functions", "Classes"],
    JavaScript: ["Arrays", "Events", "DOM", "Promises", "Functions"],
    Java: ["OOP", "Inheritance", "Loops", "Arrays", "Methods"],
    "C++": ["Pointers", "Vectors", "Loops", "Classes", "Memory"],

    CSharp: ["LINQ", "OOP", "Async/Await", "Collections", "Interfaces"],
    Ruby: ["Blocks", "Hashes", "Classes", "Modules", "Loops"],
    Go: ["Goroutines", "Channels", "Structs", "Interfaces", "Concurrency"],
    Rust: ["Ownership", "Borrowing", "Traits", "Enums", "Memory Safety"],
    PHP: ["Arrays", "Forms", "Sessions", "OOP", "Functions"],
    Swift: ["Optionals", "Structs", "Protocols", "Closures", "UI Basics"],
    Kotlin: ["Coroutines", "Null Safety", "Classes", "Collections", "Functions"],
    TypeScript: ["Types", "Interfaces", "Generics", "Modules", "Classes"],
    SQL: ["Select", "Joins", "Indexes", "Subqueries", "Aggregation"],
    R: ["Vectors", "Data Frames", "Plots", "Statistics", "Functions"],
    Bash: ["Variables", "Loops", "Pipes", "Permissions", "Scripting"]
};

function updateTopicDropdown() {
    const language = document.getElementById("language").value;
    const topicSelect = document.getElementById("topic");

    // Clear old topics
    topicSelect.innerHTML = "<option value=''>Select a topic</option>";

    // Add new topics
    if (topicOptions[language]) {
        topicOptions[language].forEach(topic => {
            const option = document.createElement("option");
            option.value = topic;
            option.textContent = topic;
            topicSelect.appendChild(option);
        });
    }
}
document.addEventListener("DOMContentLoaded", () => {
    updateTopicDropdown();
});
