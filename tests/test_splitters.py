import pytest

from src.services.chain.splitters import NoPunctuationSplitter


@pytest.mark.parametrize(
    "message, tokens",
    [
        ("Hello, I'm a string!!! слово ещё,,, бла-бла-бла", ['Hello', "I'm", 'a', 'string', 'слово', 'ещё', 'бла-бла-бла'])
    ]
)
def test_no_punctuation_splitter(message, tokens):
    splitter = NoPunctuationSplitter()
    assert splitter.split_tokens(message) == tokens
