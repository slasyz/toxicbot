import re
from typing import List


NO_PUNCTUATION_SPLIT_REGEXP = re.compile(r"[^\w'-]+")
PUNCTUATION_SPLIT_REGEXP = re.compile(r"[\w'-]+|\s+|[^\w\s'-]+")
PUNCTUATION_FIRST_REGEXP = re.compile(r"[^\W\d]+[\w'-]*")
PUNCTUATION_LAST_REGEXP = re.compile(r".*[.!?\w]")
PUNCTUATION_SENTENCE_END_REGEXP = re.compile(r'.*[.!?]\s+$')


class Splitter:
    def split(self, message: str) -> List[str]:
        raise NotImplementedError()

    def join(self, tokens: List[str]) -> str:
        raise NotImplementedError()


class NoPunctuationSplitter(Splitter):
    def split(self, message: str) -> object:
        res = NO_PUNCTUATION_SPLIT_REGEXP.split(message)
        if res == ['']:
            return []

        return res

    def join(self, tokens: List[str]) -> str:
        return ' '.join(tokens)


class PunctuationSplitter(Splitter):
    def split(self, message: str) -> object:
        return PUNCTUATION_SPLIT_REGEXP.findall(message)

    def join(self, tokens: List[str]) -> str:
        first_non_punctuation = next(
            (i for i, token in enumerate(tokens) if PUNCTUATION_FIRST_REGEXP.match(token)),
            len(tokens)
        )
        last_allowed = next(
            (i for i, token in enumerate(reversed(tokens)) if PUNCTUATION_LAST_REGEXP.match(token)),
            len(tokens)
        )
        tokens = tokens[first_non_punctuation:len(tokens)-last_allowed]

        res = ''
        for token in tokens:
            if res == '' or PUNCTUATION_SENTENCE_END_REGEXP.match(res) and len(token) > 0:
                token = token[0].upper() + token[1:]
            res += token

        return res.strip()


# TODO: примыкать пробелы к пунктуации, игнорировать отдельные пробелы, джойнить умнее
#       (ставить пробел между токенами только когда оба не пунктуационные).
#       В этом случае пробелы не будут отдельными токенами => в одно "окно" будет помещаться больше осмысленных токенов.
# class PunctuationSplitter(Splitter):
#     def split(self, message: str) -> object:
#         pass
#
#     def join(self, tokens: List[str]) -> str:
#         pass
