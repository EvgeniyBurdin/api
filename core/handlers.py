""" Модуль для обработчиков CRUD.
"""
from datetime import datetime, timezone
from typing import List

from .data_classes.params import ArticleCreatedPP, NewArticleDCRB
from .data_classes.results import ArticleDC
from .decorators import validate, validate_raw
from .storages import Storage


@validate_raw("body", "return")
async def create_article(
    new_article: NewArticleDCRB, storage: Storage
) -> ArticleDC:
    """ Создает в хранилище новую запись о статье.
        Возвращает созданную запись.
    """
    new_article["created"] = datetime.now(tz=timezone.utc).date()

    return await storage.create(table_name="articles", row=new_article)


@validate_raw("return")
@validate("created")
async def read_articles(
    storage: Storage, created: ArticleCreatedPP
) -> List[ArticleDC]:
    """ Читает из хранилища статьи и возвращает их.
    """
    filters = {"created": [created]}

    return await storage.read(table_name="articles", filters=filters)
