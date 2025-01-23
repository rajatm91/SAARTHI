import asyncio
from contextlib import asynccontextmanager
from http.server import SimpleHTTPRequestHandler, HTTPServer
from pathlib import Path

import uvicorn
from autogen.io import IOWebsockets
from fastapi import FastAPI
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocket

from smart_analyst_autogen.main import on_connect

PORT = 8001


# class MyRequestHandler(SimpleHTTPRequestHandler):
#     def __init__(self, *args, **kwargs):
#         super().__init__(
#             *args,
#             directory=Path(__file__).parents[1] / "website_files" / "templates",
#             **kwargs,
#         )
#
#     def do_GET(self):
#         if self.path == "/":
#             self.path = "/chat.html"
#         return SimpleHTTPRequestHandler.do_GET(self)
#
#
# handler = MyRequestHandler
#
# with IOWebsockets.run_server_in_thread(on_connect=on_connect, port=8080) as uri:
#     print(f"Websocket server started at {uri}", flush=True)
#
#     with HTTPServer(("", PORT), handler) as httpd:
#         print(f"HTTP server started at http://localhost:{str(PORT)}")
#
#         try:
#             httpd.serve_forever()
#         except KeyboardInterrupt:
#             print(" - HTTP server stopped.", flush = True)

html = """
<!DOCTYPE html>
<html>
<head>
    <title>SAARTHI: Smart AI Agent for Real-Time Handling & Insights</title>
    <style>
        body {
            font-family: sans-serif;
            margin: 0;
            padding: 0;
            background: #fafafa;
        }

        .chat-container {
            /* Make the chat box bigger and centered */
            max-width: 80%;
            height: 85vh;  /* Occupies most of the vertical screen */
            margin: 2rem auto;
            display: flex;
            flex-direction: column;
            border: 1px solid #ccc;
            border-radius: 8px;
            background-color: #fff;
        }

        .title {
            text-align: center;
            margin-bottom: 1rem;
        }

        .messages {
            list-style-type: none;
            padding: 0;
            margin: 0;
        }

        .message {
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 5px;
            max-width: 70%;
            clear: both;
        }

        /* Align user messages on the right */
        .user-message {
            background-color: #DCF8C6;
            margin-left: auto;
            text-align: left;
        }

        /* Align agent messages on the left */
        .agent-message {
            background-color: #F0F0F0;
            margin-right: auto;
            text-align: left;
        }

        .input-area {
            display: flex;
            margin-top: 1rem;
        }

        .input-area input {
            flex: 1;
            padding: 0.5rem;
        }

        .input-area button {
            padding: 0.5rem 1rem;
            margin-left: 0.5rem;
        }
    </style>
</head>
<body>
<div class="chat-container">
    <h2 class="title">SAARTHI: Smart AI Agent for Real-Time Handling & Insights</h2>

    <ul id="messages" class="messages"></ul>

    <div class="input-area">
        <input type="text" id="messageText" placeholder="Type a message..." autocomplete="off"/>
        <button onclick="sendMessage()">Send</button>
    </div>
</div>

<script>
let ws;

function connectWebSocket() {
    ws = new WebSocket("ws://localhost:8080/ws");

    ws.onopen = function() {
        console.log("WebSocket connection established.");
    };

    ws.onmessage = function(event) {
    try {
        const data = JSON.parse(event.data);
        // Filter out "terminate" messages
        // if (data.type === "text" && data.content?.content?.includes("TERMINATE")) {
        //     console.log("Terminate message received, skipping display.");
        //     console.log("Message: ", data.content);
        //     return; // Skip rendering this message
        // }

        // Handle "text" messages
        
        if (data.type === "text") {
            const { sender_name, content } = data.content || {};
            console.log("Text message: ", content);
            console.log("Sender_name: ", sender_name);
            const cleanedContent = content.replace(/TERMINATE/g, "").trim();
            
            if (cleanedContent){
                console.log("Cleaned content: ", cleanedContent);
                console.log("Sender_name: ", sender_name);
                
                const imagePath = extractImagePath(content);

                if (imagePath) {
                    // Render the image
                    const imageUrl = `/static/images/${imagePath.split("/").pop()}`; // Convert local path to URL
                    renderImage(imageUrl);
                } else {
                    addMessage(cleanedContent, sender_name);
                }
            } else {
                console.log("Content is empty after removing TERMINATE, skipping display.");
            }    
            
        } else {
            console.log("Non-text message:", data);
            }
        } catch (error) {
        console.error("Error parsing WebSocket message:", error);
        }
    };

    ws.onclose = function(event) {
        console.log("WebSocket connection closed:", event);
        // Attempt to reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
    };
}
connectWebSocket(); // Initial connection

function extractImagePath(message) {
    const regex = /!\[.*?\]\((.*?)\)/; // Matches Markdown image syntax
    const match = message.match(regex);
    return match ? match[1] : null; // Returns the image path or null
}

function renderImage(imageUrl) {
    const messages = document.getElementById("messages");
    const img = document.createElement("img");
    img.src = imageUrl;
    img.style.maxWidth = "100%";
    messages.appendChild(img);

    // Scroll to bottom
    messages.scrollTop = messages.scrollHeight;
}

function addMessage(text, senderName) {
    const messages = document.getElementById("messages");
    const li = document.createElement("li");
    li.classList.add("message");

    if (senderName === "user_proxy") {
        li.classList.add("user-message");
    } else {
        li.classList.add("agent-message");
    }

    li.textContent = text || "";
    messages.appendChild(li);
    messages.scrollTop = messages.scrollHeight;
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
        ws.send(JSON.stringify(msg));
        input.value = "";
        addMessage(text, "user_proxy");
    } else {
        console.error("WebSocket is not open.");
    }
}
</script>
</body>
</html>
"""


@asynccontextmanager
async def run_websocket_server(app):
    try:
        with IOWebsockets.run_server_in_thread(on_connect=on_connect, port=8080) as uri:
            print(f"WebSocket server started at {uri}.", flush=True)
            yield
    except Exception as e:
        print(f"Failed to start WebSocket server: {e}", flush=True)
        raise
    finally:
        print("WebSocket server stopped.", flush=True)

app = FastAPI(lifespan=run_websocket_server)

#app.mount("~/Development/HDFC/smart-analyst-autogen/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def get():
    return { "name": "SAARTHI: Smart AI Agent for Real-Time Handling & Insights" }



@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        # Handle the received message
        print(f"Received message: {data}")
        # You can send a response back if needed
        await websocket.send_text(f"Message text was: {data}")


async def main():
    config = uvicorn.Config(app)
    server = uvicorn.Server(config)
    await server.serve()



if __name__ == '__main__':
    asyncio.run(main())

