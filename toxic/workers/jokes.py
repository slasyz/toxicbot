import logging
import math
import time

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

    def work(self):
        while True:
            now = time.localtime()
            now = time.mktime(now[:3] + (0, 0, 0) + now[6:])  # отбрасываем часы-минуты-секунды
            seconds = math.ceil(now + 24 * 3600 - time.time())  # прибавляем 24 часа, смотрим сколько осталось
            print_sleep(seconds, 'next midnight joke')
            time.sleep(seconds)

            for id in self.chats_repo.get_joker_chats():
                logging.info('Sending joke to chat #%d', id)
                joke, _ = self.joker.get_random_joke()

                try:
                    self.messenger.send(id, joke)
                except Exception as ex:
                    logging.error('Cannot send joke to chat #%d.', id, exc_info=ex)
                    continue

            time.sleep(2)


if __name__ == '__main__':
    text, _ = Joker('ошибка').get_random_joke()
    print(text)
