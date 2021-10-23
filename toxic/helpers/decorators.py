from typing import Callable, Optional, Type

import telegram

from toxic.handlers.handler import MessageHandler


def non_empty(func: Callable[[Type[MessageHandler], str, telegram.Message], bool]) -> Callable[[Type[MessageHandler], telegram.Message], bool]:
    """
    Checks if message contains text before calling wrapping function.  If it does not contain it, returns False.
    """

    def wrapper(self, message: telegram.Message):
        if message.text is None:
            return False

        return func(self, message.text, message)

    return wrapper


def with_retry(max_attempts: int, exceptions: tuple[type[Exception], ...]) -> Callable:
    def decorator(f: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            latest_exception: Optional[Exception] = None
            for _ in range(max_attempts):
                try:
                    return f(*args, *kwargs)
                except exceptions as ex:
                    latest_exception = ex

            raise latest_exception

        return wrapper

    return decorator
