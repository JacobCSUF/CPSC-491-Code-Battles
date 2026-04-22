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
    Python: ["Lists", "Loops", "Dictionaries", "Functions", "Classes", "String Methods", "Tuples", "Exception Handling", "File I/O", "Recursion"],
    JavaScript: ["Arrays", "Events", "DOM", "Promises", "Functions", "Callbacks", "Async/Await", "Error Handling", "String Methods", "Array Methods"],
    Java: ["OOP", "Inheritance", "Loops", "Arrays", "Methods", "Interfaces", "Exception Handling", "Collections", "String Methods", "Recursion"],
    "C++": ["Pointers", "Vectors", "Loops", "Classes", "Memory", "References", "Inheritance", "Arrays", "Exception Handling", "String Methods"],
    CSharp: ["LINQ", "OOP", "Async/Await", "Collections", "Interfaces", "Exception Handling", "Loops", "String Methods", "Generics", "Inheritance"],
    Ruby: ["Blocks", "Hashes", "Classes", "Modules", "Loops", "Iterators", "Exception Handling", "String Methods", "Arrays", "Symbols"],
    Go: ["Goroutines", "Channels", "Structs", "Interfaces", "Concurrency", "Pointers", "Error Handling", "Slices", "Maps", "Loops"],
    Rust: ["Ownership", "Borrowing", "Traits", "Enums", "Memory Safety", "Structs", "Pattern Matching", "Error Handling", "Closures", "Loops"],
    PHP: ["Arrays", "Forms", "Sessions", "OOP", "Functions", "String Methods", "Loops", "Exception Handling", "File I/O", "Regular Expressions"],
    Swift: ["Optionals", "Structs", "Protocols", "Closures", "UI Basics", "Enums", "Error Handling", "Loops", "Arrays", "String Methods"],
    Kotlin: ["Coroutines", "Null Safety", "Classes", "Collections", "Functions", "Loops", "Lambdas", "Exception Handling", "String Methods", "Data Classes"],
    TypeScript: ["Types", "Interfaces", "Generics", "Modules", "Classes", "Union Types", "Enums", "Type Guards", "Async/Await", "Array Methods"],
    SQL: ["Select", "Joins", "Indexes", "Subqueries", "Aggregation", "Group By", "Where Clauses", "Order By", "Insert & Update", "Transactions"],
    R: ["Vectors", "Data Frames", "Plots", "Statistics", "Functions", "Loops", "String Manipulation", "Apply Functions", "Lists", "Sorting"],
    Bash: ["Variables", "Loops", "Pipes", "Permissions", "Scripting", "Conditionals", "Functions", "Input & Output", "String Manipulation", "File Operations"]
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
