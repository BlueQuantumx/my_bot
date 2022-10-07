import functools
import json


class Room:

  def __init__(self, id, owner) -> None:
    self.id = id
    self.owner: Player = owner
    self.state = None
    self.player: list[Player] = [owner]
    self.survivor: list[Player] = []

  async def broadcast_to_player(self, condition, msg, websocket):
    for i in self.player:
      if condition(i):
        await websocket.send(
            json.dumps({
                "action": "send_private_msg",
                "params": {
                    "user_id": i,
                    "message": msg
                },
            }))
        await websocket.recv()

  async def broadcast_to_survivor(self, condition, msg, websocket):
    for i in self.survivor:
      if condition(i):
        await websocket.send(
            json.dumps({
                "action": "send_private_msg",
                "params": {
                    "user_id": i,
                    "message": msg
                },
            }))
        await websocket.recv()

  def check_if_ends(self):
    cnt_bad = 0
    cnt_good = 0
    for i in self.survivor:
      if i.side == "Bad":
        cnt_bad += 1
      if i.side == "Good":
        cnt_good += 1
    if cnt_good == 0:
      return "Bad"
    if cnt_bad == 0:
      return "Good"
    return "Not ends"

  async def start(self):
    self.state = "Start"
    await self.broadcast_to_player(lambda _: True, "游戏开始！当前房间号：" + self.id)
    await self.broadcast_to_player(
        lambda _: True, "本局玩家：" + functools.reduce(
            lambda x, y: x + y.nickname + "id: " + y.user_id + "\n",
            self.player, ""))
    await self.sunset()

  async def sunset(self):
    await self.broadcast_to_player(lambda _: True, "天黑请闭眼")
    pass

  async def sunrise(self):
    await self.broadcast_to_player(lambda _: True, "天亮请睁眼")
    pass


class Player:

  def __init__(self, nickname, user_id) -> None:
    self.role = None
    self.side = None  # Bad or Good
    self.nickname = nickname
    self.user_id = user_id


class Role:
  pass


class Civilian(Role):
  pass


class Wolf(Role):
  pass


class Hunter(Role):
  pass


class Prophet(Role):
  pass


running_rooms: list[Room] = []


async def open_room(message, websocket, id, owner):
  for room in running_rooms:
    if room.id == id:
      await websocket.send(
          json.dumps({
              "action": "send_private_msg",
              "params": {
                  "user_id": message["user_id"],
                  "message": "这个 id 已经被使用了，换一个吧"
              },
          }))
      await websocket.recv()
      return
  running_rooms.append(
      Room(id, Player(message["sender"]["nickname"], message["user_id"])))


async def join_room(id):
  pass


async def start_room(message, websocket, id):
  for room in running_rooms:
    if (room.id == id):
      await room.start()
      return


async def werewolf(message, websocket):
  if (message["post_type"] == "message"
      and message["message_type"] == "private"
      and message["message"][0:3] == "狼人杀"):
    args = message["message"].split()
    if (args[1] == "开房间"):
      open_room(message, websocket, args[2], message["user_id"])
    if (args[1] == "加入"):
      join_room(args[2])
    if (args[1] == "开始"):
      start_room(message, websocket, args[2])
