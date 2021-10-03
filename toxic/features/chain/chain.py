import random
from typing import Tuple


FEATURE_BREAK = 0


class Chain:
    """
    Chain class learns a sequence of features to be able to predict next feature using given input.
    """
    def teach(self, feature: int):
        raise NotImplementedError()

    def predict(self, features: list[int, ...]) -> list[int]:  # TODO: replace with generator
        raise NotImplementedError()


class MarkovChain(Chain):
    """
    MarkovChain is an implementation of Markov chain algorithm.

    Example: if it is taught using sequence [1 2 3 1 2 4 1 2 3 1 2 5], then given an input [1 2] it will predict next
    feature with such probability:
      - 3 with 50%
      - 4 with 25%
      - 5 with 25%
    """
    def __init__(self, window: int):
        self.window = window
        self.data: dict[Tuple[int, ...], dict[int, int]] = {}
        self.current: Tuple[int, ...] = ()

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


class ChainFactory:
    def __init__(self, window: int):
        self.window = window

    def create(self) -> Chain:
        chain = MarkovChain(self.window)
        chain.teach(FEATURE_BREAK)
        return chain
