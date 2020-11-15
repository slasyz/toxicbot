from src.features import translate


def test_translate():
    res = translate.do('токсичный')
    assert res == 'токсичний'
