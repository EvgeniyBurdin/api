""" Модуль для обработчиков CRUD.
"""
import datetime
from typing import List

from storages import Storage

from .data_classes.params import NewArticleDC, ReadArticlesDCA
from .data_classes.results import ArticleDC
from .decorators import validate, validate_raw


@validate_raw("body", "return")
async def create_article(
    body: NewArticleDC, storage: Storage
) -> ArticleDC:
    """ Создает в хранилище новую запись о статье.
        Возвращает созданную запись.
    """
    if "created" in body:
        body["created"] = datetime.datetime.strptime(
            body["created"], '%Y-%m-%d'
        ).date()
    else:
        body["created"] = datetime.datetime.now(
            tz=datetime.timezone.utc
        ).date()

    return await storage.create(table_name="articles", row=body)


@validate_raw("return")
@validate("created", "query")
async def read_articles(
    storage: Storage, created: datetime.date, query: ReadArticlesDCA
) -> List[ArticleDC]:
    """ Читает из хранилища статьи и возвращает их.
    """
    filters = {"created": [created]}
    print(query.header_prefix)

    return await storage.read(table_name="articles", filters=filters)
