""" Модуль для обработчиков CRUD.
"""
import datetime
from typing import List, Optional

from valdec.decorators import async_validate as validate

from .data_classes.params import ArticleCreatedDatePP, CreateArticleDCRB
from .data_classes.results import ArticleDC
from .decorators import only_validate
from .storages import Storage


@only_validate("row", "return")
async def create_article(
    row: CreateArticleDCRB, storage: Storage
) -> ArticleDC:
    """ Создает в хранилище новую запись о статье.
        Возвращает созданную запись.
    """
    row["created"] = datetime.date.today()

    return await storage.create(table_name="articles", row=row)


@only_validate("return")
@validate("created")
async def read_articles(
    storage: Storage, created: Optional[ArticleCreatedDatePP] = None
) -> List[ArticleDC]:
    """ Читает из хранилища статьи и возвращает их.
    """
    filters = None if created is None else {"created": [created]}

    return await storage.read(table_name="articles", filters=filters)
