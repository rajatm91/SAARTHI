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
  if (
    data &&
    data?.type !== "tool_response" &&
    data.content &&
    data.content.content
  ) {
    const messageContent = data.content.content.trim();
    const imagePath = extractImagePath(data.content.content);
    const finalAnswer =
      parseConcatenatedJSON(data?.content?.content)?.[0]?.final_answer || null;

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
      !isJsonObject(messageContent) &&
      finalAnswer
    ) {
      addMessage(finalAnswer, "agent");
    } else if (messageContent && data?.content?.sender_name !== "user_proxy") {
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

  messageElement.classList.add(sender); // Add 'user' or 'agent' class

  const parsedData = parseConcatenatedJSON(message) || message;
  if (parsedData && parsedData.length > 0) {
    // Iterate through parsed data and create accordions or plain messages
    parsedData?.forEach((data) => {
      const accordionContainer = document.createElement("div");
      accordionContainer.classList.add("accordion");

      // Handle objects by creating accordion items
      if (typeof data === "object") {
        Object.entries(data).forEach(([key, value]) => {
          if (key === "final_answer") {            
            const finalAnswerMessage = document.createElement("div");
            finalAnswerMessage.innerHTML = `<strong>FinalAnswer:</strong> ${value}`;
            messageElement.appendChild(finalAnswerMessage);
          } else {        
            const accordionItem = document.createElement("div");
            accordionItem.classList.add("accordion-item");

            // Accordion title
            const accordionTitle = document.createElement("div");
            accordionTitle.classList.add("accordion-title");
            accordionTitle.textContent = key;

            // Arrow span
            const arrow = document.createElement("span");
            arrow.classList.add("arrow");
            arrow.textContent = "▼"; // Default arrow
            accordionTitle.appendChild(arrow);

            // Click event for toggling accordion
            accordionTitle.onclick = function () {
              const isActive = this.classList.toggle("active");
              const content = this.nextElementSibling;
              arrow.textContent = isActive ? "▲" : "▼"; // Toggle arrow direction
              content.style.display = isActive ? "block" : "none";
            };

            // Accordion content
            const accordionContent = document.createElement("div");
            accordionContent.classList.add("accordion-content");
            accordionContent.style.display = "none"; // Hidden by default

            // Check if the value is an object or an array
            if (typeof value === "object") {
              const formattedContent = formatJSON(value);
              accordionContent.appendChild(formattedContent);
            } else {
              accordionContent.textContent = value;
            }

            accordionItem.appendChild(accordionTitle);
            accordionItem.appendChild(accordionContent);
            accordionContainer.appendChild(accordionItem);
          }
        });

        messageElement.appendChild(accordionContainer);
      } else {
        // If the data is a simple string, append it directly
        const simpleMessage = document.createElement("div");
        simpleMessage.textContent = data;
        messageElement.appendChild(simpleMessage);
      }
    });
  } else {
    messageElement.textContent = message;
  }

  document.getElementById("messages").appendChild(messageElement);
  scrollToBottom();
}

function formatJSON(json) {
  const container = document.createElement("div");

  if (Array.isArray(json)) {
    json.forEach((item, index) => {
      const itemDiv = document.createElement("div");
      itemDiv.classList.add("json-item");
      itemDiv.innerHTML = `<strong>[${index}]</strong>: ${
        typeof item === "object" ? "" : item
      }`;

      if (typeof item === "object") {
        const nestedContent = formatJSON(item);
        itemDiv.appendChild(nestedContent);
      }

      container.appendChild(itemDiv);
    });
  } else {
    Object.entries(json).forEach(([key, value]) => {
      const itemDiv = document.createElement("div");
      itemDiv.classList.add("json-item");
      itemDiv.innerHTML = `<strong>${key}:</strong> ${
        typeof value === "object" ? "" : value
      }`;

      if (typeof value === "object") {
        const nestedContent = formatJSON(value);
        itemDiv.appendChild(nestedContent);
      }

      container.appendChild(itemDiv);
    });
  }

  return container;
}
function parseConcatenatedJSON(concatenatedJSON) {
  try {
    // Split the string into separate JSON objects
    const jsonObjects = concatenatedJSON?.trim()?.split("\n");

    // console.log('JSON OBJECT',jsonObjects)
    // Parse each JSON string into an object
    const parsedObjects = jsonObjects?.map((jsonStr) => JSON.parse(jsonStr));

    return parsedObjects;
  } catch (error) {
    // console.error("Error parsing concatenated JSON:", error);
    return [];
  }
}

