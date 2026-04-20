import asyncio
import websockets

async def handler(websocket):
    print("[Mascot Proxy Mock] Client connected.")
    try:
        async for message in websocket:
            # Just acknowledging we receive data
            pass
    except websockets.ConnectionClosed:
        print("[Mascot Proxy Mock] Client disconnected.")

async def main():
    async with websockets.serve(handler, "localhost", 8000):
        print("[Mascot Proxy Mock] Running on ws://localhost:8000/proxy")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
