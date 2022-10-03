import json

from utils import cq_code_at

intended_users_tag = {}  # {user_id: tag}
image_tag: dict = {}  # {tag: (file_id, url)}


def parse_cq_image(msg: str):
  if msg[0:9] != "[CQ:image":
    raise Exception("Not image!")
  arg = msg.split(',')
  return (arg[2][4:], arg[3][4:])


def add_intended_user(message):
  tag = message["message"][7:]
  intended_users_tag[message["user_id"]] = tag
  print(str(message["user_id"]) + " added tag: " + tag)


async def add_image_tag(message, websocket):
  try:
    image_tag[intended_users_tag[message["user_id"]]] = parse_cq_image(
        message["message"])
    print("Added image tag:", intended_users_tag[message["user_id"]])
    intended_users_tag.pop(message["user_id"])
  except Exception as e:
    print("Exception from add tag:", e)
    await websocket.send(
        json.dumps({
            "action": "send_group_msg",
            "params": {
                "group_id":
                message["group_id"],
                "message":
                cq_code_at(message["user_id"]) + "出错了，检查一下使用方式吧！\n" + "Error: "
            },
        }))


async def image_lib(message: dict, websocket):
  try:
    if (message["post_type"] == "message"
        and message["message_type"] == "group"
        and message["message"][0:7] == "收藏 tag="):
      add_intended_user(message)
    elif (message["post_type"] == "message"
          and message["message_type"] == "group"
          and intended_users_tag.get(message["user_id"]) != None):
      add_image_tag(message, websocket)
  except Exception as e:
    print("Exception_from_image_lib:", e)
