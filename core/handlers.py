""" Модуль для обработчиков CRUD.
"""
import datetime
from typing import List

from valdec.decorators import async_validate as validate

from .data_classes.params import ArticleCreatedDatePP, CreateArticleDCRB
from .data_classes.results import ArticleDC
from .decorators import only_validate
from .storages import Storage


@only_validate("body", "return")
async def create_article(
    body: CreateArticleDCRB, storage: Storage
) -> ArticleDC:
    """ Создает в хранилище новую запись о статье.
        Возвращает созданную запись.
    """
    body["created"] = datetime.date.today()

    return await storage.create(table_name="articles", row=body)


@only_validate("return")
@validate("created")
async def read_articles(
    storage: Storage, created: ArticleCreatedDatePP
) -> List[ArticleDC]:
    """ Читает из хранилища статьи и возвращает их.
    """
    filters = {"created": [created]}

    return await storage.read(table_name="articles", filters=filters)
