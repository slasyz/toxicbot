import logging
import math
import time

from toxicbot.db import Database
from toxicbot.features.joke import Joker
from toxicbot.helpers.log import print_sleep
from toxicbot.helpers.messages import Bot
from toxicbot.workers.worker import Worker


class JokesWorker(Worker):
    def __init__(self, joker: Joker, database: Database, bot: Bot):
        self.joker = joker
        self.database = database
        self.bot = bot

    def work(self):
        while True:
            now = time.localtime()
            now = time.mktime(now[:3] + (0, 0, 0) + now[6:])  # отбрасываем часы-минуты-секунды
            seconds = math.ceil(now + 24 * 3600 - time.time())  # прибавляем 24 часа, смотрим сколько осталось
            print_sleep(seconds, 'next midnight joke')
            time.sleep(seconds)

            rows = self.database.query('SELECT tg_id FROM chats WHERE tg_id < 0;')
            for row in rows:
                logging.info('sending joke to %d', row[0])
                joke, _ = self.joker.get_random_joke()
                self.bot.send(row[0], joke)

            time.sleep(2)


if __name__ == '__main__':
    text, _ = Joker('ошибка').get_random_joke()
    print(text)
