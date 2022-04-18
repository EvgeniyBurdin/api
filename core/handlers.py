""" Модуль для обработчиков CRUD.
"""
from datetime import datetime, timezone
from typing import List

from valdec.decorators import async_validate as validate

from .data_classes.params import ArticleCreatedPP, NewArticleDCRB
from .data_classes.results import ArticleDC
from .decorators import only_validate
from .storages import Storage


@only_validate("body", "return")
async def create_article(
    new_article_dcrb: NewArticleDCRB, storage: Storage
) -> ArticleDC:
    """ Создает в хранилище новую запись о статье.
        Возвращает созданную запись.
    """
    new_article_dcrb["created"] = datetime.now(tz=timezone.utc).date()

    return await storage.create(table_name="articles", row=new_article_dcrb)


@only_validate("return")
@validate("created")
async def read_articles(
    storage: Storage, created: ArticleCreatedPP
) -> List[ArticleDC]:
    """ Читает из хранилища статьи и возвращает их.
    """
    filters = {"created": [created]}

    return await storage.read(table_name="articles", filters=filters)
