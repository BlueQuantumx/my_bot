from json import dump, loads
import requests

url = "http://localhost:5700"

res = loads(requests.get(url + "/get_friend_list").text)["data"]
for i in res:
  print(i["nickname"], i["user_id"])
