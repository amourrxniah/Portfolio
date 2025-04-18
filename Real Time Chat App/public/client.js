const socket = io();
const form = document.getElementById("chat-form");
const msgInput = document.getElementById("msg");
const chatBox = document.getElementById("chat-box");
const typingIndicator = document.getElementById('typing');

//parse URL params
const { username, room } = Object.fromEntries(new URLSearchParams(location.search).entries);

//join room
socket.emit('joinRoom', { username, room });

//send message
form.addEventListener('submit', (e) => {
    e.preventDefault();
    socket.emit('chatMessage', msgInput.value);
    msgInput.value = "";
    socket.emit("typing", false);
});

//receive message from server
socket.on('message', (msg) => {
    const p = document.createElement("p");
    p.textContent = `${msg.user}: ${msg.text}`;
    chatBox.appendChild(p);
    chatBox.scrollTop = chatBox.scrollHeight;
});

//typing event
msgInput.addEventListener("input", () => {
    socket.emit("typing", msgInput.value.length > 0);
});

socket.on("typing", ({ username, isTyping }) => {
    typingIndicator.textContent = isTyping ? `${username} is typing...` : "";
});
