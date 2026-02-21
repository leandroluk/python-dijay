# Lifecycle Hooks

**dijay** supports `@on_bootstrap` and `@on_shutdown` decorators to execute logic when the container starts or stops.

## Method Hooks

The most common pattern is decorating methods within `@injectable` classes:

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

When the container bootstraps, it resolves the `Database` singleton and calls `connect()`. On shutdown, it calls `disconnect()`.

## Standalone Hooks

Hooks can also be standalone functions. Parameters are injected automatically:

```python
from dijay import on_bootstrap

@on_bootstrap
async def log_startup(db: Database):
    print(f"App started with {db}")
```

## Sync and Async

Hooks can be synchronous or asynchronous — the container handles both:

```python
@on_bootstrap
def sync_hook():
    print("Sync hook!")

@on_bootstrap
async def async_hook():
    print("Async hook!")
```

## Triggering Hooks

### Async Context Manager (recommended)

Hooks are triggered automatically when using the container as an async context manager:

```python
async with Container.from_module(AppModule) as container:
    # @on_bootstrap hooks have already run here
    ...
# @on_shutdown hooks run when exiting the block
```

### Manual Control

You can also call hooks explicitly:

```python
container = Container.from_module(AppModule)
await container.bootstrap()
# ... app logic ...
await container.shutdown()
```

!!! note
    `shutdown()` only runs hooks for singletons that were actually created during the container's lifetime.
