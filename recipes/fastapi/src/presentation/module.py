from dijay import module

from .http import HttpModule

modules = [HttpModule]


@module(imports=modules, exports=modules)
class PresentationModule:
    pass
