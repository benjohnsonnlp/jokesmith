let player = JSON.parse(document.getElementById('player').textContent);
let session = JSON.parse(document.getElementById('session').textContent);
let getQuestionURL = JSON.parse(document.getElementById('getQuestionURL').textContent);
let getVotingURL = JSON.parse(document.getElementById('getVotingURL').textContent);

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
        "player": player,
    }));
};

function send_message(title, body) {
    if (!title && !body) {
        return;
    }
    let message = '<div class="card">\n';
    if (title) {
        message += ('<div class="card-header">' + title + '</div>\n'
            + '<div class="card-body">' + body + "</div></div>");
    } else {
        message += '<div class="card-body notice">' + body + "</div></div>";
    }

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

function displayQuestion(msg) {
    console.log("Received response from getQuestion" + msg)
    msg = JSON.parse(msg);
    if (!msg.response) {
        $('#promptResponse').css('display', 'none');
        $('#waiting').css('display', 'initial');
    } else {
        let prompt = $('#promptResponse .prompt');
        prompt.text(msg.prompt.text);
        $('#submitResponse').click(function (evt) {
            submitResponse()
        });
        let text = $('#responseText');

        text.attr("response_id", msg.response.id);
        text.val('');
        // text.click(function (event) {
        //     if (event.keyCode == 13) {
        //         submitResponse();
        //     }
        // });
    }
}

function submitResponse() {
    $('#promptResponse').hide();
    $('#waiting').show();
    let textfield = $('#responseText');
    chatSocket.send(JSON.stringify({
        "type": "response_submission",
        "player": player.id,
        "text": textfield.val(),
        "response_id": textfield.attr("response_id")
    }));
}

function pose_questions(data) {
    $('.prompt-text').val('');
    $('#promptResponse').show();
    $('#waiting').hide();
    $.ajax({
        method: 'GET',
        url: getQuestionURL,
        data: {
            player_id: player.id
        }
    }).done(displayQuestion);
}

function submitVote() {
    let selected = $('#votingContainer input:checked');
    chatSocket.send(JSON.stringify({
        "type": "vote_submission",
        "player": player.id,
        "response_id": selected.attr("responseid")
    }));
    $('#votingContainer').hide();
    $('#waiting').show();
}


// Example ballot
// {
//   "prompt": {
//     "id": 132,
//     "text": "Unknown Baldwin brother",
//     "author": 2
//   },
//   "responses": [
//     {
//       "id": 334,
//       "player": 14,
//       "prompt": 132,
//       "session": 82,
//       "text": "response from 0"
//     },
//     {
//       "id": 335,
//       "player": 16,
//       "prompt": 132,
//       "session": 82,
//       "text": "response from 2"
//     },
//   ],
//   "can_vote": false
// }

function displayVoting(msg) {
    console.log("Received response from getVoting" + msg)
    msg = JSON.parse(msg);
    $('#votingContainer h3').text(msg.prompt.text);
    let list = $('#votingContainer .group');
    list.html('');
    for (i in msg.responses) {
        let response = msg.responses[i];
        list.append(`
            <div class="form-check">
                <input type="radio" name="voteOptions" 
                       class="form-check-input voteRadio" responseId="${response.id}"> 
                
                <label class="form-check-label">
                    ${response.text}
                </label>
            
            </div>
        `);
    }
    $('#votingSubmit').off('click').click(submitVote);
}

function begin_voting(data) {
    $('#promptResponse').hide();
    $('#resultsContainer').hide();
    $('#waiting').hide();
    $('#votingContainer').show();
    $.ajax({
        method: 'GET',
        url: getVotingURL,
        data: {
            player_id: player.id
        }
    }).done(displayVoting);
}

function user_joined(data) {
    if (data.player.id !== player.id) {
        $('#playerList ul').append(`
            <li class="list-group-item" playerId="${data.player.id}">
                ${data.player.name}
                <span class="badge badge-primary badge-pill">${data.player.score}</span>
            </li>
        `);
    }
}

//  Results look like
//  {
//   "type": "display_results",
//   "prompt": {
//     "id": 1,
//     "text": "Weird thing to say to in-laws",
//     "author": null
//   },
//   "results": [
//     {
//       "response": {
//         "id": 13,
//         "player": 2,
//         "prompt": 1,
//         "session": 4,
//         "text": "response from 0"
//       },
//       "votes": [
//         {
//           "id": 4,
//           "player": 3,
//           "response": 13,
//           "session": 4
//         }
//       ]
//     },
//     {
//       "response": {
//         "id": 14,
//         "player": 4,
//         "prompt": 1,
//         "session": 4,
//         "text": "response from 2"
//       },
//       "votes": []
//     }
//   ],
//   players: [ list of player objects]
// }



function display_results(data) {
    $('#promptResponse').hide();
    $('#waiting').hide();
    $('#votingContainer').hide();
    $('#resultsContainer').show();

    updatePlayerInfo(data.players);

    $('#resultsContainer h3').text(data.prompt.text);
    let list = $('#resultsContainer > ul');
    list.html('');
    for (let i in data.results) {
        let result = data.results[i];
        let html = '';
        html += `
            <li class="list-group-item">
                 ${result.response.text} <i>--${result.response.player_name}</i>: ${result.votes.length} votes
                 <ul class="list-group">
        `;

        result.votes.forEach(function (vote, index) {
            html += `
                    <li class="list-group-item">
                       ${vote.player_name}
                    </li>
           `;
        });

        html += `
                </ul>
            </li>
        `;

        list.append(html);
    }
}

function updatePlayerInfo(players) {
    players.forEach(function(player, index){
        let score = player.score;
        $(`#playerList li[playerId=${player.id}] span.badge`).each(function() {
            $(this).text(score);
        });
    });

}

function reset_session(data) {
    $('#promptResponse').hide();
    $('#waiting').hide();
    $('#votingContainer').hide();
    $('#resultsContainer').hide();
    $('#readyButton').show();
}

function handle_game_events(data) {
    const handlers = {
        "start_match": start_match,
        "all_prompts_submitted": pose_questions,
        "user_joined": user_joined,
        "next_question": pose_questions,
        "begin_voting": begin_voting,
        "display_results": display_results,
        "reset_session": reset_session
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
    $('#readyButton').hide();
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
