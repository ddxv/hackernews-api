"""API endpoints for serving HN articles publicly.

/articles/{article_id} a specific article
/articles/{article_id}/comments comments for a specific article
/articles/top : one of top, new or best
"""


from typing import Self

from litestar import Controller, Response, get
from litestar.background_tasks import BackgroundTask

from my_app.db.connection import query_article, query_type
from my_app.log_umami import send_page_view
from my_app.models import Article, Articles


class ArticleController(Controller):
    """Holds all article related endpoints."""

    path = "/api/articles"

    @get(path="/{article_id:int}")
    async def get_article(self: Self, article_id: int) -> Article:
        """Handle GET requests for a specific article.

        Args:
        ----
            article_id (int): The id of the article to retrieve.

        Returns:
        -------
            Article: A dictionary representation of the article.
        """
        print(f"GET for {article_id=}")
        df = query_article(article_id)
        mydict: Article = df.set_index("id").to_dict(orient="index")
        return mydict

    @get(path="/list/{list_type:str}")
    async def get_article_list(
        self: Self,
        list_type: str,
        page: int = 1,
        items_per_page: int = 50,
    ) -> Response[Articles]:
        """Handle GET requests for a list of articles of a certain type.

        Args:
        ----
            list_type (str): The type of articles to retrieve.
            page (int, optional): The page number of the articles list. Defaults to 1.
            items_per_page (int, optional): The number of articles per page. Defaults to 50.

        Returns:
        -------
            Articles: A dictionary representation of the list of articles.
        """
        print(f"GET for {list_type=} and {page=}")
        if list_type in ["top", "new", "best"]:
            df = query_type(
                list_type=list_type,
                page_number=page,
                items_per_page=items_per_page,
            )
            df = df.sort_values("rank", ascending=True)
            mydict: Articles = df.set_index("id").to_dict(orient="index")
        return Response(
            mydict,
            background=BackgroundTask(
                send_page_view,
                list_type,
            ),
        )
