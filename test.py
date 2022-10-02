import asyncio
import json
import websockets

IP_ADDR = "127.0.0.1"
IP_PORT = "8080"


async def serverRecv(websocket):
  while True:
    res = json.loads(await websocket.recv())
    if (res["post_type"] == "message"):
      print(res["message_id"])
      await websocket.send(
          json.dumps({
              "action": "get_msg",
              "params": {
                  "message_id": res["message_id"]
              },
          }))
      msg = await websocket.recv()
      print("res:", res)
      print("msg:", msg)
    print(res["post_type"])


async def serverRun(websocket, path):
  print(path)
  await serverRecv(websocket)


if __name__ == '__main__':
  print("======server main begin======")
  server = websockets.serve(serverRun, IP_ADDR, IP_PORT)
  asyncio.get_event_loop().run_until_complete(server)
  asyncio.get_event_loop().run_forever()
