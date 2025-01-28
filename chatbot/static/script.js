import { addMessage } from './messageHandlers/addMessage.js';
import { connectWebSocket, ws } from './websocket/connectWebSocket.js';

function sendMessage() {
  console.log('I am CLicked')
  const input = document.getElementById("messageText");
  const text = input.value.trim();
  if (!text) return;

  const msg = {
    type: "text",
    content: {
      uuid: "some-random-uuid",
      content: text,
      sender_name: "user_proxy",
      recipient_name: "data_analyst_agent"
    }
  };

  if (ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(msg)); // Send the function name and params to the server
    input.value = "";
    addMessage(text, "user");
  } else {
    console.error("WebSocket is not open.");
  }
}

document.getElementById("messageText").addEventListener("keydown", function (event) {
  if (event.key === "Enter") {
    sendMessage();
  }
});

window.sendMessage = sendMessage;

window.onload = function () {
  connectWebSocket();
};