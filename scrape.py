import datetime

import pandas as pd
import requests

from connection import connection, upsert_df

BASE_URL = "https://hacker-news.firebaseio.com/v0/"
STORY_TYPES = ["top", "best", "new"]
TOP_STORIES = "topstories.json"
BEST_STORIES = "beststories.json"
NEW_STORIES = "newstories.json"


def get_article(id: str) -> dict:
    response = requests.get(BASE_URL + f"item/{id}.json")
    article: dict = response.json()
    return article


def get_articles(my_type: str) -> list:
    response = requests.get(BASE_URL + f"{my_type}stories.json")
    article_ids = response.json()
    articles = list()
    i = 0
    for id in article_ids:
        article_info = get_article(id)
        articles.append(article_info)
        if i > 10:
            break
        i += 1
        print(f"{type}: {i}/{len(article_ids)}")
    return articles


for type in STORY_TYPES:
    articles = get_articles(type)
    articles_df = pd.DataFrame(articles)
    articles_df["crawled_at"] = datetime.datetime.utcnow()
    comments_df = articles_df[["id", "kids"]].copy()
    articles_df = articles_df.drop("kids", axis=1)
    # Upset the Articles which are the primary key first
    upsert_df(
        df=articles_df,
        table_name="articles",
        database_connection=connection,
        key_columns=["id"],
        insert_columns=articles_df.columns.tolist(),
    )

    # Upset the lists they belong to here
    upsert_df(
        df=articles_df[["id"]],
        table_name=type,
        database_connection=connection,
        key_columns=["id"],
        insert_columns=["id"],
    )
