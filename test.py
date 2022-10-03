import asyncio
from functools import reduce
import json
import websockets

IP_ADDR = "127.0.0.1"
IP_PORT = "8080"


def cq_code_at(user_id: int) -> str:
  return "[CQ:at,qq=" + str(user_id) + "]"


async def serverRecv(websocket):
  while True:
    res: dict = json.loads(await websocket.recv())
    try:
      if (res["post_type"] == "message" and res["message_type"] == "group"):
        msg: list = res["message"].split()
        if (msg[0] == "/echo"):
          echo_msg = reduce(lambda x, y: x + y, msg[1:])
          await websocket.send(
              json.dumps({
                  "action": "send_group_msg",
                  "params": {
                      "group_id": res["group_id"],
                      "message": cq_code_at(res["user_id"]) + ' ' + echo_msg
                  },
              }))
          await websocket.recv()  # {data}
        print(msg)
        print("res:", res)
      if (res["post_type"] != "meta_event"):
        print(res["post_type"])
    except Exception as e:
      print("Exception: ", e)
      print(res)


async def main():
  async with websockets.serve(serverRun, IP_ADDR, IP_PORT):
    await asyncio.Future()


async def serverRun(websocket, path):
  await serverRecv(websocket)


if __name__ == '__main__':
  print("======server main begin======")
  asyncio.run(main())
