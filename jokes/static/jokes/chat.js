//playerName and lobbyName defined in session.html
console.log("Recieved playerName " + playerName + " and sessionName " + sessionName);
if (window.location.protocol === 'https:') {
    protocol = 'wss:';
} else {
    protocol = 'ws:';
}

const chatSocket = new WebSocket(
    protocol
    + window.location.host
    + '/ws/chat/'
    + sessionName
    + '/'
);

chatSocket.onopen = function (e) {
    chatSocket.send(JSON.stringify({
        "type": "user_joined",
        "username": playerName,
    }));
}


chatSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    console.log("Received message:  " + data);
    if (data.type === "chat_message") {
        const message = data.username + ": " + data.message;
        $('#chat-log').append(message + '\n');
    } else if (data.type === "user_joined") {
        const message = data.username + " has joined the fray!";
        $('#chat-log').append(message + '\n');
    }
};

chatSocket.onclose = function (e) {
    console.error('Chat socket closed unexpectedly');
};

document.querySelector('#chat-message-input').focus();
document.querySelector('#chat-message-input').onkeyup = function (e) {
    if (e.keyCode === 13) {  // enter, return
        document.querySelector('#chat-message-submit').click();
    }
};

document.querySelector('#chat-message-submit').onclick = function (e) {
    const messageInputDom = document.querySelector('#chat-message-input');
    const message = messageInputDom.value;
    chatSocket.send(JSON.stringify({
        "type": "chat_message",
        "username": playerName,
        'message': message
    }));
    messageInputDom.value = '';
};
