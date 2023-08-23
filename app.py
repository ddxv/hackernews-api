from litestar import Litestar
from litestar.openapi import OpenAPIConfig, OpenAPIController

from my_app.controllers.article import ArticleController


class MyOpenAPIController(OpenAPIController):
    path = "/api/docs"


app = Litestar(
    route_handlers=[ArticleController],
    openapi_config=OpenAPIConfig(
        title="HackerNews API", version="1.0.0", openapi_controller=MyOpenAPIController
    ),
)
