""" Модуль для обработчиков CRUD.
"""
from .data_classes.params import CreateArticleParamsDC
from .data_classes.results import ArticleResultsDC
from .storages import Storage


async def create_article(
    row: CreateArticleParamsDC, storage: Storage
) -> ArticleResultsDC:
    """ Создает в хранилище новую запись о статье.
        Возвращает созданную запись.
    """
    return await storage.create(table_name="articles", row=row)
