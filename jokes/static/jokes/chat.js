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

chatSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    var message = playerName + ": " + data.message;
    $('#chat-log').append(message + '\n');
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
        "username": playerName,
        'message': message
    }));
    messageInputDom.value = '';
};
