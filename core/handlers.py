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
    body["created"] = datetime.datetime.now(
        tz=datetime.timezone.utc
    ).date()

    return await storage.create(table_name="articles", row=body)


@validate_raw("return")
@validate("created", "uq")
async def read_articles(
    storage: Storage, created: datetime.date, uq: ReadArticlesDCA
) -> List[ArticleDC]:
    """ Читает из хранилища статьи и возвращает их.
    """
    filters = {"created": [created]}
    print(uq.header_prefix)

    return await storage.read(table_name="articles", filters=filters)
