import asyncio

from core.storages import Storage
from core.handlers import create_article


storage = Storage()


article = asyncio.run(create_article(
    row={"header": "Header", "content": "Content"},
    storage=storage,
))

print(article)
print(storage.db)
