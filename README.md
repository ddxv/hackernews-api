# Scraper & API for HackerNews

This repo has two parts:

1. Scrape data from HackerNews API and store to `my_app/db/data.db`
2. Host API to support [hackernews-app](<https://github.com/ddxv/hackernews-app>)

## Scraper

Takes several command line arguments:

1. `-l` limits running to one instance. This is to prevent running the scraper more than once.
2. `-t` for testing to only scrape the top few results from each type

### SQLite Database

The database created has the following tables:

- `articles`: primary resource for articles and their info eg title, comments, date etc
- `best`: mapping of current rank 1-500 and article id
- `top`: mapping of current rank 1-500 and article id
- `new`: mapping of current rank 1-500 and article id

### Run Scraper

Set the cronjob to run once an hour or at your preferred cadence. Using /bin/sh -c to run in bash and allow scraper to find if it is currently being run.

```/bin/sh -c 'exec {PATH_TO_ENV}/bin/python {PATH_TO_MODULE}/hackernews-api/scrape.py -l'```

## API Service

This API is currently used for returning lists of current Hacker News articles after being scraped from the official HackerNews API.

## Setup

- Current setup is based on Python3.11
- pip install dependencies, found in pyproject.toml: `pip install "litestar[standard]" pydantic pandas requests tldextract gunicorn uvicorn`

## Running Locally

- To run locally for testing use
  - `$ gunicorn -k uvicorn.workers.UvicornWorker app:app`

## Running in production

To setup the API for production requires 3 files outside of this project to be set. Two systemctl systemd unit files: service & socket. The third file is the nginx configuration to point HTTP traffic to the unix socket.

### Socket Unit File

location: `/etc/systemd/system/hackernews-api.socket`

```Shell
[Unit]
Description=Gunicorn socket

[Socket]
ListenStream=/run/hackernews-api.sock
User=www-data

[Install]
WantedBy=sockets.target
```

### Service Unit file

location: `/etc/systemd/system/hackernews-api.service`

```Shell
[Unit]
Description=Gunicorn instance to serve HackerNews API
After=network.target

[Service]
Type=Notify
User=ubuntu
Group=ubuntu
RuntimeDirectory=gunicorn
WorkingDirectory=/home/ubuntu/hackernews-api
Environment="PROD=True" /home/ubuntu/venvs/hackernews-env/bin
ExecStart=/home/ubuntu/venv/hackernews-env/bin/gunicorn -k uvicorn.workers.UvicornWorker --workers 1 --bind unix:hackernews-api.sock -m 007 app:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

### Nginx config file

This is wherever you have your nginx configuration set, possibly sites-available `/etc/nginx/sites-available/hackernews-api` or `/etc/nginx/conf.d/hackerews-api.conf`

`hackernews-api`

```Nginx
server {
    listen 80;
    client_max_body_size 2M;

    location /api {
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-NginX-Proxy true;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_pass http://unix:/run/hackernews-api.sock;
    }
}
```

If you put your nginx configuration in a new file in sites-available, be sure to link to sites-enabled to start:

```Shell
sudo ln -s /etc/nginx/sites-available/hackernews-api /etc/nginx/sites-enabled/hackernews-api
sudo systemctl restart nginx.service 
```

## Start the service and socket

- `systemctl enable hackernews-api.socket` to automatically start socket on server reboot
- `sudo systemctl start hackernews-api.socket` star
- `sudo systemctl status hackernews-api` to check status

## Check your API endpoints

try visiting example.com/api/articles/list/top

## Troubleshooting

Checking your local API docs:

`http://127.0.0.1:8000/api/docs`

Restarting Unit service

- `sudo systemctl stop hackernews-api`
- `sudo systemctl start hackernews-api`
