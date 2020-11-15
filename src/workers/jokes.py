import logging
import math
import time

from src import db
from src.helpers import general
from src.features.joke import get_random_joke
from src.helpers.logging import print_sleep
from src.workers.worker import Worker


class JokesWorker(Worker):
    def work(self):
        while True:
            t = time.localtime()
            t = time.mktime(t[:3] + (0, 0, 0) + t[6:])  # отбрасываем часы-минуты-секунды
            seconds = math.ceil(t + 24 * 3600 - time.time())  # прибавляем 24 часа, смотрим сколько осталось
            print_sleep(seconds, 'next midnight joke')
            time.sleep(seconds)

            with db.conn, db.conn.cursor() as cur:
                cur.execute('SELECT tg_id FROM chats WHERE tg_id < 0;')
                for record in cur:
                    logging.info('sending anek to %d', record[0])
                    anek = get_random_joke()
                    general.send(record[0], anek)

            time.sleep(2)


if __name__ == '__main__':
    print(get_random_joke())