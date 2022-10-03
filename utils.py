# TODO: CQ code serialize


def cq_code_at(user_id: int) -> str:
  return "[CQ:at,qq=" + str(user_id) + "]"


def cq_code_image(file_id, url):
  return "[CQ:image,file=" + file_id + ",subType=0" + ",url=" + url + "]"