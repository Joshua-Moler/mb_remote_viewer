import asyncio
import websockets
import requests


async def hello():
    async with websockets.connect('') as websocket:
        await websocket.send("Hello world!")
        await websocket.recv()

asyncio.run(hello())
