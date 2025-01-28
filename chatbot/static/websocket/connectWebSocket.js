export let ws;
// import { handleMessage } from '../../app/messageHandlers/handleMessage';
import { handleMessage } from '../messageHandlers/handleMessage.js';

export function connectWebSocket() {
  ws = new WebSocket("ws://localhost:8080/ws");

  ws.onopen = () => {
    console.log("WebSocket connection established.");
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    handleMessage(data);
  };

  ws.onclose = (event) => {
    console.log("WebSocket connection closed:", event);
    setTimeout(connectWebSocket, 3000);
  };
}

export function getWebSocket() {
  return ws;
}
