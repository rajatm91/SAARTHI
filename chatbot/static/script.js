let ws;

function connectWebSocket() {
  ws = new WebSocket("ws://localhost:8080/ws");

  ws.onopen = function () {
    console.log("WebSocket connection established.");
  };

  ws.onmessage = function (event) {
    const data = JSON.parse(event.data);
    handleMessage(data);
  };

  ws.onclose = function (event) {
    console.log("WebSocket connection closed:", event);
    setTimeout(connectWebSocket, 3000);
  };
}

function handleMessage(data) {
  addServerMessage(JSON.stringify(data));
  if (data && data.content && data.content.content) {
    const messageContent = data.content.content.trim();
    const imagePath = extractImagePath(data.content.content);
   
    if (messageContent.includes("Here is the analysis")) {
      // Extract and format the table data
      const rows = messageContent
        .split("\n")
        .filter((line) => line.includes(":")) // Filter lines with data
        .map((line) => {
          const [key, value] = line.split(":");
          return { key: key.trim(), value: value.trim() };
        });

      // Display the data in tabular format
      addTableMessage(rows);
    } else if (imagePath) {
      // If image path is present, display the image in the chat
      addImageMessage(imagePath);
    } else if (
      messageContent &&
      messageContent !== "TERMINATE" &&
      typeof messageContent === "string" &&
      !isJsonObject(messageContent)
    ) {
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
  const messageElement = document.createElement("li");
  messageElement.textContent = message;
  messageElement.classList.add(sender); // Add 'user' or 'agent' class

  document.getElementById("messages").appendChild(messageElement);
  scrollToBottom();
}

// // Function to add messages to the server messages chat
function addServerMessage(messageContent) {
  const serverMessages = document.getElementById("server-messages");
  if (serverMessages) {
    const newMessage = document.createElement("li");
    newMessage.textContent = messageContent;
    newMessage.classList.add("agent");
    serverMessages.appendChild(newMessage);
  } else {
    console.error("Server messages container not found!");
  }
  scrollToBottomServerMessage();
}

function scrollToBottomServerMessage() {
  const messages = document.getElementById("server-messages");
  messages.scrollTop = messages.scrollHeight;
}
function scrollToBottom() {
  const messages = document.getElementById("messages");
  messages.scrollTop = messages.scrollHeight;
}

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

function extractImagePath(message) {
  const regex = /!\[.*?\]\((.*?)\)/; 
  const match = message.match(regex);
  return match ? match[1] : null; 
}

function addImageMessage(imagePath) {
  const messages = document.getElementById("messages");
  if (messages) {
    const newMessage = document.createElement("li");
    newMessage.classList.add("agent");

    const image = document.createElement("img");
    image.src = "https://picsum.photos/536/354";

    image.alt = "Server Image";

    // Append the image to the message
    newMessage.appendChild(image);
    messages.appendChild(newMessage);
  } else {
    console.error("Messages container not found!");
  }
}

function addTableMessage(rows) {
  const messages = document.getElementById("messages");
  if (messages) {
    const newMessage = document.createElement("li");
    newMessage.classList.add("agent");

    // Create table element
    const table = document.createElement("table");
    table.style.borderCollapse = "collapse";
    table.style.width = "100%";

    // Add table header
    const headerRow = document.createElement("tr");
    const header1 = document.createElement("th");
    const header2 = document.createElement("th");
    header1.textContent = "Month";
    header2.textContent = "Amount";
    header1.style.border = "1px solid #ddd";
    header2.style.border = "1px solid #ddd";
    header1.style.padding = "8px";
    header2.style.padding = "8px";
    header1.style.textAlign = "left";
    header2.style.textAlign = "left";
    headerRow.appendChild(header1);
    headerRow.appendChild(header2);
    table.appendChild(headerRow);

    // Add rows to the table
    rows.forEach((row) => {
      const tableRow = document.createElement("tr");
      const cell1 = document.createElement("td");
      const cell2 = document.createElement("td");
      cell1.textContent = row.key;
      cell2.textContent = row.value;
      cell1.style.border = "1px solid #ddd";
      cell2.style.border = "1px solid #ddd";
      cell1.style.padding = "8px";
      cell2.style.padding = "8px";
      tableRow.appendChild(cell1);
      tableRow.appendChild(cell2);
      table.appendChild(tableRow);
    });

    // Append the table to the message
    newMessage.appendChild(table);
    messages.appendChild(newMessage);
  } else {
    console.error("Messages container not found!");
  }
}
