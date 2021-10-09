import random
from typing import Tuple, Optional


class Chain:
    """
    Chain class learns a sequence of features to be able to predict next feature using given input.
    """
    def teach(self, feature: int):
        raise NotImplementedError()

    def get_start(self, features: list[int, ...]) -> tuple:
        raise NotImplementedError()

    def predict(self, current: tuple) -> Optional[int]:
        raise NotImplementedError()


class MarkovChain(Chain):
    """
    MarkovChain is an implementation of Markov chain algorithm.

    Example: if it is taught using sequence [1 2 3 1 2 4 1 2 3 1 2 5], then given an input [1 2] (with window=2) it will
    predict next feature with such probability:
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
            return

        if self.current in self.data:
            if feature in self.data[self.current]:
                self.data[self.current][feature] += 1
            else:
                self.data[self.current][feature] = 1
        else:
            self.data[self.current] = {feature: 1}

        self.current = self.current[1:] + (feature,)

    def get_start(self, features: list[int, ...]) -> tuple:
        if len(features) < self.window:
            return random.choice(list(self.data.keys()))

        return tuple(features[-self.window:])

    def predict(self, current: tuple) -> Optional[int]:
        try:
            stat = self.data[current]
        except KeyError:
            print('not found {} in data'.format(current))
            return None

        word = self.pick(stat)

        return word


class ChainFactory:
    def __init__(self, window: int):
        self.window = window

    def create(self) -> Chain:
        return MarkovChain(self.window)
