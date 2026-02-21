# FastAPI Integration

This guide shows how to integrate **dijay** with [FastAPI](https://fastapi.tiangolo.com/).

## Helpers

Create two helper functions that bridge FastAPI's `Depends` with dijay's container:

```python
from typing import Annotated, Any

from fastapi import Depends, Request


def inject[T](token: type[T]) -> T:
    """Resolve a dependency from the dijay container."""
    async def use(request: Request) -> T:
        return await request.app.state.container.resolve(token, id=str(id(request)))

    return Annotated[token, Depends(use)]


def guard(token: type, *args) -> Any:
    """Resolve a guard and execute it with the current request."""
    async def use(request: Request):
        instance = await request.app.state.container.resolve(token, id=str(id(request)))
        return await instance(request, *args)

    return Annotated[Any, Depends(use)]
```

- `inject(Token)` resolves and returns the **instance** of the token.
- `guard(Token, *args)` resolves the instance, **calls** it with the request and extra arguments, and returns the result.

Each request gets a unique `id` based on the request object, enabling `REQUEST`-scoped dependencies.

## Server as Injectable

Encapsulate the FastAPI app inside an injectable class so dijay manages its lifecycle:

```python
from fastapi import FastAPI

from dijay import injectable


@injectable()
class HttpServer:
    def __init__(self, config: HttpConfig):
        self.config = config
        self.app = FastAPI(title="My API", version="0.0.1")
        # register routes, middleware, etc.
```

The container stores the `HttpServer` as a singleton. Its dependencies (like `HttpConfig`) are resolved automatically.

## Running the Application

Use the container as an async context manager and resolve the server to run it:

```python
import asyncio

import uvicorn

from dijay import Container

from .module import AppModule
from .presentation.http.server import HttpServer


async def main():
    async with Container.from_module(AppModule) as container:
        server = await container.resolve(HttpServer)
        server.app.state.container = container
        config = uvicorn.Config(
            server.app,
            host=server.config.host,
            port=server.config.port,
        )
        await uvicorn.Server(config).serve()
```

The `async with` block ensures that `@on_bootstrap` hooks run before serving and `@on_shutdown` hooks run on exit.

For development with auto-reload, use [watchfiles](https://watchfiles.helpmanual.io/) instead of uvicorn's `--reload`:

```python
from watchfiles import run_process

from .presentation.http.config import HttpConfig

config = HttpConfig()

if config.enable_reload:
    run_process("./src", target=lambda: asyncio.run(main()))
else:
    asyncio.run(main())
```

This re-runs the entire `main()` on file changes, so the container is always rebuilt cleanly.

## Using Routes

Use `inject` to resolve dependencies in route parameters:

```python
@app.get("/users")
async def list_users(service: inject(UserService)):
    return await service.get_all()

@app.post("/users")
async def create_user(service: inject(UserService), body: CreateUserDTO):
    return await service.create(body)
```

## Guards

A guard is an injectable class with a `__call__` method that validates the request:

```python
import jwt
from fastapi import HTTPException, Request

from dijay import injectable


@injectable()
class PermissionGuard:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def __call__(self, request: Request, roles: list[str]):
        token = (request.headers.get("authorization") or "").removeprefix("Bearer ").strip()
        if not token:
            raise HTTPException(401)

        try:
            payload = jwt.decode(token, "SECRET", algorithms=["HS256"])
        except jwt.InvalidTokenError:
            raise HTTPException(401)

        user = await self.user_service.find_by_id(payload["sub"])
        if not user or not any(r in user.roles for r in roles):
            raise HTTPException(403, "Insufficient permissions")

        return user
```

Use the `guard` helper to resolve and execute it in a single step:

```python
@app.get("/me")
async def me(user: guard(PermissionGuard, ["user", "admin"])):
    return {"id": user.id, "email": user.email}
```

### Chaining Guards

Guards can be chained so each one handles a single responsibility.

**By parameter order** — each guard communicates via `request.state`:

```python
@injectable()
class FooGuard:
    async def __call__(self, request: Request):
        request.state.foo = "foo_value"
        return request.state.foo


@injectable()
class BarGuard:
    async def __call__(self, request: Request):
        foo = request.state.foo  # set by FooGuard
        return f"{foo}_bar"


@app.get("/example")
async def example(foo: guard(FooGuard), bar: guard(BarGuard)):
    return {"foo": foo, "bar": bar}
```

The execution order follows the parameter declaration: `FooGuard` runs first, then `BarGuard`.

**By dependency chain** — a guard declares another guard as a dependency in its `__call__`:

```python
@injectable()
class FooGuard:
    async def __call__(self, request: Request):
        return "foo_value"


@injectable()
class BarGuard:
    async def __call__(self, request: Request, foo: guard(FooGuard)):
        return f"{foo}_bar"


@app.get("/example")
async def example(bar: guard(BarGuard)):
    return {"bar": bar}
```

`BarGuard` explicitly depends on `FooGuard`, so the execution order is guaranteed regardless of parameter position. Only the final guard needs to appear in the route.

## Full Example

See the [fastapi-ddd recipe](https://github.com/leandroluk/python-dijay/tree/main/recipes/fastapi-ddd) for a complete example with:

- DDD-style architecture (`domain`, `application`, `infrastructure`, `presentation`)
- Abstract ports with concrete adapters via `@injectable(Token)`
- Custom OpenAPI configuration
- Development and production entry points
