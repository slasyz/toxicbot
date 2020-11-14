import re
from typing import List


class Splitter:
    def split_tokens(self, message: str) -> List[str]:
        raise NotImplementedError()


class NoPunctuationSplitter(Splitter):
    def split_tokens(self, message: str) -> object:
        return re.split(r"[^\w'-]+", message)


class PunctuationSplitter(Splitter):
    def split_tokens(self, message: str) -> object:
        return re.findall(r"[\w'-]+|\s+|[^\w\s'-]+", message)
