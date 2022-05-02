from typing import Callable


def with_retry(max_attempts: int, exceptions: tuple[type[Exception], ...]) -> Callable:
    def decorator(f: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            latest_exception: Exception | None = None
            for _ in range(max_attempts):
                try:
                    return f(*args, *kwargs)
                except exceptions as ex:
                    latest_exception = ex

            raise latest_exception

        return wrapper

    return decorator
