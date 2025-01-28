from fastapi import FastAPI
from fastapi.responses import FileResponse
from starlette.responses import HTMLResponse
from app.index import html

from app.websocket_manager import run_websocket_server
from starlette.staticfiles import StaticFiles
import os

app = FastAPI(lifespan=run_websocket_server)

# Mount the static directory to serve static files (like CSS and JS)
# app.mount("/chatbot/static", StaticFiles(directory="chatbot/static"), name="static")


# Mount the static directory to serve static files
static_dir = os.path.join(os.getcwd(), "chatbot/static")
app.mount("/chatbot/static", StaticFiles(directory=static_dir), name="static")


# Route for registry.html
@app.get("/registry.html")
async def serve_registry():
    file_path = os.path.join("chatbot", "static", "registry.html")
    return FileResponse(file_path)


@app.get("/")
async def get():
    return HTMLResponse(html)
