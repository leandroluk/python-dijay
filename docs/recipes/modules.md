# Modules

Modules are the building blocks of a **dijay** application. They encapsulate providers and manage dependencies between different parts of your system.

## Defining a Module

Use the `@module` decorator to define a module:

```python
from dijay import module

@module(
    imports=[DatabaseModule],
    providers=[UserService, UserRepository],
    exports=[UserService],
)
class UserModule: ...
```

| Parameter   | Description                                       |
| ----------- | ------------------------------------------------- |
| `imports`   | Modules whose exports become available here.      |
| `providers` | Classes or `Provide` entries to register.         |
| `exports`   | Providers to make available to importing modules. |
| `globals`   | If `True`, exports are available globally.        |

## Module Hierarchy

Modules form a tree. The root module imports feature modules, which import infrastructure modules:

```
AppModule
├── UserModule
│   └── DatabaseModule
├── AuthModule
│   └── DatabaseModule
└── HttpModule
```

```python
@module(imports=[UserModule, AuthModule, HttpModule])
class AppModule: ...
```

## Dynamic Modules

For conditional configuration (e.g., swapping implementations by environment), use a static method that returns a `DynamicModule`:

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

The `DynamicModule` is a `TypedDict` with the following keys:

| Key         | Type        | Description                             |
| ----------- | ----------- | --------------------------------------- |
| `module`    | `Any`       | The module class being configured.      |
| `providers` | `list[Any]` | Additional providers to register.       |
| `imports`   | `list[Any]` | Additional modules to import.           |
| `exports`   | `list[Any]` | Additional providers to export.         |
| `globals`   | `bool`      | Whether exports are globally available. |

!!! tip
    The default `@module` metadata serves as fallback. The `DynamicModule` returned by `for_root()` overrides or extends it at container creation time.
