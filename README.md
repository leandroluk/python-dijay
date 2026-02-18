# 🎧 dijay

**dijay** is a high-performance, asynchronous Dependency Injection (DI) library for Python 3.14+, heavily inspired by the NestJS ecosystem. Built for strict typing and speed, it leverages the latest Python features (PEP 649, 695) and is optimized for `uv`.

## 🚀 Features

* **Constructor Injection**: Clean, testable injection via `__init__` and `Annotated`.
* **Flexible Scopes**: Support for `SINGLETON`, `TRANSIENT`, and `REQUEST`.
* **Async Native**: First-class support for asynchronous factories and lifecycle hooks.
* **Scope Bubbling**: Intelligent lifetime management to prevent stale references.
* **Lifecycle Hooks**: Simple `@on_bootstrap` and `@on_shutdown` decorators.
* **Zero Config**: Powerful autowiring based on Type Hints.

## 📦 Installation

```bash
uv add dijay

```

## ⚡ Quick Start

```python
from typing import Annotated
from dijay import inject, resolve, Inject

class Base: pass

@inject(Base)
class Implementation(Base):
    pass

@inject()
class Controller:
    def __init__(self, service: Base):
        self.service = service

async def main():
    app = await resolve(Controller)

```

## 🫧 Scope Bubbling

**dijay** implements automatic scope elevation (bubbling). If a provider with a wider lifetime (e.g., `SINGLETON`) depends on a provider with a narrower lifetime (e.g., `REQUEST`), the container automatically treats the dependent as having the narrower scope.

This prevents **Scope Leaks**, ensuring that a Singleton never captures and holds onto a stale Request-scoped instance.

## 🌐 FastAPI Integration

To integrate **dijay** with FastAPI, use a dependency to manage request-scoped resolution:

```python
from fastapi import FastAPI, Request, Depends
from dijay import resolve, instance

app = FastAPI()
container = instance()

async def get_service[T](token: type[T]):
    async def _resolve(request: Request) -> T:
        return await container.resolve(token, id=str(id(request)))
    return _resolve

@app.get("/")
async def root(service: Annotated[MyService, Depends(get_service(MyService))]):
    return await service.do_something()

```

## 💉 Advanced Constructor Injection

The library leverages `Annotated` to decouple type hints from injection tokens, similar to the NestJS `@Inject()` decorator.

```python
from typing import Annotated
from dijay import Inject, inject

@inject()
class Persistence:
    def __init__(
        self, 
        conn_string: Annotated[str, Inject("DB_CONNECTION")]
    ):
        self.conn = conn_string

```

## 🛠️ Development

1. **Sync Environment**: `uv sync`
2. **Run Tests**: `uv run pytest`
3. **Build Package**: `uv build`

## 🔄 Circular Dependency Detection

**dijay** actively monitors the resolution stack. If a cycle is detected (e.g., A -> B -> A), a `RuntimeError` is raised immediately to prevent stack overflow.

## 📄 License

MIT

