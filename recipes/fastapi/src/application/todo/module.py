from dijay import module

from .create_todo import CreateTodoUsecase
from .delete_todo import DeleteTodoUsecase
from .get_todo_by_id import GetTodoByIdUsecase
from .list_todo import ListTodoUsecase
from .update_todo import UpdateTodoUsecase

providers = [
    CreateTodoUsecase,
    DeleteTodoUsecase,
    GetTodoByIdUsecase,
    ListTodoUsecase,
    UpdateTodoUsecase,
]


@module(providers=providers, exports=providers)
class TodoModule:
    pass
