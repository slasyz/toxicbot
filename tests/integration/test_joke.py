from toxicbot.features.joke import Joker


def test_get_random_joke():
    joker = Joker('bottom text')
    _, ok = joker.get_random_joke()
    assert ok
