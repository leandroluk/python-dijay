from datetime import UTC, datetime


class DomainError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
        self.occurred_at = datetime.now(UTC)
        self.name = self.__class__.__name__
