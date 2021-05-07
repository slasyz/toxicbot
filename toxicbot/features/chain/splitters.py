import re
from typing import List


NO_PUNCTUATION_SPLIT_REGEXP = re.compile(r"[^\w'-]+")
PUNCTUATION_SPLIT_REGEXP = re.compile(r"[\w'-]+|\s+|[^\w\s'-]+")
PUNCTUATION_FIRST_REGEXP = re.compile(r"[^\W\d]+[\w'-]*")
PUNCTUATION_LAST_REGEXP = re.compile(r".*[.!?\w]")
PUNCTUATION_SENTENCE_END_REGEXP = re.compile(r'.*[.!?]\s+$')
SPACE_ADJOIN_SPLIT_REGEXP = re.compile(r"(([^\w'-]*|\s*)[^\w\s'-]+([^\w'-]*|\s*)|[\w'-]+|[\n\t+]+)")


class Splitter:
    def split(self, message: str) -> List[str]:
        raise NotImplementedError()

    def join(self, tokens: List[str]) -> str:
        raise NotImplementedError()


class NoPunctuationSplitter(Splitter):
    def split(self, message: str) -> List[str]:
        res = NO_PUNCTUATION_SPLIT_REGEXP.split(message)
        if res == ['']:
            return []

        return res

    def join(self, tokens: List[str]) -> str:
        return ' '.join(tokens)


class PunctuationSplitter(Splitter):
    def split(self, message: str) -> List[str]:
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


class SpaceAdjoinSplitter(Splitter):
    """
    Примыкает пробелы к пунктуации, игнорирует отдельные пробелы, джойнит умнее (ставит пробел между токенами только
    когда оба не пунктуационные).
    В этом случае пробелы не являются отдельными токенами => в одно "окно" помещается больше осмысленных токенов.
    """
    def split(self, message: str) -> List[str]:
        return [x for x, y, z in SPACE_ADJOIN_SPLIT_REGEXP.findall(message)]

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

        if len(tokens) == 0:
            return ''

        if len(tokens) == 1:
            token = tokens[0]
            return token[0].upper() + token[1:]

        res = ''
        for i in range(len(tokens)-1):
            token, token_next = tokens[i], tokens[i+1]
            if res == '' or PUNCTUATION_SENTENCE_END_REGEXP.match(res) and len(token) > 0:
                token = token[0].upper() + token[1:]

            res += token

            if re.match(r"[\w'-]+", token) and re.match(r"[\w'-]+", token_next):
                res += ' '

        res += tokens[-1]
        return res.strip()
