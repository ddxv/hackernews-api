from litestar import Litestar

from my_app.controllers.article import ArticleController

app = Litestar(route_handlers=[ArticleController])
