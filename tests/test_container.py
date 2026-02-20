from typing import Annotated

import pytest

from dijay import (
    REQUEST,
    TRANSIENT,
    Inject,
    injectable,
    instance,
    resolve,
)


class Base:
    pass


@injectable(Base)
class Implementation(Base):
    pass


@injectable()
class Service:
    pass


@injectable(scope=TRANSIENT)
class TransientService:
    pass


@injectable(scope=REQUEST)
class RequestService:
    pass


@injectable()
async def async_factory() -> str:

    return "async_ready"


@pytest.mark.asyncio
async def test_singleton():

    s1 = await resolve(Service)

    s2 = await resolve(Service)

    assert s1 is s2


@pytest.mark.asyncio
async def test_transient():

    t1 = await resolve(TransientService)

    t2 = await resolve(TransientService)

    assert t1 is not t2


@pytest.mark.asyncio
async def test_request_scope():

    r1 = await resolve(RequestService, id="req_a")

    r2 = await resolve(RequestService, id="req_a")

    r3 = await resolve(RequestService, id="req_b")

    assert r1 is r2

    assert r1 is not r3


@pytest.mark.asyncio
async def test_abstract_injection():

    obj = await resolve(Base)

    assert isinstance(obj, Implementation)


@pytest.mark.asyncio
async def test_async_factory_resolution():

    val = await resolve(str)
    assert val == "async_ready"


@pytest.mark.asyncio
async def test_constructor_injection():

    @injectable()
    class App:

        def __init__(self, service: Service, data: str):

            self.service = service

            self.data = data

    app = await resolve(App)

    assert isinstance(app.service, Service)
    assert app.data == "async_ready"


@pytest.mark.asyncio
async def test_annotated_token_injection():
    c = instance()

    @c.injectable("API_URL")
    def url_factory() -> str:

        return "http://localhost"

    @c.injectable()
    class Client:

        def __init__(self, url: Annotated[str, Inject("API_URL")]):

            self.url = url

    client = await c.resolve(Client)

    assert client.url == "http://localhost"


@pytest.mark.asyncio
async def test_lifecycle_context_manager():
    c = instance()

    events = []

    @c.on_bootstrap
    async def boot():

        events.append("boot")

    @c.on_shutdown
    def shut():

        events.append("shut")

    async with c:

        assert "boot" in events

        assert "shut" not in events

    assert "shut" in events
