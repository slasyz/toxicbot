from src.features import translate


def test_translate():
    res = translate.do('токсичный', 'ru', 'uk')
    assert res == 'токсичний'
