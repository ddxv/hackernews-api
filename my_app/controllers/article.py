from litestar import Controller, get

from my_app.db.connection import query_article, query_type
from my_app.models import Article, Articles

"""
/articles/{article_id} a specific article
/articles/{article_id}/comments comments for a specific article
/articles/top : one of top, new or best
"""


class ArticleController(Controller):
    path = "/api/articles"

    @get(path="/{article_id:int}")
    async def get_article(self, article_id: int) -> Article:
        """
        Handles a GET request for a specific article.

        Args:
            article_id (int): The id of the article to retrieve.

        Returns:
            Article: A dictionary representation of the article.
        """
        print(f"GET for {article_id=}")
        df = query_article(article_id)
        mydict: Article = df.set_index("id").to_dict(orient="index")
        return mydict

    @get(path="/list/{type:str}")
    async def get_article_list(
        self, type: str, page: int = 1, items_per_page: int = 50
    ) -> Articles:
        """
        Handles a GET request for a list of articles of a certain type.

        Args:
            type (str): The type of articles to retrieve.
            page (int, optional): The page number of the articles list. Defaults to 1.
            items_per_page (int, optional): The number of articles per page. Defaults to 50.

        Returns:
            Articles: A dictionary representation of the list of articles.
        """
        print(f"GET for {type=} and {page=}")
        if type in ["top", "new", "best"]:
            df = query_type(type=type, page_number=page, items_per_page=items_per_page)
            df = df.sort_values("rank", ascending=True)
            mydict: Articles = df.set_index("id").to_dict(orient="index")
        return mydict
