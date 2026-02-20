# API Reference

## Container

The core dependency injection container.

```python
from dijay import Container
```

### `Container()`

Creates an empty container with no registered providers.

### `Container.from_module(mod) -> Container`

Creates a container from a module hierarchy. Scans the module tree, registers all providers, and returns a fully configured `Container`.

```python
container = Container.from_module(AppModule)
```

### `container.injectable(token=None, scope=SINGLETON)`

Decorator that registers a class or factory as a provider.

| Parameter | Type          | Default     | Description                                            |
| --------- | ------------- | ----------- | ------------------------------------------------------ |
| `token`   | `Any \| None` | `None`      | Token to register under. Defaults to the class itself. |
| `scope`   | `str`         | `SINGLETON` | Lifetime scope.                                        |

```python
@container.injectable(scope=TRANSIENT)
class EmailSender: ...
```

### `container.register(token, provider, scope=SINGLETON)`

Explicitly bind a provider to a token at runtime.

```python
container.register(Database, FakeDatabase)
```

### `container.resolve(token, id=None) -> T`

Resolve a dependency by token, respecting its scope.

| Parameter | Type             | Description                                   |
| --------- | ---------------- | --------------------------------------------- |
| `token`   | `type[T] \| Any` | The type or key to resolve.                   |
| `id`      | `str \| None`    | Request identifier for `REQUEST` scoped deps. |

Raises `RuntimeError` on circular dependency or unregistered token.

```python
service = await container.resolve(MyService)
```

### `container.call(target, id=None, **kwargs)`

Invoke a callable with dependencies resolved and injected automatically.

```python
result = await container.call(my_function)
```

### `container.on_bootstrap(fn)`

Register a hook to run during `bootstrap()`.

### `container.on_shutdown(fn)`

Register a hook to run during `shutdown()`.

### `container.bootstrap()`

Execute all registered bootstrap hooks in order.

### `container.shutdown()`

Execute all shutdown hooks and clear internal caches.

### Async Context Manager

The container supports `async with` for automatic lifecycle management:

```python
async with Container.from_module(AppModule) as container:
    # @on_bootstrap hooks ran
    ...
# @on_shutdown hooks ran
```

---

## Module-Level Shortcuts

These are shortcuts that operate on a global `Container` instance. Ideal for simple apps:

```python
from dijay import injectable, register, resolve, on_bootstrap, on_shutdown, instance
```

| Function       | Description                                               |
| -------------- | --------------------------------------------------------- |
| `injectable`   | Decorator to register a provider on the global container. |
| `register`     | Bind a provider to a token on the global container.       |
| `resolve`      | Resolve a dependency from the global container.           |
| `on_bootstrap` | Register a bootstrap hook on the global container.        |
| `on_shutdown`  | Register a shutdown hook on the global container.         |
| `instance()`   | Create a new, independent `Container`.                    |

---

## Provide

Dataclass for custom provider registration within modules.

```python
from dijay import Provide
```

| Attribute     | Type               | Default     | Description                   |
| ------------- | ------------------ | ----------- | ----------------------------- |
| `token`       | `Any`              | —           | The token to bind.            |
| `use_value`   | `Any`              | `None`      | Binds a constant value.       |
| `use_class`   | `Any`              | `None`      | Binds a class to instantiate. |
| `use_factory` | `Callable \| None` | `None`      | Binds a callable to invoke.   |
| `scope`       | `str`              | `SINGLETON` | Lifetime scope.               |

```python
@module(providers=[
    Provide("DB_URL", use_value="postgresql://localhost/mydb"),
    Provide(Cache, use_class=RedisCache),
    Provide(HttpClient, use_factory=create_http_client),
])
class InfraModule: ...
```

---

## Inject

Marker used in `Annotated` type hints to specify a custom injection token.

```python
from dijay import Inject
```

```python
def __init__(self, url: Annotated[str, Inject("DB_URL")]): ...
```

---

## module

Decorator that marks a class as a Module.

```python
from dijay import module
```

| Parameter   | Type        | Default | Description                                |
| ----------- | ----------- | ------- | ------------------------------------------ |
| `providers` | `list[Any]` | `[]`    | Providers to register within this module.  |
| `imports`   | `list[Any]` | `[]`    | Imported modules that export providers.    |
| `exports`   | `list[Any]` | `[]`    | Providers to export to importing modules.  |
| `globals`   | `bool`      | `False` | If `True`, exports are available globally. |

---

## DynamicModule

`TypedDict` returned by static methods to configure dynamic modules.

```python
from dijay import DynamicModule
```

| Key         | Type        | Description                             |
| ----------- | ----------- | --------------------------------------- |
| `module`    | `Any`       | The module class being configured.      |
| `providers` | `list[Any]` | Additional providers to register.       |
| `imports`   | `list[Any]` | Additional modules to import.           |
| `exports`   | `list[Any]` | Additional providers to export.         |
| `globals`   | `bool`      | Whether exports are globally available. |

---

## Scope Constants

```python
from dijay import SINGLETON, TRANSIENT, REQUEST
```

| Constant    | Value         | Description                                    |
| ----------- | ------------- | ---------------------------------------------- |
| `SINGLETON` | `"singleton"` | Single instance shared across all resolutions. |
| `TRANSIENT` | `"transient"` | New instance on every `resolve()` call.        |
| `REQUEST`   | `"request"`   | One instance per request ID.                   |
