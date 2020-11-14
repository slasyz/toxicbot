import re
import random
from typing import Union

from src.services.chain.splitters import Splitter

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
        if len(self.current) == self.window and (self.current[-1] != BREAK or word != BREAK):
            if self.current in self.data:
                if word in self.data[self.current]:
                    self.data[self.current][word] += 1
                else:
                    self.data[self.current][word] = 1
            else:
                self.data[self.current] = {word: 1}

        self.current = self.current[1:] + (word,)

    def teach_message(self, message: Union[str, type(None)]):
        if message is None or message == '':
            return

        regex = r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))'
        message = re.sub(regex, '', message)
        words = self.splitter.split_tokens(message)
        for word in words:
            if word != '':  # TODO: [картинка]
                self.teach_word(word.lower())
        self.teach_word(BREAK)

    def predict(self, message: str) -> str:
        if self.window == 1:
            current = (BREAK,)
        else:
            arr = re.split(r'[^\w]+', message)  # TODO: если нет достаточного числа слов
            current = tuple(arr[-self.window+1:]) + (BREAK,)

        result = []
        while True:
            try:
                stat = self.data[current]
            except KeyError:
                break

            word = self.pick(stat)
            current = (word,)

            if current == (BREAK,):
                break

            result.append(word)

        res = ' '.join(result)
        if res != '':
            return res[0].upper() + res[1:]

        return ''
