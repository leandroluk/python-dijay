from dijay import module

from .config import HttpConfig
from .server import HttpServer

providers = [HttpConfig, HttpServer]


@module(providers=providers, exports=providers)
class HttpModule:
    pass
