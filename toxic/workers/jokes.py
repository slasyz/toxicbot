import logging
import math
import time

from telegram.error import Unauthorized

from toxic.db import Database
from toxic.features.joke import Joker
from toxic.helpers.log import print_sleep
from toxic.messenger import Messenger
from toxic.workers.worker import Worker


class JokesWorker(Worker):
    def __init__(self, joker: Joker, database: Database, messenger: Messenger):
        self.joker = joker
        self.database = database
        self.messenger = messenger

    def work(self):
        while True:
            now = time.localtime()
            now = time.mktime(now[:3] + (0, 0, 0) + now[6:])  # отбрасываем часы-минуты-секунды
            seconds = math.ceil(now + 24 * 3600 - time.time())  # прибавляем 24 часа, смотрим сколько осталось
            print_sleep(seconds, 'next midnight joke')
            time.sleep(seconds)

            rows = self.database.query('SELECT tg_id, joke FROM chats WHERE tg_id < 0;')
            for row in rows:
                if not row[1]:
                    continue

                logging.info('Sending joke to chat #%d', row[0])
                joke, _ = self.joker.get_random_joke()

                try:
                    self.messenger.send(row[0], joke)
                except Unauthorized as ex:
                    logging.info('Cannot send joke to chat #%d', row[0], exc_info=ex)
                    continue

            time.sleep(2)


if __name__ == '__main__':
    text, _ = Joker('ошибка').get_random_joke()
    print(text)
