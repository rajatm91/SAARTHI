import { extractRelativePath } from "../utils/index.js";

export function addImageMessage(imagePath) {
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
