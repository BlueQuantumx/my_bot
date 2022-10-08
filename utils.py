# TODO: CQ code serialize
# TODO: 扬了 CQ, 突然发现 go-cqhttp 可以返回 json 格式的消息，nnd 我为啥要在这 parse CQ


def cq_code_at(user_id: int) -> str:
  return "[CQ:at,qq=" + str(user_id) + "]"


# 只用 file_id 规避缓存问题（貌似可以？
def cq_code_image(file_id, url):
  return "[CQ:image,file=" + file_id + "]"

def cq_code_image_url(url):
  return "[CQ:image,url=" + url + "]"

def parse_cq_image(msg: str):
  msg = msg[1:-1]
  if msg[0:8] != "CQ:image":
    raise Exception("Not image!")
  arg = msg.split(',')
  return (arg[1][5:], arg[3][4:])


def parse_cq_reply(msg: str):
  msg = msg[1:-1]
  if msg[0:8] != "CQ:reply":
    raise Exception("Not reply!")
  arg = msg.split(',')
  return arg[1][3:]


def parse_cq_at(msg: str):
  msg = msg[1:-1]
  if msg[0:5] != "CQ:at":
    raise Exception("Not at!")
  arg = msg.split(',')
  return arg[1][3:]
