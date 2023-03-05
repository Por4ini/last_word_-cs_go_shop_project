from datetime import datetime
import requests
from modules import good_str, date


def get_data(connection, key, list_names):
    global tmid_list
    tmid_list = []
    cursor = connection.cursor()
    on_sale = f"https://market.csgo.com/api/v2/search-list-items-by-hash-name-all?key={key}{list_names}"
    history = f"https://market.csgo.com/api/v2/get-list-items-info?key={key}{list_names}"

    cursor.execute('''
                                     CREATE TABLE IF NOT EXISTS history (
                                         id BIGINT PRIMARY KEY,
                                         time DATETIME,
                                         price TEXT,
                                         status TEXT,
                                         market_hash_name_id TEXT,
                                         classid_instanceid TEXT,
                                         tmid BIGINT,
                                         asset TEXT
                                     )
                                 ''')

    cursor.execute('''
                                     CREATE TABLE IF NOT EXISTS on_sale (
                                         tmid BIGINT PRIMARY KEY,
                                         asset TEXT,
                                         price TEXT,
                                         time DATETIME,
                                         status TEXT,
                                         market_hash_name_id TEXT,
                                         classid_instanceid TEXT
                                     )
                                 ''')
    connection.commit()
    try:
        on_sale_data = requests.get(on_sale).json()

        on_sale_values = []
        if on_sale_data['data']:
            for name, items in on_sale_data['data'].items():
                for item in items:
                    tmid = int(item['id'])
                    asset = item.get('extra', {}).get('asset', '')
                    price = str(float(item['price'].split(',')[0]) / 100)
                    classid_instanceid = good_str(item['class'], item['instance'])
                    on_sale_values.append((tmid, asset, price, date, 'on_sale', name, classid_instanceid))

        if on_sale_values:
            cursor.executemany(f'''
                                                   INSERT INTO on_sale (
                                                       tmid,
                                                       asset,
                                                       price,
                                                       time,
                                                       status,
                                                       market_hash_name_id,
                                                       classid_instanceid
                                                   ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                                                   ON DUPLICATE KEY UPDATE
                                                       asset=VALUES(asset),
                                                       price=VALUES(price),
                                                       time=VALUES(time)
                                               ''', on_sale_values)
    except Exception as e:
        print(f'Посилка {e} при запиті до on _sale: \n {on_sale}')
    try:
        history_data = requests.get(history).json()

        history_values = []
        if history_data['data']:
            for name, history_items in history_data['data'].items():
                for item in history_items['history']:
                    time = datetime.fromtimestamp(item[0]).strftime('%Y-%m-%d %H:%M:%S')
                    id = str(item[1] + item[0] + len(name)).replace('.', '')
                    history_values.append((int(id), time, str(item[1]), 'need_check', name, '', 0, ''))
        if history_values:
            cursor.executemany('''
                                                   INSERT IGNORE INTO history (
                                                       id,
                                                   time,
                                                   price,
                                                   status,
                                                   market_hash_name_id,
                                                   classid_instanceid,
                                                   tmid,
                                                   asset
                                               ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                           ''', history_values)
    except Exception as e:
        print(f'Помилка {e} при запиті до history: {history}')

    connection.commit()
