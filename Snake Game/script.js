// === firebase config & firestore setup ===
const firebaseConfig = {
    apiKey: "AIzaSyDwd1M8TV8pxMUgKM1e_Bp-G4e7p_l-hYg",
    authDomain: "snake-game-c0cb7.firebaseapp.com",
    projectId: "snake-game-c0cb7",
    storageBucket: "snake-game-c0cb7.firebasestorage.app",
    messagingSenderId: "1061710098302",
    appId: "1:1061710098302:web:c6b37d6bc696c961304d2f",
    measurementId: "G-S5D766TGDV"
};

try {
    firebase.initializeApp(firebaseConfig);
    const db = firebase.firestore();
    db.enablePersistence()
        .catch((err) => {
            console.log("Persistance failed: ", err);
        });
} catch (err) {
    console.log("Firebase initialisation error: " , err);
}

// === canvas setup ===
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
canvas.width = 800;
canvas.height = 480;

// === game elements ===
const scoreDisplay = document.getElementById("score");
const timerDisplay = document.getElementById("timeValue");
const progressCircle = document.getElementById("progress");
let popup = document.getElementById("gameOverPopup");

let snake = [], food = {}, specialItems = [];
let box = 20;
let direction = "RIGHT";
let moveQueue = [];
let score = 0;
let gameInterval, timerInterval;
let timeLeft = 30;
let controlType = "arrow";
let playerName = "";
let gameStarted = false;
let gameSpeed = 100;

// === control selection ===
document.getElementById("controlSelect").addEventListener("change", (e) => {
    controlType = e.target.value;
});

// === mode selection ===
document.getElementById("modeSelect").addEventListener("change", (e) => {
    switch(e.target.value) {
        case "easy": gameSpeed = 150; break;
        case "medium": gameSpeed = 100; break;
        case "hard": gameSpeed = 70; break;
    }
});

// === pre game instructions ===
function drawPreGameInstructions() {
    ctx.fillStyle = "rgba(0, 0, 0, 0.7)";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = "#fff";
    ctx.font = "30px Verdana";
    ctx.textAlign = "center";

    //animated floating effect
    const floatOffset = Math.sin(Date.now() / 500) * 10;

    ctx.fillText("Welcome to Slither Snake Game 🐍", canvas.width/2, canvas.height/2 - 50 + floatOffset);
    ctx.font = "20px Arial";
    ctx.fillText("Choose controls and mode, enter your name", canvas.width/2, canvas.height/2 + floatOffset);
    ctx.fillText("Click START GAME to begin!", canvas.width/2, canvas.height/2 + 30 + floatOffset);

    //draw small animated snake
    const snakeX = canvas.width/2 - 100 + Math.sin(Date.now() / 300) * 50;
    const snakeY = canvas.height/2 + 80 + floatOffset;
    for (let i = 0; i < 5; i++) {
        ctx.fillStyle = `hsl(${(Date.now()/50 + i*30) % 360}, 100%, 50%)`;
        ctx.fillRect(snakeX + i*20, snakeY, 15, 15);
    }
}

// === start game ===
function startGame() {
    playerName = document.getElementById("username").value.trim() || "Player";
    snake = [{ x: 5 * box, y: 5 * box }];
    direction = "RIGHT";
    moveQueue = [];
    score = 0;
    timeLeft = 30;
    scoreDisplay.textContent = score;
    timerDisplay.textContent = timeLeft;
    document.getElementById("levelDisplay").textContent = "Level 1";
    popup.classList.add("hidden");
    clearInterval(gameInterval);
    clearInterval(timerInterval);
    spawnFood();
    specialItems = [];
    gameStarted = true;
    gameInterval = setInterval(draw, gameSpeed);
    timerInterval = setInterval(updateTimer, 1000);
}

// === timer update ===
function updateTimer() {
    if (timeLeft > 0) {
        timeLeft--;
        timerDisplay.textContent = timeLeft;
        let offset = 176 - (timeLeft / 30) * 176;
        progressCircle.style.strokeDashoffset = offset;
    } else {
        gameOver();
    }
}

// === spawn regular food ===
function spawnFood() {
    food = {
        x: Math.floor(Math.random() * (canvas.width / box)) * box,
        y: Math.floor(Math.random() * (canvas.height / box)) * box,
    };
}
 
// === spawn special items ===
function spawnSpecialItem() {
    specialItems.push({
        x: Math.floor(Math.random() * (canvas.width / box)) * box,
        y: Math.floor(Math.random() * (canvas.height / box)) * box,
        type: Math.random() > 0.5 ? "score" : "time"
    });
}

