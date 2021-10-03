from typing import Optional

from toxic.features.chain.chain import Chain
from toxic.features.chain.featurizer import Featurizer
from toxic.features.chain.splitters import Splitter
from toxic.helpers.consts import LINK_REGEXP
from toxic.metrics import Metrics


class Textizer:
    """
    Textizer is a text prediction class.  It splits text to tokens using Splitter, maps them with integer features'
    IDs using Featurizer, and uses chain to predict next tokens in a sequence.

    It also preprocesses text and has some workarounds to make text more clean.
    """
    def __init__(self, featurizer: Featurizer, splitter: Splitter, metrics: Metrics):
        self.featurizer = featurizer
        self.splitter = splitter
        self.metrics = metrics

    def teach(self, chain: Chain, message: Optional[str]):
        if message is None or message == '':
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

    def predict(self, chain: Chain, message: Optional[str] = None) -> str:
        if message is None:
            message = ''

        src_words = self.splitter.split(message)

        src_features = []
        for word in src_words:
            feature = self.featurizer.get_feature(word)
            src_features.append(feature)

        result_features = chain.predict(src_features)

        result_words = []
        for feature in result_features:
            result_words.append(self.featurizer.get_value(feature))

        result_message = self.splitter.join(result_words)
        if result_message != '':
            return result_message[0].upper() + result_message[1:]

        return ''

    def _predict_not_empty_inner(self, chain: Chain, message: str = None):
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