function addServerMessage(messageContent) {
  const serverMessagesContainer = document.getElementById("server-messages");

  if (!serverMessagesContainer) {
    console.error("Server messages container not found!");
    return;
  }

  const messages = Array.isArray(messageContent)
    ? messageContent
    : [messageContent];

  messages?.forEach((message, index) => {
    // Parse the incoming message
    const parsedData =
      typeof message === "string" ? JSON.parse(message) : message;

    // Create a message box
    const messageBox = document.createElement("div");
    messageBox.classList.add("message-box");

    // Recursive function to handle nested data
    const createKeyValueDiv = (key, value) => {
      const keyValueDiv = document.createElement("div");
      keyValueDiv.classList.add("key-value-pair");

      const keySpan = document.createElement("span");
      keySpan.classList.add("key");
      keySpan.textContent = key;

      const valueSpan = document.createElement("span");
      valueSpan.classList.add("value");

      // Handle nested objects
      if (typeof value === "object" && value !== null) {
        const nestedContainer = document.createElement("div");
        nestedContainer.classList.add("nested-container");

        Object.entries(value).forEach(([nestedKey, nestedValue]) => {
          nestedContainer.appendChild(
            createKeyValueDiv(nestedKey, nestedValue)
          );
        });

        valueSpan.appendChild(nestedContainer);
      } else if (
        typeof value === "string" &&
        (value.startsWith("{") || value.startsWith("["))
      ) {
        // Parse stringified JSON
        try {
          let parsedValue = JSON.parse(value);

          // Check if the parsed value is an array of JSON objects
          if (Array.isArray(parsedValue)) {
            parsedValue.forEach((item) => {
              const nestedContainer = document.createElement("div");
              nestedContainer.classList.add("nested-container");
              Object.entries(item).forEach(([nestedKey, nestedValue]) => {
                nestedContainer.appendChild(
                  createKeyValueDiv(nestedKey, nestedValue)
                );
              });
              valueSpan.appendChild(nestedContainer);
            });
          } else if (typeof parsedValue === "object") {
            const nestedContainer = document.createElement("div");
            nestedContainer.classList.add("nested-container");

            Object.entries(parsedValue).forEach(([nestedKey, nestedValue]) => {
              nestedContainer.appendChild(
                createKeyValueDiv(nestedKey, nestedValue)
              );
            });

            valueSpan.appendChild(nestedContainer);
          } else {
            valueSpan.textContent = parsedValue;
          }
        } catch (e) {
          valueSpan.textContent = value; // If parsing fails, show as is
        }
      } else {
        valueSpan.textContent = value;
      }

      keyValueDiv.appendChild(keySpan);
      keyValueDiv.appendChild(valueSpan);
      return keyValueDiv;
    };

    // Handle the nested 'content' field if it contains stringified JSON
    if (parsedData.content && typeof parsedData.content === "string") {
      // First, decode the escaped string inside the content field
      let contentDecoded;
      try {
        contentDecoded = JSON.parse(parsedData.content); // Parse the outer content first
      } catch (e) {
        console.error("Failed to parse the content:", e);
        contentDecoded = parsedData.content; // Fallback to raw content
      }

      // Now check if the contentDecoded has newline-separated JSON objects
      if (typeof contentDecoded === "string" && contentDecoded.includes("\n")) {
        const contentParts = contentDecoded
          .split("\n")
          .map((item) => {
            try {
              return JSON.parse(item.trim()); // Try parsing each line
            } catch (e) {
              return item.trim(); // Fallback to raw string if parsing fails
            }
          })
          .filter(Boolean); // Remove empty entries

        contentParts.forEach((contentPart) => {
          if (typeof contentPart === "object" && contentPart !== null) {
            Object.entries(contentPart).forEach(([key, value]) => {
              messageBox.appendChild(createKeyValueDiv(key, value));
            });
          } else {
            const textDiv = document.createElement("div");
            textDiv.classList.add("text-content");
            textDiv.textContent = contentPart;
            messageBox.appendChild(textDiv); // For non-object content, just display the raw text
          }
        });
      } else {
        // If it's a single JSON object or string, parse and display it
        if (typeof contentDecoded === "object" && contentDecoded !== null) {
          Object.entries(contentDecoded).forEach(([key, value]) => {
            messageBox.appendChild(createKeyValueDiv(key, value));
          });
        } else {
          const textDiv = document.createElement("div");
          textDiv.classList.add("text-content");
          textDiv.textContent = contentDecoded;
          messageBox.appendChild(textDiv); // For non-object content, just display the raw text
        }
      }
    } else {
      // If no nested content, just render the regular message
      Object.entries(parsedData).forEach(([key, value]) => {
        messageBox.appendChild(createKeyValueDiv(key, value));
      });
    }

    // Add the message box to the container
    serverMessagesContainer.appendChild(messageBox);

    // Add a connector if it's not the last message
    if (index === messages.length - 1) {
      const connector = document.createElement("div");
      connector.classList.add("connector");
      serverMessagesContainer.appendChild(connector);
    }
  });

  // Scroll to the bottom to show the latest messages
  // setTimeout(() => {
  //   serverMessagesContainer.scrollTop = serverMessagesContainer.scrollHeight;
  // }, 0);
  scrollToBottom();
}

function parseMessage(message) {
  try {
    return JSON.parse(message);
  } catch (e) {
    console.error("Failed to parse message:", message);
    return { error: "Invalid JSON" };
  }
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
    image.src = extractRelativePath(imagePath); 

    image.alt = "Server Image";

    // Append the image to the message
    newMessage.appendChild(image);
    messages.appendChild(newMessage);
  } else {
    console.error("Messages container not found!");
  }
}
function extractRelativePath(imagePath) {
  const basePath = "/chatbot/static/"; 
  const index = imagePath.indexOf(basePath);
  if (index !== -1) {
    return imagePath.substring(index);
  }
  return null; 
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
