from dijay import module
from src.domain.todo import TodoRepository

from .repositories import FakeTodoRepository

providers = [FakeTodoRepository]


@module(providers=providers, exports=[TodoRepository])
class FakeDatabaseModule:
    pass
