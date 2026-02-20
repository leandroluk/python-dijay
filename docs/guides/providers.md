# Providers

Providers are the core of dependency injection. They define **what** gets created and **how**.

## `@injectable` Decorator

The simplest way to register a provider is with `@injectable`:

```python
from dijay import injectable

@injectable()
class EmailService:
    def send(self, to: str, body: str) -> None: ...
```

By default, the class itself is used as the injection token with `SINGLETON` scope.

### Abstract Tokens

You can pass an abstract class as a token to register a concrete implementation under the abstract type. This enables **dependency inversion**:

```python
from abc import ABC, abstractmethod
from dijay import injectable

class Database(ABC):
    @abstractmethod
    async def query(self, sql: str) -> list: ...

@injectable(Database)
class PostgresDatabase(Database):
    async def query(self, sql: str) -> list: ...
```

Any provider that depends on `Database` will automatically receive the `PostgresDatabase` instance.

### Scopes

Control the lifetime of instances with the `scope` parameter:

```python
from dijay import injectable, SINGLETON, TRANSIENT, REQUEST

@injectable(scope=SINGLETON)   # One instance for the entire app (default)
class ConfigService: ...

@injectable(scope=TRANSIENT)   # New instance on every resolution
class RequestLogger: ...

@injectable(scope=REQUEST)     # One instance per request ID
class RequestContext: ...
```

| Scope       | Description                                         |
| ----------- | --------------------------------------------------- |
| `SINGLETON` | Single shared instance across all resolutions.      |
| `TRANSIENT` | New instance created on every `resolve()` call.     |
| `REQUEST`   | One instance per request ID, shared within request. |

## `Provide` Dataclass

For more control, use `Provide` to register values, classes, or factories in a module:

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

### `use_value`

Bind any constant value (strings, numbers, config objects):

```python
Provide("API_KEY", use_value="sk-abc123")
```

### `use_class`

Bind a concrete class to an abstract token:

```python
Provide(Cache, use_class=RedisCache)
```

### `use_factory`

Bind a factory function. The function's parameters are injected automatically:

```python
async def create_http_client(config: AppConfig) -> HttpClient:
    return HttpClient(base_url=config.api_url)

Provide(HttpClient, use_factory=create_http_client)
```

## Constructor Injection

Dependencies are injected via `__init__` parameters. The container inspects type hints and resolves them automatically:

```python
@injectable()
class OrderService:
    def __init__(self, db: Database, email: EmailService):
        self.db = db
        self.email = email
```

### `Inject` Marker

Use `Annotated` with `Inject` to decouple the type hint from the injection token:

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

This resolves `"DB_URL"` from the container instead of trying to resolve `str`.
