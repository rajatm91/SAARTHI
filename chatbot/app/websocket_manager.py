from contextlib import asynccontextmanager
from autogen.io import IOWebsockets
from agents.agents import on_connect

@asynccontextmanager
async def run_websocket_server(app):
    print("Setting up WebSocket server...", flush=True)
    try:
        with IOWebsockets.run_server_in_thread(on_connect=on_connect, port=8080) as uri:
            print(f"WebSocket server started at {uri}.", flush=True)
            yield
    except Exception as e:
        print(f"Failed to start WebSocket server: {e}", flush=True)
        raise
    finally:
        print("WebSocket server stopped.", flush=True)
