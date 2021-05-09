import random
from typing import Optional, Tuple

from toxicbot.features.chain.splitters import Splitter
from toxicbot.helpers.general import LINK_REGEXP


FEATURE_BREAK = 0

# TODO: Chain -> Textizer, Machine -> Chain


class Machine:
    def teach(self, feature: int):
        pass

    def predict(self, features: list[int, ...]) -> list[int]:
        pass


class Markov(Machine):
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


class Featurizer:
    def __init__(self):
        self.features: dict[str, int] = {}
        self.values: dict[int, str] = {}

    def get_feature(self, value: Optional[str]) -> int:
        if value is None:
            return FEATURE_BREAK

        try:
            return self.features[value]
        except KeyError:
            n = len(self.features) + 1
            self.features[value] = n
            self.values[n] = value
            return n

    def get_value(self, feature: int) -> Optional[str]:
        if feature == FEATURE_BREAK:
            return None

        return self.values[feature]


class Chain:
    def __init__(self, featurizer: Featurizer, splitter: Splitter):
        self.featurizer = featurizer
        self.splitter = splitter

    def teach(self, machine: Machine, message: Optional[str]):
        if message is None or message == '':
            return

        message = LINK_REGEXP.sub('', message)
        words = self.splitter.split(message)
        for word in words:
            if word == '':  # TODO: [картинка]
                continue

            feature = self.featurizer.get_feature(word.lower())
            machine.teach(feature)

        feature = self.featurizer.get_feature(None)
        machine.teach(feature)

    def predict(self, machine: Machine, message: Optional[str] = None) -> str:
        if message is None:
            message = ''

        src_words = self.splitter.split(message)

        src_features = []
        for word in src_words:
            feature = self.featurizer.get_feature(word)
            src_features.append(feature)

        result_features = machine.predict(src_features)

        result_words = []
        for feature in result_features:
            result_words.append(self.featurizer.get_value(feature))

        result_message = self.splitter.join(result_words)
        if result_message != '':
            return result_message[0].upper() + result_message[1:]

        return ''

    def predict_not_empty(self, machine: Machine, message: str = None):
        for _ in range(10):
            res = self.predict(machine, message)
            if res != '':
                return res

        for _ in range(100):
            res = self.predict(machine)
            if res != '':
                return res

        return 'Не могу сказать ничего дельного.'
