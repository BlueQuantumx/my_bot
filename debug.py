message_ex_filter = ["meta_event"]


async def debug_print(message: dict, websocket):
  if (message.get("post_type") != None):
    if (message_ex_filter.count(message["post_type"]) == 0):
      print("")
      print(message)
      print("")