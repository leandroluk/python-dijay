# Getting Started

## Installation

Install **dijay** using your preferred package manager:

=== "uv"

    ```bash
    uv add dijay
    ```

=== "pip"

    ```bash
    pip install dijay
    ```

!!! note "Python Version"
    dijay requires **Python 3.14+** and leverages modern features like `type` parameter syntax and `Annotated` generics.

## Your First App

### 1. Define a Service

Use the `@injectable` decorator to mark a class as injectable:

```python
from dijay import injectable

@injectable()
class GreetingService:
    def greet(self, name: str) -> str:
        return f"Hello, {name}!"
```

### 2. Create a Module

Modules group related providers together. Use `providers` to register and `exports` to share:

```python
from dijay import module

@module(
    providers=[GreetingService],
    exports=[GreetingService],
)
class GreetingModule: ...
```

### 3. Create the Root Module

The root module imports all feature modules:

```python
@module(imports=[GreetingModule])
class AppModule: ...
```

### 4. Bootstrap and Resolve

Use `Container.from_module` to build the dependency graph and resolve services:

```python
import asyncio
from dijay import Container

async def main():
    async with Container.from_module(AppModule) as container:
        service = await container.resolve(GreetingService)
        print(service.greet("World"))

if __name__ == "__main__":
    asyncio.run(main())
```

Running this will print:

```
Hello, World!
```

## How It Works

1. `@injectable()` marks `GreetingService` as a provider.
2. `@module(...)` groups providers and exports them.
3. `Container.from_module(AppModule)` scans the module tree and registers all providers.
4. `async with container` runs `@on_bootstrap` hooks on entry and `@on_shutdown` hooks on exit.
5. `container.resolve(GreetingService)` returns a fully constructed instance with all dependencies injected.

## Next Steps

- Learn how to organize your app with [Modules](guides/modules.md)
- Use [Custom Providers](guides/providers.md) for values, factories, and class overrides
- Add [Lifecycle Hooks](guides/lifecycle.md) for startup/shutdown logic
- Integrate with [FastAPI](guides/fastapi.md)
