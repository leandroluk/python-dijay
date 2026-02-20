from src.domain._shared import DomainError


class TodoNotFoundError(DomainError):
    def __init__(self, message: str | None = None):
        super().__init__(message or "Todo not found")
