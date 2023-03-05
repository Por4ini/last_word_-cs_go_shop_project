import multiprocessing
import mysql.connector
from get_data import get_data
from modules import item_split, get_50, target_time, date, get_50_tmid
import requests


def process_data(config, key, list_names):
    connection = mysql.connector.connect(**config)
    get_data(connection, key, list_names)
    connection.close()


if __name__ == '__main__':
    config = {
        'user': 'root',
        'password': 'Itred1984',
        'host': 'localhost',
        'database': 'items',
        'port': 3707,
    }
    tmid_list = []
    names = []
    keys = ['vCkVaFAV7rrFGOX5xTE6zsu27t36g9N', '4DsygAaKoCRDAs2jX9o3Gcx68gq34oX', 'vXJ7sFz4nsuc7fT81RNqIkrj7y06m14',
            'UAYvjQAX5U7Lu0GjHcovE3f5Yf8lsEA', '00Evwqok5v459W3CsG1uwBnOV7vG7I6', 'yREZeeZN2pZAKnhDKEUi2gtY5xxtDoU',
            'NDJSqIbxf0zCNE9yYSh35iHHxxMFzz7', '1KAEe664V41vorlgd6kG9hx17g5y6F0', 'w522SCV09kFqLyH02RCRK18kbauVhCL',
            'jwqZ69qF3UMfcfRdyj3cBpqT403WZ36']
    with open('hash_name.json', 'r', encoding='utf-8') as f:
        # Зчитайте вміст файлу як рядок
        data = f.read()
    while True:

        if len(names) != 0:
            processes = []
            for key in keys:
                print(len(names))
                on_sale = f"https://market.csgo.com/api/v2/search-list-items-by-hash-name-all?key={key}{get_50_tmid(names)}"
                try:
                    on_sale_data = requests.get(on_sale).json()
                    if on_sale_data['data']:
                        for name, items in on_sale_data['data'].items():
                            for item in items:
                                tmid_list.append(item['id'])
                except Exception as e:
                    print(f'Ця помилка {e} для цього запиту: \n {on_sale} ')
                p = multiprocessing.Process(target=process_data, args=(config, key, get_50(names)))
                processes.append(p)
                p.start()
            for p in processes:
                p.join()

        if len(names) <= 1:
            for item in data.split('@@@'):
                names.append(item_split(item))
            print('Перший збір')
            print(date)

        elif len(names) >= 1 and len(names) <= 499:
            for item in data.split('@@@'):
                names.append(item_split(item))
            print('Другий збір')
            connection = mysql.connector.connect(**config)
            cursor = connection.cursor()
            print(len(tmid_list))
            try:
                cursor.execute(
                    "UPDATE on_sale SET status = 'on_sale' WHERE status = 'not_found' AND tmid IN (%s)" % ",".join(
                        str(i) for i in tmid_list))
            except Exception as e:
                print(f'Помилка при спробі поміняти not_found в таблиці on_sale на on_sale\n{e}')
            try:
                cursor.execute(
                    "UPDATE on_sale SET status = 'need_check' WHERE status = 'on_sale' AND tmid NOT IN (%s)" % ",".join(
                        str(i) for i in tmid_list))
                print('1')
            except Exception as e:
                print(f'Помилка при спробі поміняти on_sale в таблиці need_check на on_sale\n{e}')
            try:
                cursor.execute(f'''
                                        UPDATE on_sale SET status = 'not_found'
                                        WHERE status = 'need_check' AND time < '{target_time}'
                                        ''')
                print('2')
            except Exception as e:
                print(
                    f'Помилка при спробі присвоїта статус not_found улементу зі статусом need_check в таблиці on_sale\n{e}')

            try:
                cursor.execute(f'''
                                UPDATE history SET status = 'not_found'
                                WHERE status = 'need_check' AND time < '{target_time}'
                                ''')
                print('3')
            except Exception as e:
                print(
                    f'Помилка при спробі присвоїта статус not_found улементу зі статусом need_check в таблиці history\n{e}')
            connection.commit()
            print('4')
            try:
                cursor.execute("""
                                                      UPDATE history h
                                                      JOIN on_sale s
                                                      ON h.market_hash_name_id = s.market_hash_name_id
                                                      AND h.status = 'need_check'
                                                      AND s.status = 'need_check'
                                                      AND h.price = s.price
                                                      SET h.classid_instanceid = s.classid_instanceid,
                                                          h.asset = s.asset,
                                                          h.tmid = s.tmid,
                                                          h.status = 'found',
                                                          s.status = 'found'
                                                  """)
            except Exception as e:
                print(f'Помилка присвоєння found : {e}')
            connection.commit()
            connection.close()
            tmid_list.clear()
            print(date)
