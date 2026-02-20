# 🎧 dijay — FastAPI Recipe

This recipe demonstrates how to use **dijay** in a real FastAPI application, following a **DDD (Ports & Adapters)** architecture with **Use Cases** as business logic orchestrators and **raw entities** (Pydantic models) without embedded domain logic.

## 🏗️ Architecture

```
src/
├── domain/                    # Domain layer (pure, no external dependencies)
│   ├── _shared/               # Mixins (Indexable, Creatable, Updatable), ports (Database), errors
│   └── todo/
│       ├── entities.py        # TodoEntity (raw data structure)
│       ├── errors.py          # TodoNotFoundError
│       └── repositories.py    # TodoRepository (port — ABC)
│
├── application/               # Application layer (orchestration)
│   ├── _shared/
│   │   └── usecase.py         # Usecase[TResult, TInput] (generic contract)
│   └── todo/
│       ├── create_todo.py     # CreateTodoUsecase
│       ├── list_todo.py       # ListTodoUsecase
│       ├── get_todo_by_id.py
│       ├── update_todo.py
│       └── delete_todo.py
│
├── infrastructure/           # Infrastructure layer (adapters)
│   └── database/
│       ├── module.py         # DatabaseModule (Dynamic Module — swappable implementation)
│       └── fake/
│           ├── module.py     # FakeDatabaseModule
│           ├── database.py   # FakeDatabase (adapter for Database port)
│           └── repositories/
│               └── todo.py   # FakeTodoRepository (adapter for TodoRepository port)
│
├── presentation/             # Presentation layer
│   └── http/
│       ├── config.py         # HttpConfig (environment variables)
│       ├── server.py         # HttpServer (FastAPI app builder)
│       └── todo/
│           ├── route.py      # REST routes (CRUD)
│           └── dtos/         # Input DTOs (request body)
│
├── module.py                 # AppModule (root module)
└── main.py                   # Entry point (dev + production)
```

### Principles

- **Entities** are raw data structures (Pydantic `BaseModel`) — no business methods.
- **Repositories** are ports (ABCs) defined in the domain — the domain knows nothing about infrastructure.
- **Use Cases** orchestrate business logic, receiving repositories via dependency injection.
- **Adapters** (infrastructure) implement the domain ports.
- **Dynamic Modules** allow swapping implementations via environment variable.

## 🔄 Dynamic Module — Swappable Implementations

`DatabaseModule` is ready to swap database implementations at runtime via the `DB_PROVIDER` environment variable:

```python
# src/infrastructure/database/module.py

@module(
    imports=[FakeDatabaseModule],
    exports=[FakeDatabaseModule],
)
class DatabaseModule:
    @staticmethod
    def for_root(connection_string: str) -> DynamicModule:
        db_module = {
            "fake": FakeDatabaseModule,
            # "postgres": PostgresDatabaseModule,
            # "mongo": MongoDatabaseModule,
        }[os.getenv("DB_PROVIDER", "fake")]

        return DynamicModule(
            module=DatabaseModule,
            imports=[db_module],
            exports=[db_module],
        )
```

To add a new implementation (e.g. PostgreSQL):

1. Create `src/infrastructure/database/postgres/` with an adapter for `TodoRepository`.
2. Create `PostgresDatabaseModule` registering the providers.
3. Add the entry `"postgres": PostgresDatabaseModule` to the `for_root` dict.
4. Set `DB_PROVIDER=postgres` in your environment.

No changes to domain or use cases are needed.

## 🚀 Running

### Development (with hot-reload)

```bash
cd recipes/fastapi
uv run python -m src
```

By default `HTTP_ENABLE_RELOAD=true`, and uvicorn reloads automatically on file changes.

### Production

```bash
HTTP_ENABLE_RELOAD=false uv run python -m src
```

### Environment Variables

| Variable             | Default     | Description             |
| -------------------- | ----------- | ----------------------- |
| `HTTP_HOST`          | `127.0.0.1` | Server host             |
| `HTTP_PORT`          | `8000`      | Server port             |
| `HTTP_PATH`          | `/`         | Path prefix             |
| `HTTP_ENABLE_RELOAD` | `true`      | Hot-reload (dev)        |
| `HTTP_TITLE`         | `Todo API`  | OpenAPI title           |
| `HTTP_VERSION`       | `0.0.1`     | OpenAPI version         |
| `HTTP_DESCRIPTION`   | `Todo API`  | OpenAPI description     |
| `DB_PROVIDER`        | `fake`      | Database implementation |

## 📡 API

| Method   | Route         | Description    |
| -------- | ------------- | -------------- |
| `POST`   | `/todos/`     | Create todo    |
| `GET`    | `/todos/`     | List all todos |
| `GET`    | `/todos/{id}` | Get by ID      |
| `PUT`    | `/todos/{id}` | Update todo    |
| `DELETE` | `/todos/{id}` | Delete todo    |

### Interactive Docs

Visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for Swagger UI.
Visit [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) for ReDoc.

## 📦 Dependencies

- [dijay](https://github.com/leandroluk/python-dijay) — DI container
- [FastAPI](https://fastapi.tiangolo.com/) — HTTP framework
- [uvicorn](https://www.uvicorn.org/) — ASGI server
- [watchfiles](https://watchfiles.helpmanual.io/) — Hot-reload
