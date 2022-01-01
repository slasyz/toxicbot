from toxic.features import translating


def test_translate():
    res = translating.do('токсичный', 'ru', 'uk')
    assert res == 'токсичний'
