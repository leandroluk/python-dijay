import asyncio

import uvicorn
from watchfiles import run_process

from dijay import Container

from .module import AppModule
from .presentation.http.config import HttpConfig
from .presentation.http.server import HttpServer


async def main():
    async with Container.from_module(AppModule) as container:
        server = await container.resolve(HttpServer)
        config = uvicorn.Config(
            server.app,
            host=server.config.host,
            port=server.config.port,
        )
        await uvicorn.Server(config).serve()


config = HttpConfig()

if config.enable_reload:
    run_process("./src", target=lambda: asyncio.run(main()))
else:
    asyncio.run(main())
