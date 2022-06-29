import pytest

from toxic.features.joke import Joker


@pytest.mark.asyncio
def test_get_random_joke():
    joker = Joker('bottom text')
    _, ok = await joker.get_random_joke()
    assert ok
