import re


NO_PUNCTUATION_SPLIT_REGEXP = re.compile(r"[^\w'-]+")
PUNCTUATION_SPLIT_REGEXP = re.compile(r"[\w'-]+|\s+|[^\w\s'-]+")
PUNCTUATION_FIRST_REGEXP = re.compile(r"[^\W\d]+[\w'-]*")
PUNCTUATION_LAST_REGEXP = re.compile(r".*[.!?\w]")
PUNCTUATION_SENTENCE_END_REGEXP = re.compile(r'.*[.!?]\s+$')
SPACE_ADJOIN_SPLIT_REGEXP = re.compile(r"(([^\w'-]*|\s*)[^\w\s'-]+([^\w'-]*|\s*)|[\w'-]+|[\n\t+]+)")


class Splitter:
    """
    Splitter class implements a strategy of splitting and then joining tokens (words, punctuation marks, etc) back.
    """
    def split(self, message: str) -> list[str]:
        raise NotImplementedError()

    def join(self, tokens: list[str]) -> str:
        raise NotImplementedError()


class WordsOnlySplitter(Splitter):
    """
    WordsOnlySplitter is a straightforward splitter that picks only letters, hyphens and apostrophes.
    """
    def split(self, message: str) -> list[str]:
        res = NO_PUNCTUATION_SPLIT_REGEXP.split(message)
        if res == ['']:
            return []

        return res

    def join(self, tokens: list[str]) -> str:
        return ' '.join(tokens)


class PunctuationSplitter(Splitter):
    """
    PunctuationSplitter extracts each sequence of punctuation marks, series of spaces and series of letters as separate
    tokens.
    """
    def split(self, message: str) -> list[str]:
        return PUNCTUATION_SPLIT_REGEXP.findall(message)

    def join(self, tokens: list[str]) -> str:
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
    Joins spaces to punctuation marks, ignores separate spaces, and joins more clever (places a space between tokens
    only if both tokens are not punctuational).

    Unlike PunctuationSplitter, spaces are not picked out as separate tokens, so single "window" can hold more
    meaningful tokens.
    """
    def split(self, message: str) -> list[str]:
        return [x for x, y, z in SPACE_ADJOIN_SPLIT_REGEXP.findall(message)]

    def join(self, tokens: list[str]) -> str:
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
