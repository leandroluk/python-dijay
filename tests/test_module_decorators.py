import pytest

from dijay import instance
from dijay import module as m
from dijay.decorators import on_bootstrap, on_shutdown


@pytest.mark.asyncio
async def test_on_bootstrap_with_container():
    c = instance()
    events = []

    @on_bootstrap(c)
    def boot():
        events.append("boot")

    async with c:
        assert "boot" in events


@pytest.mark.asyncio
async def test_on_bootstrap_container_kwarg():
    c = instance()
    events = []

    @on_bootstrap(container=c)
    def boot():
        events.append("boot")

    async with c:
        assert "boot" in events


@pytest.mark.asyncio
async def test_on_bootstrap_no_args_returns_decorator():
    c = instance()
    events = []

    decorator = on_bootstrap()

    @decorator
    @c.on_bootstrap
    def boot():
        events.append("boot")

    async with c:
        assert "boot" in events


@pytest.mark.asyncio
async def test_on_shutdown_with_container():
    c = instance()
    events = []

    @on_shutdown(c)
    def shut():
        events.append("shut")

    async with c:
        pass

    assert "shut" in events


@pytest.mark.asyncio
async def test_on_shutdown_no_args_returns_decorator():
    c = instance()
    events = []

    decorator = on_shutdown()

    @c.on_shutdown
    @decorator
    def shut():
        events.append("shut")

    async with c:
        pass

    assert "shut" in events


@pytest.mark.asyncio
async def test_module_on_bootstrap_with_container():
    c = instance()
    events = []

    @m.on_bootstrap(c)
    def boot():
        events.append("boot")

    async with c:
        assert "boot" in events


@pytest.mark.asyncio
async def test_module_on_bootstrap_container_kwarg():
    c = instance()
    events = []

    @m.on_bootstrap(container=c)
    def boot():
        events.append("boot")

    async with c:
        assert "boot" in events


@pytest.mark.asyncio
async def test_module_on_shutdown_with_container():
    c = instance()
    events = []

    @m.on_shutdown(c)
    def shut():
        events.append("shut")

    async with c:
        pass

    assert "shut" in events


@pytest.mark.asyncio
async def test_module_on_bootstrap_no_args_returns_decorator():
    c = instance()
    events = []

    decorator = m.on_bootstrap()

    @c.on_bootstrap
    @decorator
    def boot():
        events.append("boot")

    async with c:
        assert "boot" in events


@pytest.mark.asyncio
async def test_module_on_shutdown_container_kwarg():
    c = instance()
    events = []

    @m.on_shutdown(container=c)
    def shut():
        events.append("shut")

    async with c:
        pass

    assert "shut" in events


@pytest.mark.asyncio
async def test_module_on_shutdown_no_args_returns_decorator():
    c = instance()
    events = []

    decorator = m.on_shutdown()

    @c.on_shutdown
    @decorator
    def shut():
        events.append("shut")

    async with c:
        pass

    assert "shut" in events
