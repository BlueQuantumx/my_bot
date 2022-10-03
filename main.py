import asyncio
import json
import websockets

from echo import echo

IP_ADDR = "127.0.0.1"
IP_PORT = "8080"

plugins = [echo]


async def serverRecv(websocket):
  async for recv in websocket:
    message: dict = json.loads(recv)
    for func in plugins:
      await func(message, websocket)


async def main():
  async with websockets.serve(serverRun, IP_ADDR, IP_PORT):
    await asyncio.Future()


async def serverRun(websocket):
  print("Server started.")
  await serverRecv(websocket)


if __name__ == '__main__':
  print("======server main begin======")
  asyncio.run(main())
