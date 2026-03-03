# Lifecycle Hooks

**dijay** supports `@module.on_bootstrap` and `@module.on_shutdown` decorators to execute logic when the container starts or stops.

## Method Hooks

The most common pattern is decorating methods within `@injectable` classes:

```python
from dijay import module, injectable

@injectable()
class Database:
    @module.on_bootstrap
    async def connect(self):
        print("Database connected!")

    @module.on_shutdown
    async def disconnect(self):
        print("Database disconnected!")
```

When the container bootstraps, it resolves the `Database` singleton and calls `connect()`. On shutdown, it calls `disconnect()`.

## Standalone Hooks

Hooks can also be standalone functions registered on a specific container. Parameters are injected automatically:

```python
from dijay import module, instance

c = instance()

@module.on_bootstrap(c)
async def log_startup(db: Database):
    print(f"App started with {db}")
```

If no container is provided, the hook is registered on the **global container**:

```python
@module.on_bootstrap
async def log_startup(db: Database):
    print(f"App started with {db}")
```

## Sync and Async

Hooks can be synchronous or asynchronous — the container handles both:

```python
@module.on_bootstrap
def sync_hook():
    print("Sync hook!")

@module.on_bootstrap
async def async_hook():
    print("Async hook!")
```

## Triggering Hooks

### Async Context Manager (recommended)

Hooks are triggered automatically when using the container as an async context manager:

```python
async with Container.from_module(AppModule) as container:
    # @module.on_bootstrap hooks have already run here
    ...
# @module.on_shutdown hooks run when exiting the block
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
