from fastapi import APIRouter

from src.application.todo import (
    CreateTodoData,
    CreateTodoUsecase,
    DeleteTodoData,
    DeleteTodoUsecase,
    GetTodoByIdData,
    GetTodoByIdUsecase,
    ListTodoResult,
    ListTodoUsecase,
    UpdateTodoData,
    UpdateTodoUsecase,
)
from src.domain.todo import TodoEntity, TodoNotFoundError
from src.presentation.http._shared import inject, map_domain_error
from src.presentation.http.todo.dtos import CreateTodoBodyDTO, UpdateTodoBodyDTO

router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("/", status_code=201)
async def create_todo(
    body: CreateTodoBodyDTO,
    usecase: inject(CreateTodoUsecase),
) -> TodoEntity:
    data = CreateTodoData(
        title=body.title,
        description=body.description,
    )
    return await usecase.execute(data)


@router.get("/")
async def list_todos(
    usecase: inject(ListTodoUsecase),
) -> ListTodoResult:
    return await usecase.execute()


@router.get("/{id}")
@map_domain_error((TodoNotFoundError, 404))
async def get_todo(
    id: str,
    usecase: inject(GetTodoByIdUsecase),
) -> TodoEntity:
    data = GetTodoByIdData(
        id=id,
    )
    return await usecase.execute(data)


@router.put("/{id}")
@map_domain_error((TodoNotFoundError, 404))
async def update_todo(
    id: str,
    body: UpdateTodoBodyDTO,
    usecase: inject(UpdateTodoUsecase),
) -> TodoEntity:
    data = UpdateTodoData(
        id=id,
        changes=UpdateTodoData.Changes(
            title=body.title,
            description=body.description,
            done=body.done,
        ),
    )
    return await usecase.execute(data)


@router.delete("/{id}", status_code=204)
@map_domain_error((TodoNotFoundError, 404))
async def delete_todo(
    id: str,
    usecase: inject(DeleteTodoUsecase),
):
    data = DeleteTodoData(
        id=id,
    )
    await usecase.execute(data)
