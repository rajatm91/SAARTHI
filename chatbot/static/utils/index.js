export function scrollToBottom() {
  const messages = document.getElementById("messages");
  messages.scrollTop = messages.scrollHeight;
}

export function isJsonObject(str) {
  try {
    const parsed = JSON.parse(str);
    return typeof parsed === "object" && parsed !== null;
  } catch (e) {
    return false;
  }
}

export function extractImagePath(message) {
  const regex = /!\[.*?\]\((.*?)\)/;
  const match = message.match(regex);
  return match ? match[1] : null;
}

export function extractRelativePath(imagePath) {
  const basePath = "/chatbot/static/";
  const index = imagePath.indexOf(basePath);
  if (index !== -1) {
    return imagePath.substring(index);
  }
  return null;
}

export function parseMessage(message) {
  try {
    return JSON.parse(message);
  } catch (e) {
    console.error("Failed to parse message:", message);
    return { error: "Invalid JSON" };
  }
}
