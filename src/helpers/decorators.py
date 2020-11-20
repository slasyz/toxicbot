from typing import Callable, Tuple, Optional

import telegram


def non_empty(func: Callable) -> Callable:
    """
    Checks if message contains text before calling wrapping function.  If it does not contain it, returns False.
    """

    def wrapper(self, message: telegram.Message):
        if message.text is None:
            return False

        return func(self, message)

    return wrapper


def with_retry(max_attempts: int, exceptions: Tuple[Exception, ...]) -> Callable:
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
