# Scraper & API for HackerNews

This repo has two parts:

1. Scrape data from HackerNews API and store to `my_app/db/data.db`
2. Host API to support hackernews-app

## Scraper:

Takes several command line arguments:

1. `-l` limits running to one instance. This is to prevent running the scraper more than once.
2. `-t` for testing to only scrape the top few results from each type

## Scraper

### SQLite Database

The database created has the following tables:

- `articles`: primary resource for articles and their info eg title, comments, date etc
- `best`: mapping of current rank 1-500 and article id
- `top`: mapping of current rank 1-500 and article id
- `new`: mapping of current rank 1-500 and article id

### Run Scraper

Set the cronjob to run once an hour or at your preferred cadence. Using /bin/sh -c to run in bash and allow scraper to find if it is currently being run.

```/bin/sh -c 'exec {PATH_TO_ENV}/bin/python {PATH_TO_MODULE}/hackernews-api/scrape.py -l'```

## 2. Run API



