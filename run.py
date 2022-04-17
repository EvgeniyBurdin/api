import asyncio
import datetime

from core.handlers import create_article, read_articles
from core.storages import Storage

storage = Storage()


asyncio.run(create_article(
    body={"header": "Header_1", "content": "Content_1"},
    storage=storage,
))
asyncio.run(create_article(
    body={"header": "Header_2", "content": "Content_2"},
    storage=storage,
))
asyncio.run(create_article(
    body={"header": "Header_3", "content": "Content_3"},
    storage=storage,
))

storage.db["articles"][0]["created"] = datetime.date(2022, 4, 16)

articles = asyncio.run(read_articles(
    created="2022-04-17",
    storage=storage,
))

print(articles)
