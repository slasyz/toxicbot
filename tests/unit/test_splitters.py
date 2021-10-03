import pytest

from toxic.features.chain.splitters import WordsOnlySplitter, PunctuationSplitter, SpaceAdjoinSplitter


@pytest.mark.parametrize(
    ['message', 'tokens'],
    [
        ("Hello, I'm a string!!! слово ещё,,, бла-бла-бла", ['Hello', "I'm", 'a', 'string', 'слово', 'ещё', 'бла-бла-бла']),
        ('', []),
    ]
)
def test_no_punctuation_splitter(message, tokens):
    splitter = WordsOnlySplitter()
    assert splitter.split(message) == tokens


@pytest.mark.parametrize(
    ['message', 'tokens'],
    [
        ("Hello, I'm a string!!! слово ещё,,, бла-бла-бла", ['Hello', ',', ' ', "I'm", ' ', 'a', ' ', 'string', '!!!', ' ', 'слово', ' ', 'ещё', ',,,', ' ', 'бла-бла-бла']),
        ('several    spaces', ['several', '    ', 'spaces']),
        ('', []),
    ]
)
def test_punctuation_splitter(message, tokens):
    splitter = PunctuationSplitter()
    assert splitter.split(message) == tokens


@pytest.mark.parametrize(
    ['message', 'tokens'],
    [
        ('two words', ['two', 'words']),
        ('Hello, friend!', ['Hello', ', ', 'friend', '!']),
        ("Hello, I'm a string!!! слово ещё,,, бла-бла-бла", ['Hello', ', ', "I'm", 'a', 'string', '!!! ', 'слово', 'ещё', ',,, ', 'бла-бла-бла']),
        ('several    spaces', ['several', 'spaces']),
        ('line\nbreak', ['line', '\n', 'break']),
        ('', []),
    ]
)
def test_space_adjoin_splitter_split(message, tokens):
    splitter = SpaceAdjoinSplitter()
    assert splitter.split(message) == tokens


@pytest.mark.parametrize(
    ['tokens', 'message'],
    [
        (['two', 'words'], 'Two words'),
        (['Hello', ', ', 'friend', '!'], 'Hello, friend!'),
        (['Hello', ', ', "I'm", 'a', 'string', '!!! ', 'слово', 'ещё', ',,, ', 'бла-бла-бла'], "Hello, I'm a string!!! Слово ещё,,, бла-бла-бла"),
        (['line', '\n', 'break'], 'Line\nbreak'),
        (['-', 'hello'], 'Hello'),
        ([], ''),
    ]
)
def test_space_adjoin_splitter_join(tokens, message):
    splitter = SpaceAdjoinSplitter()
    assert splitter.join(tokens) == message
