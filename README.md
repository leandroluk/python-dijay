[![ci](https://github.com/leandroluk/python-dijay/actions/workflows/ci.yml/badge.svg)](https://github.com/leandroluk/python-dijay/actions/workflows/ci.yml)
[![coverage](https://codecov.io/gh/leandroluk/python-dijay/graph/badge.svg)](https://codecov.io/gh/leandroluk/python-dijay)
[![release](https://img.shields.io/github/v/release/leandroluk/python-dijay?color=green)](https://github.com/leandroluk/python-dijay/releases)
[![pypi](https://img.shields.io/pypi/v/dijay?color=green)](https://pypi.org/project/dijay)
[![license](https://img.shields.io/github/license/leandroluk/python-dijay)](https://github.com/leandroluk/python-dijay/blob/main/LICENSE)

# 🎧 dijay

**Drop the beat on your dependencies.**

**dijay** is the "remix" your architecture needs: NestJS-style modularity, native async performance, and rigorous typing for Python 3.14+. Less boilerplate, more harmony.

## 🚀 Features

* **Modular Architecture**: Organize code into `@module`s with `imports`, `providers`, and `exports`.
* **Constructor Injection**: Clean, testable injection via `__init__` and `Annotated`.
* **Flexible Scopes**: `SINGLETON`, `TRANSIENT`, and `REQUEST`.
* **Async Native**: First-class support for asynchronous factories and lifecycle hooks.
* **Custom Providers**: `Provide` dataclass for value, class and factory bindings.
* **Lifecycle Hooks**: `@on_bootstrap` and `@on_shutdown` decorators.
* **Circular Dependency Detection**: Immediate `RuntimeError` on cycles.

## 📦 Installation

```bash
uv add dijay
```

## ⚡ Quick Start

### 1. Define Services

```python
from dijay import injectable

@injectable()
class CatsService:
    def get_all(self):
        return ["Meow", "Purr"]
```

### 2. Create a Module

```python
from dijay import module

@module(
    providers=[CatsService],
    exports=[CatsService],
)
class CatsModule:
    pass
```

### 3. Bootstrap the App

```python
import asyncio
from dijay import Container, module

@module(imports=[CatsModule])
class AppModule:
    pass

async def main():
    async with Container.from_module(AppModule) as container:
        service = await container.resolve(CatsService)
        print(service.get_all())

if __name__ == "__main__":
    asyncio.run(main())
```

`Container.from_module(AppModule)` scans the module tree, registers all providers, and returns a fully configured `Container`.

## 🧩 Modules

Modules are the building blocks of a **dijay** application. They encapsulate providers and manage dependencies.

```python
@module(
    imports=[DatabaseModule],
    providers=[UserService],
    exports=[UserService],
)
class UserModule: ...
```

### Dynamic Modules

For conditional configuration (e.g. swapping implementations by environment), use a static method that returns a `DynamicModule`:

```python
import os
from dijay import DynamicModule, module

from .fake import FakeDatabaseModule
from .postgres import PostgresDatabaseModule

@module(
    imports=[FakeDatabaseModule],
    exports=[FakeDatabaseModule],
)
class DatabaseModule:
    @staticmethod
    def for_root() -> DynamicModule:
        db_module = {
            "fake": FakeDatabaseModule,
            "postgres": PostgresDatabaseModule,
        }[os.getenv("DB_PROVIDER", "fake")]

        return DynamicModule(
            module=DatabaseModule,
            imports=[db_module],
            exports=[db_module],
        )
```

## 💉 Custom Providers

Use `Provide` to register values, classes or factories directly in a module:

```python
from dijay import module, Provide

@module(providers=[
    Provide("DB_URL", use_value="postgresql://localhost/mydb"),
    Provide(Cache, use_class=RedisCache),
    Provide(HttpClient, use_factory=create_http_client),
])
class InfraModule: ...
```

| Attribute     | Description                                 |
| ------------- | ------------------------------------------- |
| `use_value`   | Binds a constant value to the token.        |
| `use_class`   | Binds a class to instantiate for the token. |
| `use_factory` | Binds a callable to invoke for the token.   |
| `scope`       | Lifetime scope (defaults to `SINGLETON`).   |

## 💉 Advanced Constructor Injection

Use `Annotated` with `Inject` to decouple type hints from injection tokens:

```python
from typing import Annotated
from dijay import Inject, injectable

@injectable()
class Persistence:
    def __init__(
        self,
        conn_string: Annotated[str, Inject("DB_URL")]
    ):
        self.conn = conn_string
```

## 🔄 Lifecycle Hooks

**dijay** supports `@on_bootstrap` and `@on_shutdown` decorators to execute logic when the container starts or stops. The most common way to use them is as decorators for methods within `@injectable` classes:

```python
from dijay import on_bootstrap, on_shutdown, injectable

@injectable()
class Database:
    @on_bootstrap
    async def connect(self):
        print("Database connected!")

    @on_shutdown
    async def disconnect(self):
        print("Database disconnected!")
```

Hooks can also be defined as standalone functions:

```python
@on_bootstrap
async def log_startup(db: Database):
    print("App is starting...")
```

Hooks can be synchronous or asynchronous and support full dependency injection. They are automatically triggered when using the container as an async context manager:

```python
async with Container.from_module(AppModule):
    # @on_bootstrap hooks have already run here
    ...
# @on_shutdown hooks run when exiting the block
```

Alternatively, you can call them manually:

```python
container = Container.from_module(AppModule)
await container.bootstrap()
...
await container.shutdown()
```

## 🌐 FastAPI Integration

Create a helper to resolve dependencies from the container via FastAPI's `Depends`:

```python
from typing import Annotated

from fastapi import Depends, Request


def inject[T](token: type[T]) -> T:
    """FastAPI dependency that resolves a token from the container."""
    async def use(request: Request) -> T:
        return await request.app.state.container.resolve(token, id=str(id(request)))

    return Annotated[token, Depends(use)]
```

Then, use the container as an async context manager and attach it to `app.state`:

```python
import asyncio

import uvicorn
from fastapi import FastAPI

from dijay import Container, module

@module(...)
class AppModule: ...

app = FastAPI(title="My API", version="0.0.1")


async def main():
    async with Container.from_module(AppModule) as container:
        app.state.container = container

        server = uvicorn.Server(uvicorn.Config(app, host="0.0.0.0", port=8000))
        await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
```

For **development with reload**, use event handlers since uvicorn factories require synchronous return:

```python
def dev():
    container = Container.from_module(AppModule)
    app.state.container = container
    app.add_event_handler("startup", container.bootstrap)
    app.add_event_handler("shutdown", container.shutdown)
    return app
```

Use your routes with the `inject` helper:

```python
@app.get("/")
async def root(service: inject(MyService)):
    return await service.do_something()
```

## 🔄 Circular Dependency Detection

**dijay** monitors the resolution stack. If a cycle is detected (e.g., `A → B → A`), a `RuntimeError` is raised immediately.

## 🛠️ Development

```bash
uv sync
uv run pytest
uv build
```

## 📄 License

MIT
