import pytest

from dijay import instance
from dijay import module as m


@pytest.mark.asyncio
async def test_on_bootstrap_method_decoration():
    c = instance()
    events = []

    @c.injectable()
    class Service:
        @m.on_bootstrap
        async def boot(self):
            events.append("boot")

    async with c:
        assert "boot" in events


@pytest.mark.asyncio
async def test_on_shutdown_method_decoration():
    c = instance()
    events = []

    @c.injectable()
    class Service:
        @m.on_shutdown
        def shut(self):
            events.append("shut")

    async with c:
        await c.resolve(Service)

    assert "shut" in events
