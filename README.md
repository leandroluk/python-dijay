[![ci](https://github.com/leandroluk/python-dijay/actions/workflows/ci.yml/badge.svg)](https://github.com/leandroluk/python-dijay/actions/workflows/ci.yml)
[![coverage](https://codecov.io/gh/leandroluk/python-dijay/graph/badge.svg)](https://codecov.io/gh/leandroluk/python-dijay)
[![release](https://img.shields.io/github/v/release/leandroluk/python-dijay)](https://github.com/leandroluk/python-dijay/releases)
[![pypi](https://img.shields.io/pypi/v/dijay)](https://pypi.org/project/dijay)
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

## 🌐 FastAPI Integration

Integrate **dijay** using FastAPI's `lifespan` to manage the container lifecycle:

```python
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Request
from dijay import Container, module

@module(...)
class AppModule: ...

@asynccontextmanager
async def lifespan(app: FastAPI):
    container = Container.from_module(AppModule)
    await container.bootstrap()
    app.state.container = container
    yield
    await container.shutdown()

app = FastAPI(lifespan=lifespan)


def inject[T](token: type[T]):
    """FastAPI dependency that resolves a token from the container."""
    async def use(request: Request) -> T:
        return await request.app.state.container.resolve(
            token, id=str(id(request))
        )
    return Depends(use)


@app.get("/")
async def root(
    service: Annotated[MyService, inject(MyService)]
):
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
