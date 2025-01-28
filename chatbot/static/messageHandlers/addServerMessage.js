import { scrollToBottom } from "../utils/index.js";

export function addServerMessage(messageContent) {
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

    // Set background color based on message type
    const messageType = parsedData.type;
    switch (messageType) {
      case "group_chat_run_chat":
        messageBox.style.background =
          "linear-gradient(90deg, #a8c0ff, #3f2b96)";
        break;
      case "text":
        messageBox.style.background =
          "linear-gradient(90deg, #fbc2eb, #a6c1ee)";
        break;
      case "tool_call":
        messageBox.style.background =
          "linear-gradient(90deg, #ffb347, #ffcc33)";
        break;
      case "execute_function":
        messageBox.style.background =
          "linear-gradient(90deg, #ff6a00, #ee0979)";
        break;
      case "tool_response":
        messageBox.style.background =
          "linear-gradient(90deg, #e2a8f3, #9b59b6)";
        break;
      default:
        messageBox.style.background = "#e6e6e6"; // Default
        break;
    }

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
  scrollToBottom();
}
