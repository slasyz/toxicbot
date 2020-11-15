import re
from typing import List


class Splitter:
    def split(self, message: str) -> List[str]:
        raise NotImplementedError()

    def join(self, tokens: List[str]) -> str:
        raise NotImplementedError()


class NoPunctuationSplitter(Splitter):
    def split(self, message: str) -> object:
        res = re.split(r"[^\w'-]+", message)
        if res == ['']:
            return []

        return res

    def join(self, tokens: List[str]) -> str:
        return ' '.join(tokens)


class PunctuationSplitter(Splitter):
    def split(self, message: str) -> object:
        return re.findall(r"[\w'-]+|\s+|[^\w\s'-]+", message)

    def join(self, tokens: List[str]) -> str:
        first_non_punctuation = next(
            (i for i, token in enumerate(tokens) if re.match(r"[^\W\d]+[\w'-]*", token)),
            len(tokens)
        )
        last_allowed = next(
            (i for i, token in enumerate(reversed(tokens)) if re.match(r".*[.!?\w]", token)),
            len(tokens)
        )
        tokens = tokens[first_non_punctuation:len(tokens)-last_allowed]

        res = ''
        for token in tokens:
            if res == '' or re.match(r'.*[.!?]\s+$', res) and len(token) > 0:
                token = token[0].upper() + token[1:]
            res += token

        return res.strip()


# TODO: примыкать пробелы к пунктуации, игнорировать отдельные пробелы, джойнить умнее
#       (ставить пробел между токенами только когда оба не пунктуационные)
# class PunctuationSplitter(Splitter):
#     def split(self, message: str) -> object:
#         return re.findall(r"[\w'-]+|\s+|[^\w\s'-]+", message)
#
#     def join(self, tokens: List[str]) -> str:
#         return ''.join(tokens)
