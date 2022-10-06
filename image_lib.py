import json
import atexit
from utils import cq_code_at, cq_code_image, parse_cq_image

intended_users_tag = {}  # {user_id: tag}
image_tag: dict = {}  # {user_id: {tag: (file_id, url)}}


def init() -> None:
  with open("intended_user_tag.json", "r") as file:
    intended_users_tag.__init__(json.loads(file.read()))
  with open("image_tag.json", "r") as file:
    image_tag.__init__(json.loads(file.read()))
  print("Image_Lib initialized")


@atexit.register
def destroy() -> None:
  with open("intended_user_tag.json", "w") as file:
    file.write(json.dumps(intended_users_tag))
  with open("image_tag.json", "w") as file:
    file.write(json.dumps(image_tag))
  print("Image_Lib destroyed")


def add_intended_user(message):
  tag = message["message"][7:]
  intended_users_tag[message["user_id"]] = tag
  print(str(message["user_id"]) + " added tag: " + tag)


async def add_image_tag(message, websocket):
  try:
    if image_tag.get(message["user_id"]) == None:
      image_tag[message["user_id"]] = {}
    image_tag[message["user_id"]][intended_users_tag[
        message["user_id"]]] = parse_cq_image(message["message"])
    print("Added image tag:", intended_users_tag[message["user_id"]])
  except Exception as e:
    print("Exception from add tag:", e)
    await websocket.send(
        json.dumps({
            "action": "send_group_msg",
            "params": {
                "group_id": message["group_id"],
                "message": cq_code_at(message["user_id"]) + "出错了，检查一下使用方式吧！\n"
            },
        }))
  finally:
    intended_users_tag.pop(message["user_id"])


async def send_image(message: dict, websocket):
  try:
    tag = message["message"][2:]
    user_id = message["user_id"]
    if image_tag.get(user_id) == None:
      await websocket.send(
          json.dumps({
              "action": "send_group_msg",
              "params": {
                  "group_id": message["group_id"],
                  "message": cq_code_at(user_id) + "你还没有收藏过图片哦"
              },
          }))
    elif image_tag[user_id][tag] == None:
      await websocket.send(
          json.dumps({
              "action": "send_group_msg",
              "params": {
                  "group_id": message["group_id"],
                  "message": cq_code_at(message["user_id"]) + "没有这张图片哦"
              },
          }))
    else:
      file_id, url = image_tag[user_id][tag]
      await websocket.send(
          json.dumps({
              "action": "send_group_msg",
              "params": {
                  "group_id": message["group_id"],
                  "message": cq_code_image(file_id, url)
              },
          }))
  except Exception as e:
    print("Exception_from_send_image:", e)


async def image_lib(message: dict, websocket):
  try:
    if (message["post_type"] == "message"
        and message["message_type"] == "group"):
      message["user_id"] = str(message["user_id"])
      if message["message"][0:7] == "收藏 tag=":
        add_intended_user(message)
      elif intended_users_tag.get(message["user_id"]) != None:
        await add_image_tag(message, websocket)
      elif message["message"][0:2] == "发 ":
        await send_image(message, websocket)

  except Exception as e:
    print("Exception_from_image_lib:", e)
