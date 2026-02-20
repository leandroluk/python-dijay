import os

from dijay import DynamicModule, module

from .fake import FakeDatabaseModule

modules = [FakeDatabaseModule]


@module(imports=modules, exports=modules)
class DatabaseModule:
    @staticmethod
    def for_root(connection_string: str) -> DynamicModule:
        # example swapping between different database providers by environment variable
        module = {
            "fake": FakeDatabaseModule,
            # any other module
        }[os.getenv("DB_PROVIDER", "fake")]

        return DynamicModule(
            module=DatabaseModule,
            imports=[module],
            exports=[module],
        )
