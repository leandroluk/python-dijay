from abc import ABC, abstractmethod


class Usecase[TResult, TInput = None](ABC):
    @abstractmethod
    async def execute(self, *, data: TInput = None) -> TResult:
        raise NotImplementedError
