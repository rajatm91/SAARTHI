import { parseConcatenatedJSON } from "../utils/parseConcatenatedJSON.js";
import { formatJSON } from "../utils/formatJSON.js";
import { scrollToBottom } from "../utils/index.js";

export function addMessage(message, sender) {
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
