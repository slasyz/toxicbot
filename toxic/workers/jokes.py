import asyncio
import math
import random
import time

from loguru import logger

from toxic.features.joke import Joker
from toxic.helpers.log import print_sleep
from toxic.messenger.messenger import Messenger
from toxic.repositories.chats import ChatsRepository
from toxic.workers.worker import Worker


class JokesWorker(Worker):
    def __init__(self, joker: Joker, chats_repo: ChatsRepository, messenger: Messenger):
        self.joker = joker
        self.chats_repo = chats_repo
        self.messenger = messenger

    async def work(self):
        while True:
            now = time.localtime()
            now = time.mktime(now[:3] + (0, 0, 0) + now[6:])  # отбрасываем часы-минуты-секунды
            seconds = math.ceil(now + 24 * 3600 - time.time())  # прибавляем 24 часа, смотрим сколько осталось
            print_sleep(seconds, 'next midnight joke')
            await asyncio.sleep(seconds)

            for id, period in self.chats_repo.get_joker_chats():
                random_value = random.randint(1, period)
                if random_value != 1:
                    logger.info('Not sending joke to chat #{} (#{}/#{}).', id, random_value, period)
                    continue

                logger.info('Sending joke to chat #{}.', id)
                joke, _ = self.joker.get_random_joke()

                try:
                    await self.messenger.send(id, joke)
                except Exception as ex:
                    logger.opt(exception=ex).error('Cannot send joke to chat #%d.', id)
                    continue

            await asyncio.sleep(2)


if __name__ == '__main__':
    text, _ = Joker('ошибка').get_random_joke()
    print(text)