// === draw loop ===
function draw() {
    if (!gameStarted) {
        drawPreGameInstructions();
        return;
    }

    ctx.fillStyle = "#222";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    //snake
    ctx.fillStyle = "lime";
    for (let part of snake) {
        ctx.fillRect(part.x, part.y, box, box);
    }

    //food
    ctx.fillStyle = "red";
    ctx.fillRect(food.x, food.y, box, box);

    //special items
    for (let item of specialItems) {
        ctx.fillStyle = item.type === "score" ? "gold" : "cyan";
        ctx.beginPath();
        ctx.arc(item.x + box / 2, item.y + box / 2, box / 2, 0, 2 * Math.PI);
        ctx.fill();
    }
    
    //move snake
    let head = { ...snake[0] };

    //mouse controls
    if (controlType === "cursor") {
        canvas.onmousemove = (e) => {
            const rect = canvas.getBoundingClientRect();
            const mx = e.clientX - rect.left;
            const my = e.clientY - rect.top;
            if (Math.abs(mx - head.x) > Math.abs(my - head.y)) {
                direction = mx > head.x ? "RIGHT" : "LEFT";
            } else {
                direction = my > head.y ? "DOWN" : "UP";
            }
        };
    }

    //queue movement
    if (moveQueue.length) {
        const newDir = moveQueue.shift();
        if (
            (direction === "LEFT" && newDir !== "RIGHT") ||
            (direction === "RIGHT" && newDir !== "LEFT") ||
            (direction === "UP" && newDir !== "DOWN") ||
            (direction === "DOWN" && newDir !== "UP")
        ) {
            direction = newDir;
        }
    }

    //move head with wall wrapping
    if (direction === "LEFT") head.x -= box;
    if (direction === "RIGHT") head.x += box;
    if (direction === "UP") head.y -= box;
    if (direction === "DOWN") head.y += box;

    //wall wrapping
    if (head.x < 0) head.x = canvas.width - box;
    if (head.x >= canvas.width) head.x = 0;
    if (head.y < 0) head.y = canvas.height - box;
    if (head.y >= canvas.height) head.y = 0;

    //self collision
    for (let part of snake) {
        if (head.x === part.x && head.y === part.y) {
          return gameOver();
        }
    }

    //add new head
    snake.unshift(head);

    //check food collision
    if (head.x === food.x && head.y === food.y) {
        score += 10;
        scoreDisplay.textContent = score;
        spawnFood();
        if (Math.random() < 0.3) spawnSpecialItem();
    } else {
        snake.pop();
    }

    //collect special items
    for (let i = 0; i < specialItems.length; i++) {
        const item = specialItems[i];
        if (head.x === item.x && head.y === item.y) {
            if (item.type === "score") score += 20;
            else if (item.type === "time") timeLeft = Math.min(30, timeLeft + 5);
            specialItems.splice(i, 1);
            break;
        }
    }
    scoreDisplay.textContent = score;
}

// === game over ===
function gameOver() {
    clearInterval(gameInterval);
    clearInterval(timerInterval);
    document.getElementById("finalScore").textContent = score;
    popup.classList.remove("hidden");
    saveScoreToFirebase(playerName, score);
    fetchLeaderboard();
    gameStarted = false;
}

// === save score to firestore ===
function saveScoreToFirebase(name, score) {
    db.collection("scores").add({
        name,
        score,
        timestamp: firebase.firestore.FieldValue.serverTimestamp()
    }).catch((error) => {
        console.error("Error adding document: ", error);
    });
}

// === fetch and display leaderboard ===
function fetchLeaderboard() {
    const list = document.getElementById("leaderboardList");
    list.innerHTML = "";
    db.collection("scores")
        .orderBy("score", "desc")
        .limit(10)
        .get()
        .then((snapshot) => {
            snapshot.forEach((doc) => {
                const data = doc.data();
                const li = document.createElement("li");
                li.textContent = `${data.name}: ${data.score}`;
                list.appendChild(li);
            });
        })
        .catch((error) => {
            console.log("Error getting leaderboard: ", error);
        });
}

  
// === keyboard controls ===
document.addEventListener("keydown", (e) => {
    if (controlType === "arrow" || controlType === "wasd") {
        const map = {
            ArrowLeft: "LEFT", ArrowUp: "UP", ArrowRight: "RIGHT", ArrowDown: "DOWN",
            a: "LEFT", w: "UP", d: "RIGHT", s: "DOWN",
        };
        if (map[e.key]) moveQueue.push(map[e.key]);
    }
});

// == toggle leaderboard sidebar ===
document.getElementById("toggleLeaderboard").addEventListener("click", () => {
    const list = document.getElementById("leaderboardList");
    list.style.display = list.style.display === "none" ? "block" : "none";
});

//fetch leaderboard
fetchLeaderboard();
draw();