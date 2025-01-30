import asyncio
from app.api import app
import uvicorn

async def main():
    config = uvicorn.Config(app, port=80)
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == '__main__':
    asyncio.run(main())
