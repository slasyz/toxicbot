import asyncio
import math
import random
import time
from datetime import datetime

from loguru import logger

from toxic.db import Database
from toxic.helpers.log import print_sleep
from toxic.interfaces import Worker
from toxic.messenger.messenger import Messenger
from toxic.modules.joker.content import Joker


class JokesWorker(Worker):
    def __init__(self, joker: Joker, database: Database, messenger: Messenger | None):
        self.joker = joker
        self.database = database
        self.messenger = messenger

    async def send(self, chat_id: int, joke: str):
        if self.messenger is None:
            await asyncio.sleep(1)
            return
        await self.messenger.send(chat_id, joke)

    async def step(self):
        tasks = []
        chats = await self.database.query('SELECT tg_id, joke_period FROM chats WHERE tg_id < 0 AND joke_period > 0;')

        for chat_id, period in chats:
            random_value = random.randint(1, period)
            if random_value != 1:
                logger.info('Not sending joke to chat #{} ({}/{}).', chat_id, random_value, period)
                continue

            logger.info('Sending joke to chat #{} (1/{}).', chat_id, period)
            joke, _ = await self.joker.get_random_joke()

            try:
                tasks.append(self.send(chat_id, joke))
            except Exception as ex:
                logger.opt(exception=ex).error('Cannot send joke to chat #%d.', chat_id)
                continue

        await asyncio.gather(*tasks)

    async def work(self):
        while True:
            now = time.localtime()
            now = time.mktime(now[:3] + (0, 0, 0) + now[6:])  # отбрасываем часы-минуты-секунды
            seconds = math.ceil(now + 24 * 3600 - time.time())  # прибавляем 24 часа, смотрим сколько осталось
            print_sleep(seconds, 'next midnight joke')
            await asyncio.sleep(seconds)

            await self.step()

            await asyncio.sleep(2)


async def __main__():
    import main  # pylint: disable=import-outside-toplevel
    deps = await main.init(['../../config.json'])

    jkr = Joker('ошибка')
    worker = JokesWorker(jkr, deps.database, None)

    start = datetime.now()
    await worker.step()
    logger.info('Finished joker step.', duration=str(datetime.now() - start))

    # text, _ = await Joker('ошибка').get_random_joke()
    # print(text)


if __name__ == '__main__':
    asyncio.run(__main__())
