from typing import Annotated, cast

from fastapi import Depends, Request


def inject[T](token: type[T]) -> type[T]:
    """
    Dependency injection helper for FastAPI that resolves a token from the application
    container.

    Args:
        token: The type or class to be resolved.

    Returns:
        The resolved instance of the specified type.
    """

    async def use(request: Request) -> T:
        return await request.app.state.container.resolve(token, id=str(id(request)))

    return cast(type[T], Annotated[token, Depends(use)])
