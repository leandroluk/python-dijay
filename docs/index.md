---
icon: lucide/rocket
---

# 🎧 dijay

**Drop the beat on your dependencies.**

**dijay** is the "remix" your architecture needs: NestJS-style modularity, native async performance, and rigorous typing for Python 3.14+. Less boilerplate, more harmony.

[![ci](https://github.com/leandroluk/python-dijay/actions/workflows/ci.yml/badge.svg)](https://github.com/leandroluk/python-dijay/actions/workflows/ci.yml)
[![coverage](https://codecov.io/gh/leandroluk/python-dijay/graph/badge.svg)](https://codecov.io/gh/leandroluk/python-dijay)
[![release](https://img.shields.io/github/v/release/leandroluk/python-dijay?color=green)](https://github.com/leandroluk/python-dijay/releases)
[![pypi](https://img.shields.io/pypi/v/dijay?color=green)](https://pypi.org/project/dijay)
[![license](https://img.shields.io/github/license/leandroluk/python-dijay)](https://github.com/leandroluk/python-dijay/blob/main/LICENSE)

---

## Features

- **Modular Architecture** — Organize code into `@module`s with `imports`, `providers`, and `exports`.
- **Constructor Injection** — Clean, testable injection via `__init__` and `Annotated`.
- **Flexible Scopes** — `SINGLETON`, `TRANSIENT`, and `REQUEST`.
- **Async Native** — First-class support for asynchronous factories and lifecycle hooks.
- **Custom Providers** — `Provide` dataclass for value, class and factory bindings.
- **Lifecycle Hooks** — `@on_bootstrap` and `@on_shutdown` decorators.
- **Circular Dependency Detection** — Immediate `RuntimeError` on cycles.

## Quick Example

```python
import asyncio
from dijay import Container, injectable, module

@injectable()
class CatsService:
    def get_all(self):
        return ["Meow", "Purr"]

@module(providers=[CatsService], exports=[CatsService])
class CatsModule: ...

@module(imports=[CatsModule])
class AppModule: ...

async def main():
    async with Container.from_module(AppModule) as container:
        service = await container.resolve(CatsService)
        print(service.get_all())

if __name__ == "__main__":
    asyncio.run(main())
```

## Next Steps

- :material-rocket-launch: **[Getting Started](getting-started.md)** — Install and create your first app
- :material-puzzle: **[Modules](guides/modules.md)** — Organize your architecture
- :material-needle: **[Providers](guides/providers.md)** — Custom bindings with `Provide`
- :material-hook: **[Lifecycle Hooks](guides/lifecycle.md)** — Bootstrap and shutdown hooks
- :fontawesome-solid-bolt: **[FastAPI](guides/fastapi.md)** — Integrate with FastAPI
- :material-api: **[API Reference](api.md)** — Full API documentation
