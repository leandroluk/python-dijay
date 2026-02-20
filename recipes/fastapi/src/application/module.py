from dijay import module

from .todo import TodoModule

modules = [TodoModule]


@module(imports=modules, exports=modules)
class ApplicationModule:
    pass
