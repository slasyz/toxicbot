import logging
import math
import re
import threading
import time
import traceback
from lxml import html

import requests

from src import db
from src.helpers import general
from src.helpers.logging import print_sleep
from src.helpers.workers import Worker

URL = 'https://baneks.ru/random'


def get_random_adecdote() -> str:
    try:
        with requests.get(URL) as r:
            data = r.content.decode('utf-8', 'ignore')
            parser = html.HTMLParser(encoding='utf-8')
            document = html.document_fromstring(data, parser=parser)
            text = document.find('.//*[@class="anek-view"]//article').text_content().strip().replace('            ', '')
    except requests.HTTPError as e:  # обрабатывать нормально
        traceback.print_stack()
        print(e)
        return 'Хуйня какая-то.'

    if not text.startswith('Анек #'):
        print('!!!!!!!  кривой анекдот !!!!!!!')
        print(data)
        print('!!!!!!! /кривой анекдот !!!!!!!')
        return 'Я обосрался.'

    text = re.sub(r'^Анек #\d+\s+', '', text)
    return text


class AnecdoteWorker(Worker):
    def work(self):
        while True:
            t = time.localtime()
            t = time.mktime(t[:3] + (0, 0, 0) + t[6:])  # отбрасываем часы-минуты-секунды
            seconds = math.ceil(t + 24 * 3600 - time.time())  # прибавляем 24 часа, смотрим сколько осталось
            print_sleep(seconds, 'next anecdote')
            time.sleep(seconds)

            with db.conn, db.conn.cursor() as cur:
                cur.execute('SELECT tg_id FROM chats WHERE tg_id < 0;')
                for record in cur:
                    logging.info(f'sending anek to {record[0]}')
                    anek = get_random_adecdote()
                    general.send_message(record[0], anek)

            time.sleep(2)


if __name__ == '__main__':
    print(get_random_adecdote())
