import random
from typing import Tuple


FEATURE_BREAK = 0


class Chain:
    def teach(self, feature: int):
        pass

    def predict(self, features: list[int, ...]) -> list[int]:
        pass


class MarkovChain(Chain):
    def __init__(self, window: int):
        self.window = window
        self.data: dict[Tuple[int, ...], dict[int, int]] = {}
        self.current: Tuple[int, ...] = ()

        self.teach(FEATURE_BREAK)

    @staticmethod
    def pick(stat: dict[int, int]) -> int:
        res: list[int] = []
        for key, value in stat.items():
            res += [key] * value

        return random.choice(res)

    def teach(self, feature: int):
        if len(self.current) < self.window:
            self.current = self.current + (feature,)
        elif self.current[-1] != FEATURE_BREAK or feature != FEATURE_BREAK:
            if self.current in self.data:
                if feature in self.data[self.current]:
                    self.data[self.current][feature] += 1
                else:
                    self.data[self.current][feature] = 1
            else:
                self.data[self.current] = {feature: 1}

            self.current = self.current[1:] + (feature,)

    def predict(self, features: list[int, ...]) -> list[int]:
        if self.window == 1:
            current = (FEATURE_BREAK,)
        else:
            if len(features) == 0:
                current = random.choice(list(self.data.keys()))
            else:
                if len(features) < self.window - 1:
                    current = random.choice(list(self.data.keys()))
                else:
                    current = tuple(features[-self.window+1:]) + (FEATURE_BREAK,)

        result = []
        while True:
            try:
                stat = self.data[current]
            except KeyError:
                break

            word = self.pick(stat)
            current = current[1:] + (word,)

            if word == FEATURE_BREAK:
                break

            result.append(word)

        return result
