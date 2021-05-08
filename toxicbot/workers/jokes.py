import logging
import math
import time

from toxicbot import db
from toxicbot.helpers import messages
from toxicbot.features.joke import get_random_joke
from toxicbot.helpers.log import print_sleep
from toxicbot.workers.worker import WorkerInterface


class JokesWorker(WorkerInterface):
    def work(self):
        while True:
            now = time.localtime()
            now = time.mktime(now[:3] + (0, 0, 0) + now[6:])  # отбрасываем часы-минуты-секунды
            seconds = math.ceil(now + 24 * 3600 - time.time())  # прибавляем 24 часа, смотрим сколько осталось
            print_sleep(seconds, 'next midnight joke')
            time.sleep(seconds)

            with db.conn, db.conn.cursor() as cur:
                cur.execute('SELECT tg_id FROM chats WHERE tg_id < 0;')
                for record in cur:
                    logging.info('sending anek to %d', record[0])
                    anek, _ = get_random_joke()
                    messages.send(record[0], anek)

            time.sleep(2)


if __name__ == '__main__':
    text, _ = get_random_joke()
    print(text)
