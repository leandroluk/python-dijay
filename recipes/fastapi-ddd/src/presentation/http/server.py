from fastapi import FastAPI

from dijay import injectable

from .config import HttpConfig
from .todo import router as todo_router


@injectable()
class HttpServer:
    config: HttpConfig
    app: FastAPI

    def __init__(self, config: HttpConfig):
        self.config = config
        self.app = FastAPI(
            title="Todo API",
            version="0.0.1",
            docs_url=f"{self.config.path}docs",
            redoc_url=f"{self.config.path}redoc",
        )
        self.app.openapi = self.custom_openapi
        self.apply_routes()

    def custom_openapi(self):
        if self.app.openapi_schema:
            return self.app.openapi_schema

        from fastapi.openapi.utils import get_openapi

        openapi_schema = get_openapi(
            title=self.config.title,
            version=self.config.version,
            description=self.config.description,
            openapi_version=self.app.openapi_version,
            routes=self.app.routes,
        )

        # Remove 422 validation errors from responses
        for path_data in openapi_schema.get("paths", {}).values():
            for method_data in path_data.values():
                responses = method_data.get("responses", {})
                if "422" in responses:
                    del responses["422"]

        # Remove default validation schemas
        for schema in ["ValidationError", "HTTPValidationError"]:
            openapi_schema.get("components", {}).get("schemas", {}).pop(schema, None)

        self.app.openapi_schema = openapi_schema
        return self.app.openapi_schema

    def apply_routes(self):
        router_list = [
            todo_router,
        ]
        for router in router_list:
            self.app.include_router(router, prefix=self.config.path.rstrip("/"))
