import asyncio
import math
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

            for id in self.chats_repo.get_joker_chats():
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
