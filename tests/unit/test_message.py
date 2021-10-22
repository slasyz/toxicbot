import pytest

from toxic.messenger.message import split_into_chunks


@pytest.mark.parametrize(
    ['message', 'max_len', 'max_trimmed_len', 'expected_text', 'expected_trimmed'],
    [
        ('abcdefghijklmnopqrstuvwxyz', 3, 4, 'abc', ['defg', 'hijk', 'lmno', 'pqrs', 'tuvw', 'xyz']),
        ('abcdefghijklmnopqrstuvwxyz', 33, 4, 'abcdefghijklmnopqrstuvwxyz', []),
    ],
)
def test_split_into_chunks(message, max_len, max_trimmed_len, expected_text, expected_trimmed):
    text, trimmed = split_into_chunks(message, max_len, max_trimmed_len)
    assert text == expected_text
    assert trimmed == expected_trimmed
