import asyncio
from typing import Annotated, Any

import pytest

from dijay import Container, Inject, injectable, instance, on_bootstrap, on_shutdown


@pytest.mark.asyncio
async def test_method_lifecycle_hooks():
    c = instance()
    events = []

    @c.injectable()
    class Service:
        @on_bootstrap
        async def boot(self):
            events.append("boot_started")
            await asyncio.sleep(0.01)
            events.append("boot_done")

        @on_shutdown
        def shut(self):
            events.append("shut")

    async with c:
        assert "boot_done" in events
        assert "shut" not in events

    assert "shut" in events


@pytest.mark.asyncio
async def test_method_hooks_with_injection():
    c = instance()
    events = []

    @c.injectable()
    class Dep:
        pass

    @c.injectable()
    class Service:
        @on_bootstrap
        async def boot(self, dep: Dep):
            assert isinstance(dep, Dep)
            events.append("boot")

    async with c:
        pass

    assert "boot" in events


@pytest.mark.asyncio
async def test_standalone_hooks_still_work():
    c = instance()
    events = []

    @c.on_bootstrap
    def boot():
        events.append("boot")

    async with c:
        pass

    assert "boot" in events


@pytest.mark.asyncio
async def test_register_with_lifecycle_hooks():
    c = instance()
    events = []

    class ManualService:
        @on_bootstrap
        def init(self):
            events.append("init")

        @on_shutdown
        async def close(self):
            events.append("close")

    c.register(ManualService, ManualService)

    async with c:
        assert "init" in events

    assert "close" in events


@pytest.mark.asyncio
async def test_shutdown_skips_uncreated_singletons():
    c = instance()
    events = []

    @c.injectable()
    class UnusedService:
        @on_shutdown
        def shut(self):
            events.append("shut")

    # We start and stop without ever resolving UnusedService
    async with c:
        pass

    assert "shut" not in events


@pytest.mark.asyncio
async def test_multiple_lifecycle_methods():
    c = instance()
    events = []

    @c.injectable()
    class MultiService:
        @on_bootstrap
        def boot1(self):
            events.append("boot1")

        @on_bootstrap
        def boot2(self):
            events.append("boot2")

    async with c:
        assert "boot1" in events
        assert "boot2" in events


class GlobalService:
    def method(self):
        pass


@pytest.mark.asyncio
async def test_hook_skip_logic():
    c = instance()

    # Manually add a "method" to hooks to trigger the 'continue'
    # Use a class defined at module level to avoid '<locals>'
    c._bootstrap_hooks.append(GlobalService.method)
    c._shutdown_hooks.append(GlobalService.method)

    async with c:
        pass  # Should skip GlobalService.method and not crash


@pytest.mark.asyncio
async def test_async_shutdown_hook():
    c = instance()
    events = []

    @c.on_shutdown
    async def shut():
        events.append("shut")

    async with c:
        pass

    assert "shut" in events


@pytest.mark.asyncio
async def test_unregistered_class_auto_resolve_in_lifecycle():
    c = instance()

    class Standalone:
        pass

    obj = await c.resolve(Standalone)
    assert isinstance(obj, Standalone)


@pytest.mark.asyncio
async def test_any_and_optional_in_injectable():
    c = instance()

    @c.injectable()
    class Service:
        def __init__(self, x: Any = 1, y: str | None = None):
            self.x = x
            self.y = y

    s = await c.resolve(Service)
    assert s.x == 1
    assert s.y is None


@pytest.mark.asyncio
async def test_annotated_without_inject_in_lifecycle():
    c = instance()

    @c.injectable()
    class Service:
        def __init__(self, x: Annotated[int, "metadata"] = 10):
            self.x = x

    s = await c.resolve(Service)
    # It tries to resolve int, which is a class, returns 0
    assert s.x == 0


@pytest.mark.asyncio
async def test_circular_dependency_in_hook():
    c = instance()

    @c.injectable()
    class A:
        def __init__(self, b: B):
            pass

    @c.injectable()
    class B:
        def __init__(self, a: A):
            pass

    @c.on_bootstrap
    async def boot(a: A):
        pass

    with pytest.raises(RuntimeError, match="Circular dependency"):
        async with c:
            pass


@pytest.mark.asyncio
async def test_unregistered_token_in_hook():
    c = instance()

    @c.on_bootstrap
    async def boot(missing: Annotated[str, Inject("unknown")]):
        pass

    with pytest.raises(RuntimeError, match="não registrado"):
        async with c:
            pass


@pytest.mark.asyncio
async def test_lifecycle_with_modules():
    from dijay import module

    events = []

    @injectable()
    class Service:
        @on_bootstrap
        def boot(self):
            events.append("boot")

    @module(providers=[Service])
    class AppModule:
        pass

    c = Container.from_module(AppModule)
    async with c:
        assert "boot" in events
