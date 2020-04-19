let player = JSON.parse(document.getElementById('player').textContent);
let session = JSON.parse(document.getElementById('session').textContent);
let getQuestionURL = JSON.parse(document.getElementById('getQuestionURL').textContent);

if (window.location.protocol === 'https:') {
    protocol = 'wss:';
} else {
    protocol = 'ws:';
}

const chatSocket = new WebSocket(
    protocol
    + window.location.host
    + '/ws/chat/'
    + session.id
    + '/' +
    +player.id
    + '/'
);

chatSocket.onerror = function (e) {
    location.reload();
};

chatSocket.onopen = function (e) {
    chatSocket.send(JSON.stringify({
        "type": "user_joined",
        "username": player.name,
    }));
};

function send_message(title, body) {
    if (!title && !body) {
        return;
    }
    let message = '<div class="card">\n';
    if (title) {
        message += '<div class="card-header">' + title + '</div>\n';
    }
    message += '<div class="card-body">' + body + "</div></div>";
    let log = $('#chat-log');
    log.append(message);

    let height = log[0].scrollHeight;
    log.scrollTop(height);
}

function start_match(data) {
    $('#prompts').css('display', 'initial');
    $('#submitPrompt').click(function () {
        chatSocket.send(JSON.stringify({
            "type": "prompt_submission",
            "player": player.id,
            'prompts': $('.prompt').map(function () {
                return $(this).val()
            }).get() // gets all the prompt vals
        }));
        $('#prompts').css('display', 'none');
    });
}

function pose_questions(data) {
    $('#promptResponse').css('display', 'initial');
    $.ajax({
        method: 'GET',
        url: getQuestionURL,
        data: {
            player_id: player.id
        }
    }).done(function (msg) {
        console.log("Received response from getQuestion" + msg)
        msg = JSON.parse(msg);
        $('#promptResponse .prompt').text(msg.prompt);
    });
}

function user_joined(data) {
    if (data.username !== player.name) {
        $('#playerList ul').append(`
            <li class="list-group-item">${data.username}</li>
        `);
    }
}

function handle_game_events(data) {
    const handlers = {
        "start_match": start_match,
        "all_prompts_submitted": pose_questions,
        "user_joined": user_joined
    };
    if (data.type in handlers) {
        handlers[data.type](data);
    }
}

chatSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    console.log("Received message:  " + e.data);
    let title = '';
    let body = '';
    if (data.type === "chat_message") {
        title = data.username;
        body = data.message;
    } else if (data.type === "user_joined") {
        body = data.username + " has joined the fray!";
    } else if (data.type === "player_readied") {
        body = data.username + " is ready to start!";
    } else if (data.type === "start_match") {
        body = "Match is starting!";
    } else if (data.type === "prompt_submission") {
        body = data.player + " has submitted their prompts and are ready to go!"
    }
    send_message(title, body);

    handle_game_events(data);

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


$('#readyButton').click(function (e) {
    $('#readyButton').css('display', 'none');
    chatSocket.send(JSON.stringify({
        "type": "player_readied",
        "username": player.name
    }));
});

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
