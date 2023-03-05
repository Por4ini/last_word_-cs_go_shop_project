import json
from modules import cool_data
import requests


res = requests.get('https://api.steamapis.com/market/items/730?api_key=r39OfExGTYD64Bf8MGntG8oaJgQ&format=comact').text

with open('hash_name.json', 'r', encoding='utf-8') as f:
    data = f.read()
    my_list = json.loads(data)
for item in cool_data(res):
    # Перевірте, чи не міститься item[0] в data
    if item[0] not in data:
        my_list.append(item[0] + '@@@')
with open('hash_name.json', 'w',encoding='utf-8') as f:
    json.dump(my_list, f)
