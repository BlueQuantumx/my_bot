import asyncio
import json
import websockets

from debug import debug_print
from echo import echo
import image_lib

IP_ADDR = "127.0.0.1"
IP_PORT = "8080"

image_lib.init()
plugins = [debug_print, echo, image_lib.image_lib]


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
