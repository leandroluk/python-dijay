from typing import Any


class Inject:
    """Marker used in ``Annotated`` type hints to specify a custom injection token.

    When a parameter is annotated with ``Annotated[SomeType, Inject(token)]``,
    the container resolves ``token`` instead of ``SomeType``.

    Example::

        async def handler(
            svc: Annotated[MyService, Inject("my_service_token")]
        ) -> None: ...
    """

    def __init__(self, token: Any) -> None:
        """
        Args:
            token: The token (class, string, or any hashable) that the container
                   should resolve for the annotated parameter.
        """
        self.token = token
