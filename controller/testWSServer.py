import asyncio
import websockets


async def echo(websocket):
    async for message in websocket:
        print(websocket)
        print(message)
        await websocket.send(message)


async def main():
    async with websockets.serve(echo, "localhost", 8765):
        await asyncio.Future()

asyncio.run(main())
