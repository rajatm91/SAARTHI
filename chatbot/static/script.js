let ws;
let lastMessageTime = 0;

function connectWebSocket() {
  // if (reconnecting) return; // Prevent multiple reconnections
  // reconnecting = true;

  ws = new WebSocket("ws://localhost:8080/ws");

  ws.onopen = function () {
    console.log("WebSocket connection established.");
  };

  ws.onmessage = function (event) {
    const data = JSON.parse(event.data);
    handleMessage(data);
    // if (data && data.content && data.content.content) {
    //     const messageContent = data.content.content.trim();

    //     if (messageContent && messageContent !== "TERMINATE") {
    //         console.log('Message from server:', messageContent);
    //         addMessage(messageContent, "agent");
    //     } else {
    //         console.log('Invalid or terminate message:', messageContent);
    //     }
    // }
  };

  ws.onclose = function (event) {
    console.log("WebSocket connection closed:", event);
    setTimeout(connectWebSocket, 3000);
  };
}

function handleMessage(data) {
  if (data && data.content && data.content.content) {
    const messageContent = data.content.content.trim();

    if (
      messageContent &&
      messageContent !== "TERMINATE" &&
      typeof messageContent === "string" &&
      !isJsonObject(messageContent)
    ) {
      console.log(
        "Message from server:",
        typeof messageContent === "string",
        messageContent
      );
      addMessage(messageContent, "agent");
    } else {
      console.log("Invalid or terminate message:", messageContent);
    }
  }
}

function sendMessage() {
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

function addMessage(message, sender) {
  const messageList = document.getElementById("messages");
//   const listItem = document.createElement("li");
//   listItem.textContent = `${sender}: ${message}`;
//   messageList.appendChild(listItem);

  const messageElement = document.createElement("li");
  messageElement.textContent = message;
  messageElement.classList.add(sender); // Add 'user' or 'agent' class

  document.getElementById("messages").appendChild(messageElement);
  scrollToBottom();
}

function scrollToBottom() {
  const messages = document.getElementById("messages");
  messages.scrollTop = messages.scrollHeight;
}

// Call connectWebSocket when the page loads
window.onload = function () {
  connectWebSocket();
};

function isJsonObject(str) {
  try {
    const parsed = JSON.parse(str);
    return typeof parsed === "object" && parsed !== null;
  } catch (e) {
    return false;
  }
}
