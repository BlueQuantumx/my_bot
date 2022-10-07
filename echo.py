from functools import reduce
from utils import cq_code_at
import json


async def echo(message: dict, websocket):
  try:
    if (message["post_type"] == "message"
        and message["message_type"] == "group"):
      msg: list = message["message"].split()
      if (msg[0] == "/echo"):
        echo_msg = reduce(lambda x, y: x + ' ' + y, msg[1:])
        await websocket.send(
            json.dumps({
                "action": "send_group_msg",
                "params": {
                    "group_id": message["group_id"],
                    "message": cq_code_at(message["user_id"]) + echo_msg
                },
            }))
        await websocket.recv()
  except Exception as e:
    print("Exception_from_echo:", e)
    print(message)
