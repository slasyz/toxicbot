import pytest

from toxic.helpers.delayer import Delayer


@pytest.mark.parametrize(
    ["total", "keepalive", "expected"],
    [
        (10, 5, [5, 5]),
        (11, 5, [5, 5, 1]),
        (5, 10, [5]),
        (4, 5, [4]),
    ]
)
def test_delayer(total: int, keepalive: int, expected: list[int]):
    delayer = Delayer(total, keepalive)
    result = list(iter(delayer))
    assert result == expected
