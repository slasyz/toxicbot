import random
from typing import Optional

from src.features.chain.splitters import Splitter
from src.helpers.general import LINK_REGEXP

BREAK = '[BREAK]'


class Chain:
    def __init__(self, window: int, splitter: Splitter):
        self.window = window
        self.splitter = splitter
        self.data = {}
        self.current = ()

        self.teach_word(BREAK)

    @staticmethod
    def pick(stat: dict) -> str:
        res = []
        for key, value in stat.items():
            res += [key] * value

        return random.choice(res)

    def teach_word(self, word: str):
        if len(self.current) < self.window:
            self.current = self.current + (word,)
        elif self.current[-1] != BREAK or word != BREAK:
            if self.current in self.data:
                if word in self.data[self.current]:
                    self.data[self.current][word] += 1
                else:
                    self.data[self.current][word] = 1
            else:
                self.data[self.current] = {word: 1}

            self.current = self.current[1:] + (word,)

    def teach_message(self, message: Optional[str]):
        if message is None or message == '':
            return

        message = LINK_REGEXP.sub('', message)
        words = self.splitter.split(message)
        for word in words:
            if word != '':  # TODO: [картинка]
                self.teach_word(word.lower())
        self.teach_word(BREAK)

    def _predict(self, message: str = None) -> str:
        if self.window == 1:
            current = (BREAK,)
        else:
            if message is None:
                current = random.choice(list(self.data.keys()))
            else:
                arr = self.splitter.split(message)
                if len(arr) < self.window - 1:
                    current = random.choice(list(self.data.keys()))
                else:
                    current = tuple(arr[-self.window+1:]) + (BREAK,)

        result = []
        while True:
            try:
                stat = self.data[current]
            except KeyError:
                break

            word = self.pick(stat)
            current = current[1:] + (word,)

            if word == BREAK:
                break

            result.append(word)

        res = self.splitter.join(result)
        if res != '':
            return res[0].upper() + res[1:]

        return ''

    def predict_not_empty(self, message: str = None):
        for _ in range(10):
            res = self._predict(message)
            if res != '':
                return res

        for _ in range(100):
            res = self._predict()
            if res != '':
                return res

        return 'Не могу сказать ничего дельного.'
