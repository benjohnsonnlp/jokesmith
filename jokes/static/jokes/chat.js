var player = JSON.parse(document.getElementById('player').textContent);
var session = JSON.parse(document.getElementById('session').textContent);

if (window.location.protocol === 'https:') {
    protocol = 'wss:';
} else {
    protocol = 'ws:';
}

const chatSocket = new WebSocket(
    protocol
    + window.location.host
    + '/ws/chat/'
    + session.name
    + '/'
);

chatSocket.onopen = function (e) {
    chatSocket.send(JSON.stringify({
        "type": "user_joined",
        "username": player.name,
    }));
}

chatSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    console.log("Received message:  " + data);
    var title = '';
    var body = '';
    if (data.type === "chat_message") {
        title = data.username;
        body = data.message;
    } else if (data.type === "user_joined") {
        body = data.username + " has joined the fray!";
    } else if (data.type === "player_readied") {
        body = data.username + " is ready to start!";
    }
    var message = '<div class="card">\n';
    if (title) {
        message += '<div class="card-header">' + title + '</div>\n';
    }
    message += '<div class="card-body">' + body + "</div></div>";
     $('#chat-log').append(message);
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


document.querySelector('#readyButton').onclick = function (e) {
    chatSocket.send(JSON.stringify({
        "type": "player_readied",
        "username": player.name
    }));
};

document.querySelector('#chat-message-submit').onclick = function (e) {
    const messageInputDom = document.querySelector('#chat-message-input');
    const message = messageInputDom.value;
    chatSocket.send(JSON.stringify({
        "type": "chat_message",
        "username": player.name,
        'message': message
    }));
    messageInputDom.value = '';
};
