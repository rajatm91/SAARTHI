
from fastapi import FastAPI
from starlette.responses import HTMLResponse
from app.html_template import html
from app.websocket_manager import run_websocket_server
from starlette.staticfiles import StaticFiles
import os

app = FastAPI(lifespan=run_websocket_server)

# Mount the static directory to serve static files (like CSS and JS)
# app.mount("/chatbot/static", StaticFiles(directory="chatbot/static"), name="static")


# Mount the static directory to serve static files
static_dir = os.path.join(os.getcwd(), "chatbot/static")
app.mount("/chatbot/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def get():
    return HTMLResponse(html)
