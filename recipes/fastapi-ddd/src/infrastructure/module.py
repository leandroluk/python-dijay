from dijay import module

from .database import DatabaseModule

modules = [
    DatabaseModule,
]


@module(imports=modules, exports=modules)
class InfrastructureModule:
    pass
