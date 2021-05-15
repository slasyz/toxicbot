from typing import Optional

from toxicbot.features.chain.chain import FEATURE_BREAK


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
            next_feature_num = len(self.features) + 1
            self.features[value] = next_feature_num
            self.values[next_feature_num] = value
            return next_feature_num

    def get_value(self, feature: int) -> Optional[str]:
        if feature == FEATURE_BREAK:
            return None

        return self.values[feature]
