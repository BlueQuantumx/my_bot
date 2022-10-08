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
  with open("banned_user.json", "r") as file:
    banned_user.__init__(json.loads(file.read()))
  print("Image_Lib initialized")


@atexit.register
def destroy() -> None:
  with open("intended_user_tag.json", "w") as file:
    file.write(json.dumps(intended_users_tag))
  with open("image_tag.json", "w") as file:
    file.write(json.dumps(image_tag))
  with open("banned_user.json", "w") as file:
    file.write(json.dumps(banned_user))
  print("Image_Lib destroyed")


async def add_intended_user(message, websocket):
  if banned_user.count(message["user_id"]) != 0:
    await websocket.send(
        json.dumps({
            "action": "send_group_msg",
            "params": {
                "group_id": message["group_id"],
                "message": cq_code_at(message["user_id"]) + "你被 ban 了"
            },
        }))
    await websocket.recv()
    return
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
    await websocket.recv()
  finally:
    intended_users_tag.pop(message["user_id"])


async def send_image(message: dict, websocket):
  if banned_user.count(message["user_id"]) != 0:
    await websocket.send(
        json.dumps({
            "action": "send_group_msg",
            "params": {
                "group_id": message["group_id"],
                "message": cq_code_at(message["user_id"]) + "你被 ban 了"
            },
        }))
    await websocket.recv()
    return
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
      await websocket.recv()
    elif image_tag[user_id].get(tag) == None:
      search_res_url = search_bing(tag)
      await websocket.send(
          json.dumps({
              "action": "send_group_msg",
              "params": {
                  "group_id": message["group_id"],
                  "message": cq_code_at(message["user_id"]) + "没有这张图片哦"
              },
          }))
      await websocket.recv()
      await websocket.send(
          json.dumps({
              "action": "send_group_msg",
              "params": {
                  "group_id": message["group_id"],
                  "message": "bot 找到了相关的这张图片" + cq_code_image_url(search_res_url)
              },
          }))
      await websocket.recv()
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
      await websocket.recv()
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
    await websocket.recv()
    return

  await websocket.send(
      json.dumps({
          "action": "get_msg",
          "params": {
              "message_id": reply_id,
          },
      }))
  await websocket.recv()
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
          await websocket.recv()
        else:
          await websocket.send(
              json.dumps({
                  "action": "send_group_msg",
                  "params": {
                      "group_id": message["group_id"],
                      "message": "取消失败，请确认权限"
                  },
              }))
          await websocket.recv()
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
  await websocket.recv()
  user_msg = json.loads(await websocket.recv())["data"]
  return user_msg


async def ban_user(message, websocket):
  user_info = await get_group_member_info(message, websocket)
  if (user_info["role"] == "admin" or user_info["role"] == "owner"):
    try:
      user_id = parse_cq_at(message["message"][4:].strip())
      if banned_user.count(user_id) == 0:  # TODO
        banned_user.append(user_id)
      await websocket.send(
          json.dumps({
              "action": "send_group_msg",
              "params": {
                  "group_id": message["group_id"],
                  "message": cq_code_at(message["user_id"]) + "操作成功"
              },
          }))
      await websocket.recv()
    except:
      await websocket.send(
          json.dumps({
              "action": "send_group_msg",
              "params": {
                  "group_id": message["group_id"],
                  "message":
                  cq_code_at(message["user_id"]) + "出错力，食用方法：ban @user"
              },
          }))
      await websocket.recv()
  else:
    await websocket.send(
        json.dumps({
            "action": "send_group_msg",
            "params": {
                "group_id": message["group_id"],
                "message": cq_code_at(message["user_id"]) + "权限不足"
            },
        }))
    await websocket.recv()


async def unban_user(message, websocket):
  user_info = await get_group_member_info(message, websocket)
  if (user_info["role"] == "admin" or user_info["role"] == "owner"):
    try:
      user_id = parse_cq_at(message["message"][6:].strip())
      if banned_user.count(user_id) != 0:  # TODO
        banned_user.remove(user_id)
      await websocket.send(
          json.dumps({
              "action": "send_group_msg",
              "params": {
                  "group_id": message["group_id"],
                  "message": cq_code_at(message["user_id"]) + "操作成功"
              },
          }))
      await websocket.recv()
    except:
      await websocket.send(
          json.dumps({
              "action": "send_group_msg",
              "params": {
                  "group_id":
                  message["group_id"],
                  "message":
                  cq_code_at(message["user_id"]) + "出错力，食用方法：unban @user"
              },
          }))
      await websocket.recv()
  else:
    await websocket.send(
        json.dumps({
            "action": "send_group_msg",
            "params": {
                "group_id": message["group_id"],
                "message": cq_code_at(message["user_id"]) + "权限不足"
            },
        }))
    await websocket.recv()

def search_bing(tag: str):
  res = requests.get("https://cn.bing.com/image/search?q=" + tag)
  match_res = re.match(r'.*?<img class="mimg".*?src=(.*?)>.*?', res.text, re.S | re. M).group(1)
  url = match_res.split()[0][1:-1]
  return url


async def image_lib(message: dict, websocket):
  try:
    if (message["post_type"] == "message"
        and message["message_type"] == "group"):
      message["user_id"] = str(message["user_id"])
      if message["message"][0:7] == "收藏 tag=":
        await add_intended_user(message, websocket)
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
