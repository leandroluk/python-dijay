import functools
from collections.abc import Callable

from fastapi import HTTPException


def map_domain_error[P, R](
    *mappings: tuple[type[Exception], int]
    | list[tuple[type[Exception], int]]
    | dict[type[Exception], int],
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator to map exceptions to HTTP Exceptions.

    Usage:
        @map_domain_error((NotFoundException, 404))
        # OR
        @map_domain_error((NotFoundException, 404), (ValueError, 400))
    """
    error_map = {}

    for mapping in mappings:
        if isinstance(mapping, tuple):
            error_map[mapping[0]] = mapping[1]
        elif isinstance(mapping, list):
            error_map.update(dict(mapping))
        elif isinstance(mapping, dict):
            error_map.update(mapping)

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                status_code = error_map.get(type(e))
                if status_code:
                    raise HTTPException(status_code=status_code, detail=str(e)) from e
                raise e

        return wrapper

    return decorator
