import asyncio

import uvicorn

from dijay import Container

from .module import AppModule
from .presentation.http import HttpServer
from .presentation.http.config import HttpConfig


def dev():
    # Factory for uvicorn reload.
    # Instantiate HttpServer manually to return app synchronously.
    # Async initialization (bootstrap) is deferred to startup event.
    container = Container.from_module(AppModule)

    config = HttpConfig()
    server = HttpServer(config, container)

    async def on_startup():
        await container.bootstrap()

    server.app.add_event_handler("startup", on_startup)
    server.app.add_event_handler("shutdown", container.shutdown)

    return server.app


async def main():
    # Production/Standard entry point
    async with Container.from_module(AppModule) as container:
        http_server = await container.resolve(HttpServer)

        config = uvicorn.Config(
            http_server.app,
            host=http_server.config.host,
            port=http_server.config.port,
        )
        server = uvicorn.Server(config)
        await server.serve()


def run():
    config = HttpConfig()

    if config.enable_reload:
        uvicorn.run(
            "src.main:dev",
            host=config.host,
            port=config.port,
            factory=True,
            reload=True,
        )
    else:
        asyncio.run(main())


if __name__ == "__main__":
    run()
