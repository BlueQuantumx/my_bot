import json
import atexit
from utils import cq_code_at, cq_code_image, parse_cq_at, parse_cq_image, parse_cq_reply

intended_users_tag = {}  # {user_id: tag}
banned_user = []
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
    elif image_tag[user_id].get(tag) == None:
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


async def cancel_collection(message: dict, websocket):
  try:
    reply_id = parse_cq_reply('[' + message["message"].split('[')[1])
  except:
    await websocket.send(
        json.dumps({
            "action": "send_group_msg",
            "params": {
                "group_id": message["group_id"],
                "message": "请选择图片"
            },
        }))
    return

  await websocket.send(
      json.dumps({
          "action": "get_msg",
          "params": {
              "message_id": reply_id,
          },
      }))
  reply_msg = json.loads(await websocket.recv())["data"]
  (file, _) = parse_cq_image(reply_msg["message"])
  for (uid, tags) in image_tag.items():
    for (tag, val) in tags.items():
      if (val[0] == file):
        user_msg = await get_group_member_info(message, websocket)
        if user_msg["role"] == "admin" or user_msg[
            "role"] == "owner" or uid == message["user_id"]:
          tags.pop(tag)
          await websocket.send(
              json.dumps({
                  "action": "send_group_msg",
                  "params": {
                      "group_id": message["group_id"],
                      "message": "取消成功"
                  },
              }))
        else:
          await websocket.send(
              json.dumps({
                  "action": "send_group_msg",
                  "params": {
                      "group_id": message["group_id"],
                      "message": "取消失败，请确认权限"
                  },
              }))
        return


async def get_group_member_info(message, websocket):
  await websocket.send(
      json.dumps({
          "action": "get_group_member_info",
          "params": {
              "group_id": message["group_id"],
              "user_id": message["user_id"],
          },
      }))
  user_msg = json.loads(await websocket.recv())["data"]
  return user_msg


async def ban_user(message, websocket):
  user_info = await get_group_member_info(message, websocket)
  if (user_info["role"] == "admin" or user_info["role"] == "owner"):
    try:
      user_id = parse_cq_at(message["message"][4:])
      if banned_user.count(user_id) == 0:  # TODO
        banned_user.append(user_id)
    except:
      websocket.send(
          json.dumps({
              "action": "send_group_msg",
              "params": {
                  "group_id": message["group_id"],
                  "message":
                  cq_code_at(message["user_id"]) + "出错力，食用方法：ban @user"
              },
          }))
  else:
    websocket.send(
        json.dumps({
            "action": "send_group_msg",
            "params": {
                "group_id": message["group_id"],
                "message": cq_code_at(message["user_id"]) + "还要向上爬才能 ban 别人哦"
            },
        }))


async def unban_user(message, websocket):
  user_info = await get_group_member_info(message, websocket)
  if (user_info["role"] == "admin" or user_info["role"] == "owner"):
    try:
      user_id = parse_cq_at(message["message"][6:])
      if banned_user.count(user_id) != 0:  # TODO
        banned_user.pop(user_id)
    except:
      websocket.send(
          json.dumps({
              "action": "send_group_msg",
              "params": {
                  "group_id":
                  message["group_id"],
                  "message":
                  cq_code_at(message["user_id"]) + "出错力，食用方法：unban @user"
              },
          }))
  else:
    websocket.send(
        json.dumps({
            "action": "send_group_msg",
            "params": {
                "group_id": message["group_id"],
                "message": cq_code_at(message["user_id"]) + "还要向上爬才能 unban 别人哦"
            },
        }))


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
      elif message["message"][-4:] == "取消收藏":
        await cancel_collection(message, websocket)
      elif message["message"][0:3] == "ban":
        await ban_user(message, websocket)
      elif message["message"][0:5] == "unban":
        await unban_user(message, websocket)

  except Exception as e:
    print("Exception_from_image_lib:", e)
