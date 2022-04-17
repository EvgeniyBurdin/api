import asyncio
import datetime

from core.handlers import create_article, read_article
from core.storages import Storage

storage = Storage()


asyncio.run(create_article(
    row={"header": "Header_1", "content": "Content_1"},
    storage=storage,
))
asyncio.run(create_article(
    row={"header": "Header_2", "content": "Content_2"},
    storage=storage,
))
asyncio.run(create_article(
    row={"header": "Header_3", "content": "Content_3"},
    storage=storage,
))

storage.db["articles"][0]["created"] = datetime.date(2022, 4, 16)

articles = asyncio.run(read_article(
    created="2022-04-17",
    storage=storage,
))

print(articles)
