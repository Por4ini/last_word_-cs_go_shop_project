import pytz
from datetime import timedelta, datetime


tz_ukraine = pytz.timezone("Europe/Uzhgorod")
now = (str(datetime.now(tz_ukraine)).split('.')[0])
date = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
target_time = date - timedelta(hours=1)
tmid_list = []

def cool_data(res):
    res = res.replace('{', '')
    res = res.replace('}', '')
    res = res.split(',"')
    list = []
    for item in res:
        item = item.replace('"', '')
        list.append(item.rsplit(':', maxsplit=1))
    return list

def item_split(item):
    item = item.replace('[', '')
    item = item.replace(']', '')
    item = (item.split(',', maxsplit=1)[-1]).replace('"', '')
    if len(item) > 0 and item[0] == ' ':
        item = item[1:]

    return item


def good_str(a, b):
    string = str(a) + '_' + str(b)
    return string


# Беремо 50 хешей зі спіску та створюємо частинку запиту
def get_50(all_names):
    count = 0
    list = []
    for name in all_names:
        count += 1
        list.append(f'&list_hash_name[]={name}')
        all_names.remove(name)
        if count >= 50:
            break
    return ''.join(list)

def get_50_tmid(all_names):
    count = 0
    list = []
    for name in all_names:
        count += 1
        list.append(f'&list_hash_name[]={name}')
        if count >= 50:
            break
    return ''.join(list)
