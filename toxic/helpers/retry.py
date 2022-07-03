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


def with_retry_async(max_attempts: int, exceptions: tuple[type[Exception], ...]):
    def decorator(f: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            latest_exception: Exception | None = None
            for _ in range(max_attempts):
                try:
                    return await f(*args, *kwargs)
                except exceptions as ex:
                    latest_exception = ex

            raise latest_exception

        return wrapper

    return decorator
