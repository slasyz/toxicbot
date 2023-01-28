from toxic.modules.neural.chains.chain import Chain
from toxic.modules.neural.chains.featurizer import Featurizer, FEATURE_NONE
from toxic.modules.neural.chains.splitters import Splitter
from toxic.helpers.consts import LINK_REGEXP
from toxic.metrics import Metrics


class Textizer:
    """
    Textizer is a text prediction class.  It splits text to tokens using Splitter, maps them with integer features'
    IDs using Featurizer, and uses chain to predict next tokens in a sequence.

    It also preprocesses text and has some workarounds to make text more clean.

    TODO: написать тесты для этого и других классов.  Зря что ли декомпозировал?
    """

    def __init__(self, featurizer: Featurizer, splitter: Splitter, metrics: Metrics):
        self.featurizer = featurizer
        self.splitter = splitter
        self.metrics = metrics

    def teach(self, chain: Chain, message: str):
        if message == '':
            return

        message = LINK_REGEXP.sub('', message)
        words = self.splitter.split(message)
        for word in words:
            if word == '':  # TODO: [картинка]
                continue

            feature = self.featurizer.get_feature(word.lower())
            chain.teach(feature)

        feature = self.featurizer.get_feature(None)
        chain.teach(feature)

    def predict(self, chain: Chain, message: str | None = None) -> str:
        if message is None:
            message = ''

        src_words = self.splitter.split(message)

        src_features = []
        for word in src_words:
            feature = self.featurizer.get_feature(word)
            src_features.append(feature)

        current = chain.get_start(src_features)
        result_features = []

        while True:
            feature_or_none = chain.predict(current)
            if feature_or_none is None or feature_or_none == FEATURE_NONE:
                break
            result_features.append(feature_or_none)
            current = current[1:] + (feature_or_none,)

        result_words = []
        for feature in result_features:
            word_or_none = self.featurizer.get_value(feature)
            if word_or_none is None:  # impossible, but let's check to please linter
                break
            if '\n' in word_or_none:
                break
            result_words.append(word_or_none)

        result_message = self.splitter.join(result_words)
        if result_message != '':
            return result_message[0].upper() + result_message[1:]

        return ''

    def _predict_not_empty_inner(self, chain: Chain, message: str = None):
        # TODO: исправить этот костыль, или для начала добавить метрики на плохие предсказания
        for _ in range(10):
            res = self.predict(chain, message)
            if res != '':
                return res

        for _ in range(100):
            res = self.predict(chain)
            if res != '':
                return res

        return 'Не могу сказать ничего дельного.'

    def predict_not_empty(self, chain: Chain, message: str = None) -> str:
        with self.metrics.chain_predict.time():  # TODO: do with decorator
            return self._predict_not_empty_inner(chain, message)
