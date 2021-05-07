from toxicbot.features.joke import get_random_joke


def test_get_random_joke():
    _, ok = get_random_joke()
    assert ok
