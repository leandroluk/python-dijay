# FastAPI Integration

This guide shows how to integrate **dijay** with [FastAPI](https://fastapi.tiangolo.com/).

## The `inject` Helper

Create a helper function that bridges FastAPI's `Depends` with dijay's container:

```python
from typing import Annotated

from fastapi import Depends, Request


def inject[T](token: type[T]) -> T:
    """Resolve a dependency from the dijay container."""
    async def use(request: Request) -> T:
        return await request.app.state.container.resolve(
            token, id=str(id(request))
        )

    return Annotated[token, Depends(use)]
```

Each request gets a unique `id` based on the request object, enabling `REQUEST`-scoped dependencies.

## Production Setup

Use the container as an async context manager and run uvicorn programmatically:

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

        server = uvicorn.Server(
            uvicorn.Config(app, host="0.0.0.0", port=8000)
        )
        await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
```

The `async with` block ensures that `@on_bootstrap` hooks run before serving and `@on_shutdown` hooks run on exit.

## Development with Reload

When using uvicorn's `--reload` mode, you need a synchronous factory function. Use event handlers instead:

```python
def dev():
    container = Container.from_module(AppModule)
    app.state.container = container
    app.add_event_handler("startup", container.bootstrap)
    app.add_event_handler("shutdown", container.shutdown)
    return app
```

Then run with:

```bash
uvicorn "src.main:dev" --factory --reload
```

## Using Routes

Use the `inject` helper as a type annotation in your route parameters:

```python
@app.get("/users")
async def list_users(service: inject(UserService)):
    return await service.get_all()

@app.post("/users")
async def create_user(service: inject(UserService), body: CreateUserDTO):
    return await service.create(body)
```

## Full Example

See the [fastapi-ddd recipe](https://github.com/leandroluk/python-dijay/tree/main/recipes/fastapi-ddd) for a complete example with:

- DDD-style architecture (`domain`, `application`, `infrastructure`, `presentation`)
- Abstract ports with concrete adapters via `@injectable(Token)`
- Custom OpenAPI configuration
- Development and production entry points
