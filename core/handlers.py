""" Модуль для обработчиков CRUD.
"""
import datetime

from .data_classes.params import CreateArticleDCRB
from .data_classes.results import ArticleResultsDC
from .decorators import only_validate
from .storages import Storage


@only_validate("row", "return")
async def create_article(
    row: CreateArticleDCRB, storage: Storage
) -> ArticleResultsDC:
    """ Создает в хранилище новую запись о статье.
        Возвращает созданную запись.
    """
    row["created"] = datetime.date.today()

    return await storage.create(table_name="articles", row=row)
