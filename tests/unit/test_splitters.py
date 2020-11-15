import pytest

from src.features.chain.splitters import NoPunctuationSplitter, PunctuationSplitter


@pytest.mark.parametrize(
    "message, tokens",
    [
        ("Hello, I'm a string!!! слово ещё,,, бла-бла-бла", ['Hello', "I'm", 'a', 'string', 'слово', 'ещё', 'бла-бла-бла']),
        ('', []),
    ]
)
def test_no_punctuation_splitter(message, tokens):
    splitter = NoPunctuationSplitter()
    assert splitter.split(message) == tokens


@pytest.mark.parametrize(
    "message, tokens",
    [
        ("Hello, I'm a string!!! слово ещё,,, бла-бла-бла", ['Hello', ',', ' ', "I'm", ' ', 'a', ' ', 'string', '!!!', ' ', 'слово', ' ', 'ещё', ',,,', ' ', 'бла-бла-бла']),
        ("several    spaces", ['several', '    ', 'spaces']),
        ('', []),
    ]
)
def test_punctuation_splitter(message, tokens):
    splitter = PunctuationSplitter()
    assert splitter.split(message) == tokens
