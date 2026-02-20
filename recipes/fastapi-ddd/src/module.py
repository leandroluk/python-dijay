from dijay import module

from .application import ApplicationModule
from .infrastructure import InfrastructureModule
from .presentation import PresentationModule

modules = [
    ApplicationModule,
    InfrastructureModule,
    PresentationModule,
]


@module(imports=modules, exports=modules)
class AppModule:
    pass
