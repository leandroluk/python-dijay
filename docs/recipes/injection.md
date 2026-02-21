# Injection

This guide covers the different ways to inject dependencies using **dijay**.

## Automatic Constructor Injection

The container inspects `__init__` type hints and resolves dependencies automatically:

```python
from dijay import injectable

@injectable()
class UserService:
    def __init__(self, repo: UserRepository, email: EmailService):
        self.repo = repo
        self.email = email
```

When `UserService` is resolved, the container will:

1. Look up `UserRepository` and `EmailService` in the registry.
2. Resolve them (recursively resolving their dependencies).
3. Pass them to `UserService.__init__`.

## Token Injection with `Inject`

When the type hint alone isn't enough (e.g., injecting a `str` value), use `Annotated` with `Inject`:

```python
from typing import Annotated
from dijay import Inject, injectable

@injectable()
class DatabaseConnection:
    def __init__(
        self,
        url: Annotated[str, Inject("DB_URL")],
        pool_size: Annotated[int, Inject("DB_POOL_SIZE")],
    ):
        self.url = url
        self.pool_size = pool_size
```

The `Inject("DB_URL")` marker tells the container to resolve the `"DB_URL"` token instead of trying to resolve `str`.

## Optional Dependencies

Dependencies with `Optional` (or `X | None`) type hints are treated as optional. If the token is not registered, `None` is injected instead of raising an error:

```python
@injectable()
class NotificationService:
    def __init__(self, sms: SmsGateway | None = None):
        self.sms = sms
```

## Request-Scoped Injection

When using `REQUEST` scope, pass an `id` parameter to `resolve` to group dependencies by request:

```python
instance = await container.resolve(RequestContext, id="request-123")
```

All `REQUEST`-scoped dependencies resolved with the same `id` will share instances within that request.

## Circular Dependency Detection

**dijay** monitors the resolution stack. If a cycle is detected (e.g., `A → B → A`), a `RuntimeError` is raised immediately:

```python
@injectable()
class A:
    def __init__(self, b: B): ...

@injectable()
class B:
    def __init__(self, a: A): ...

# RuntimeError: Circular dependency: <class 'A'>
```

!!! tip
    To break circular dependencies, consider using factory functions or restructuring your modules.
