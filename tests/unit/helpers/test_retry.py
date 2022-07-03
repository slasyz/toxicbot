import pytest

from toxic.helpers.retry import with_retry, with_retry_async


class FirstException(Exception):
    pass


class SecondException(Exception):
    pass


class Fail:
    def __init__(self, fail_attempts: int, exception: Exception):
        self.fail_attempts = fail_attempts
        self.exception = exception
        self.counter = 0

    def call(self) -> bool:
        self.counter += 1
        if self.counter <= self.fail_attempts:
            raise self.exception

        return True


def test_with_retry_success():
    fail = Fail(2, FirstException())

    @with_retry(3, (FirstException, SecondException))
    def fail_func() -> bool:
        return fail.call()

    assert fail_func()
    assert fail.counter == 3


async def test_with_retry_async_success():
    fail = Fail(2, FirstException())

    @with_retry_async(3, (FirstException, SecondException))
    async def fail_func() -> bool:
        return fail.call()

    assert await fail_func()
    assert fail.counter == 3


def test_with_retry_unexpected_exception():
    fail = Fail(2, FirstException())

    @with_retry(3, (SecondException,))
    def fail_func() -> bool:
        return fail.call()

    with pytest.raises(FirstException):
        fail_func()

    assert fail.counter == 1


def test_with_retry_attempts_exceeded():
    fail = Fail(5, FirstException())

    @with_retry(3, (FirstException,))
    def fail_func() -> bool:
        return fail.call()

    with pytest.raises(FirstException):
        fail_func()

    assert fail.counter == 3


async def test_with_retry_async_attempts_exceeded():
    fail = Fail(5, FirstException())

    @with_retry_async(3, (FirstException,))
    async def fail_func() -> bool:
        return fail.call()

    with pytest.raises(FirstException):
        await fail_func()

    assert fail.counter == 3
