"""API models and types."""

from dataclasses import dataclass


@dataclass
class Article:
    """A HackerNews article."""

    id: int
    rank: int
    deleted: int | None  # Using Optional since it can be missing
    type: str
    by: str
    time: int
    text: str | None  # Optional since it can be None
    dead: int | None  # Using Optional since it can be missing
    parent: int | None  # Optional since it can be None
    poll: int | None  # Optional since it can be None
    url: str
    score: int
    title: str
    descendants: int
    crawled_at: str
    # If there are other keys in some dictionaries, you would add them here as attributes


@dataclass
class Articles:
    """A List of HackerNews articles."""

    articles: list[Article]
