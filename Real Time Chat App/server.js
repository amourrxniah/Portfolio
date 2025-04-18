//server.js
const express = require("express");
const http = require("http");
const path = require("path");
const { Server} = require("socket.io");
const { text } = require("stream/consumers");

const app = express();
const server = http.createServer(app);
const io = new Server(server);

const users = {}; //socket.id => { username, room }
const messages = {}; //room => [message1, message2]

//serve static files
app.use(express.static(path.join(__dirname, "public")));

io.on("connection", (socket) => {
    socket.on("joinRoom", ({ username, room }) => {
        socket.join(room);
        users[socket.id] = { username, room };

        //welcome message to new user
        socket.emit("message", { user: "System", text: `Welcome to ${room}, ${username}` });

        //broadcast to others in the room
        socket.to(room).emit("message", { user: "System", text: `${username} has joined.` });

        //send previous messages
        if (messages[room]) {
            messages[room].forEach((msg) => socket.emit("message", msg));
        } else {
            messages[room] = [];
        }
    });

    socket.on("chatMessage", (text) => {
        const user = users[socket.id];
        const msg = { user: user.username, text };
        messages[user.room].push(msg);
        io.to(user.room).emit("message", msg);
    });

    socket.on("typing", (isTyping) => {
        const user = users[socket.id];
        if (user) {
            socket.to(user.room).emit("typing", { username: user.username, isTyping });
        }
    });

    socket.on("disconnect", () => {
        const user = users[socket.id];
        if (user) {
            io.to(user.room).emit("message", { user: "System", text: `${user.username} left.` });
            delete users[socket.id];
        }
    });
});

server.listen(3000, () => console.log("🚀 Server on http://localhost:3000"));