var client_id = Date.now();
var ip = document.getElementById("ip").value;
var ws = new WebSocket(`ws://${ip}/chats/ws/${client_id}`, {
  protocolVersion: 8,
  origin: `https:${ip}/chats/ws/${client_id}`,
  rejectUnauthorized: false
});

ws.onmessage = function (event) {
    var messages = document.getElementById('messages')
    console.log(event.data)
    console.log(typeof event.data)
    var data = JSON.parse(event.data)
    var message = `
        <article class="media">
            <figure class="media-left">
                <p class="image is-64x64">
                    <img class="is-rounded" src="${data.photo}">
                </p>
            </figure>
            <div class="media-content">
                <div class="content">
                    <p>
                        <strong>${data.sender_username}</strong>
                        <br>
                        ${data.message}
                        <br>
                    </p>
                </div>
            </div>
        </article>
    `;
    messages.innerHTML += message;
};

function sendMessage(event) {
    console.log(event.data)
    var text = document.getElementById("messageText");
    var chat_id = document.getElementById("chat_id").value;
    var user_id = document.getElementById("user_id").value;
    ws.send(`{"chat_id":"${chat_id}","message":"${text.value}","user_id":"${user_id}"}`);
    text.value = '';
    event.preventDefault();
}