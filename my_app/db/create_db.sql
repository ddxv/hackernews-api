PRAGMA foreign_keys = ON;

-- articles definition

CREATE TABLE "articles" (
id INTEGER PRIMARY KEY,
deleted BOOLEAN DEFAULT FALSE,
type TEXT CHECK(type IN ("job", "story", "comment", "poll", "pollopt")),
by TEXT,
time INTEGER, -- Assuming you want to store Unix Time as integer
text TEXT, -- Storing HTML content
dead BOOLEAN DEFAULT FALSE,
parent INTEGER REFERENCES articles(id), -- Self-referencing foreign key for parent comments/stories
poll INTEGER REFERENCES articles(id), -- Self-referencing foreign key for associated poll
url TEXT,
domain TEXT,
score INTEGER,
title TEXT, -- Storing HTML content
descendants INTEGER, -- in the case of stories or polls the comment count
crawled_at DATETIME
);

CREATE INDEX "ix_articles_id" ON "articles" ("id");



CREATE TABLE "top" (
"rank" INTEGER PRIMARY KEY,
"id" INTEGER UNIQUE,
"crawled_at" DATETIME,
    FOREIGN KEY(id) REFERENCES articles(id)
ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE "best" (
"rank" INTEGER PRIMARY KEY,
"id" INTEGER UNIQUE,
"crawled_at" DATETIME,
    FOREIGN KEY(id) REFERENCES articles(id)
    ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE "new" (
"rank" INTEGER PRIMARY KEY,
"id" INTEGER UNIQUE,
"crawled_at" DATETIME,
    FOREIGN KEY(id) REFERENCES articles(id)
    ON DELETE CASCADE ON UPDATE CASCADE
);