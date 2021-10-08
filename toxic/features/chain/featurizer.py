from typing import Optional


FEATURE_NONE = 0


class Featurizer:
    """
    Featurizer class maps a string with its unique ID.

    None value can be passed instead of a string.  It can be used to encode something outside of set of all possible
    words.  For example, in case of chat bot it's the end of the message.
    """
    def __init__(self):
        self.features: dict[str, int] = {}
        self.values: dict[int, str] = {}

    def get_feature(self, value: Optional[str]) -> int:
        if value is None:
            return FEATURE_NONE

        try:
            return self.features[value]
        except KeyError:
            next_feature_num = len(self.features) + 1
            self.features[value] = next_feature_num
            self.values[next_feature_num] = value
            return next_feature_num

    def get_value(self, feature: int) -> Optional[str]:
        if feature == FEATURE_NONE:
            return None

        return self.values[feature]
