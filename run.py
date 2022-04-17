import asyncio

from core.storages import Storage
from core.handlers import create_article, read_article


storage = Storage()


article = asyncio.run(create_article(
    row={"header": "Header", "content": "Content"},
    storage=storage,
))

article = asyncio.run(read_article(
    created="2022-04-17",
    storage=storage,
))

print(article)
