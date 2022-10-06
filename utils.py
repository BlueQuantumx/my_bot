# TODO: CQ code serialize


def cq_code_at(user_id: int) -> str:
  return "[CQ:at,qq=" + str(user_id) + "]"


def cq_code_image(file_id, url):
  return "[CQ:image,file=" + file_id + ",subType=0" + ",url=" + url + "]"


def parse_cq_image(msg: str):
  msg = msg[1:-1]
  if msg[0:8] != "CQ:image":
    raise Exception("Not image!")
  arg = msg.split(',')
  return (arg[1][5:], arg[3][4:])
