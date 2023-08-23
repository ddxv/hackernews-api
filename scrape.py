import argparse
import datetime
import os

import pandas as pd
import requests

from my_app.db.connection import connection, upsert_df

BASE_URL = "https://hacker-news.firebaseio.com/v0/"
STORY_TYPES = ["top", "best", "new"]
TOP_STORIES = "topstories.json"
BEST_STORIES = "beststories.json"
NEW_STORIES = "newstories.json"


def script_has_process() -> bool:
    already_running = False
    processes = [x for x in os.popen("ps aux ww")]
    my_processes = [
        x for x in processes if "/adscrawler/main.py" in x and "/bin/sh" not in x
    ]
    if len(my_processes) > 1:
        print(f"Already running {my_processes}")
        already_running = True
    return already_running


def manage_cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l",
        "--limit-processes",
        help="If included prevent running if script already running",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "-t",
        "--test",
        help="If included only run a few records",
        default=False,
        action="store_true",
    )
    args, leftovers = parser.parse_known_args()
    if args.limit_processes and script_has_process():
        print("Script already running, exiting")
        quit()
    return args


def get_article(id: str) -> dict:
    response = requests.get(BASE_URL + f"item/{id}.json")
    article: dict = response.json()
    return article


def get_articles(my_type: str, max_count: int) -> list:
    response = requests.get(BASE_URL + f"{my_type}stories.json")
    # Careful, these are in an ordered list!
    article_ids = response.json()
    articles = list()
    i = 1
    for id in article_ids:
        print(f"{my_type}: {i}/{len(article_ids)}")
        article_info = get_article(id)
        # This is the rank of my_type, ie Rank 1 on Top Stories
        article_info["rank"] = i
        article_info["crawled_at"] = datetime.datetime.utcnow()

        if "kids" not in article_info.keys():
            article_info["kids"] = []

        articles.append(article_info)
        if i >= max_count:
            break
        i += 1
    return articles


def main(args: argparse.Namespace) -> None:
    if args.test:
        max_count = 5
    else:
        max_count = 500
    for my_type in STORY_TYPES:
        articles = get_articles(my_type, max_count)
        articles_df = pd.DataFrame(articles)
        # comments_df = articles_df[["id", "kids", "crawled_at"]].copy()
        type_df = articles_df[["rank", "id", "crawled_at"]].copy()
        articles_df = articles_df.drop(["kids", "rank"], axis=1)
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
            df=type_df[["rank", "id", "crawled_at"]],
            table_name=my_type,
            database_connection=connection,
            key_columns=["rank"],
            insert_columns=["rank", "id"],
        )


if __name__ == "__main__":
    args = manage_cli_args()
    main(args)
