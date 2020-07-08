import logging
import math
import threading
import time
from urllib.request import urlopen
from lxml import html

from src import helpers, db

URL = 'https://baneks.ru/random'


def get_random_adecdote() -> str:
    with urlopen(URL) as f:
        data = f.read()
        parser = html.HTMLParser(encoding='utf-8')
        document = html.document_fromstring(data, parser=parser)
        text = document.find('.//*[@class="anek-view"]//article').text_content().strip().replace('            ', '')

    if not text.startswith('Анек #'):
        print('!!!!!!!  кривой анекдот !!!!!!!')
        print(data)
        print('!!!!!!! /кривой анекдот !!!!!!!')
        return 'Я обосрался.'

    return text


def worker():
    while True:
        t = time.localtime()
        t = time.mktime(t[:3] + (0, 0, 0) + t[6:])        # отбрасываем часы-минуты-секунды
        seconds = math.ceil(t + 24 * 3600 - time.time())  # прибавляем 24 часа, смотрим сколько осталось
        logging.info(f'sleeping {seconds} seconds before next anecdote')
        time.sleep(seconds)

        with db.conn, db.conn.cursor() as cur:
            cur.execute('SELECT tg_id FROM chats;')
            for record in cur:
                logging.info('sending anek')
                anek = get_random_adecdote()
                helpers.bot.send_message(record[0], anek)

        time.sleep(2)


def start_worker():
    threading.Thread(target=worker).start()
