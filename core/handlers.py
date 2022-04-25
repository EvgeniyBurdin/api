""" Модуль для обработчиков.
"""
import datetime
from typing import List

from .data_classes.params import (NewArticleDC, ReadArticlesDCA,
                                  UploadArticleFileMultipartDC)
from .data_classes.results import ArticleDC
from .decorators import validate, validate_raw
from .storages import Storage


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

        Фильтрует статьи по дате создания. Опционально можно отфильтровать по
        префиксу заголовка.
    """
    filters = {"created": [created]}
    print(query.header_prefix)

    return await storage.read(table_name="articles", filters=filters)


@validate_raw("return")
@validate("body")
async def upload_article_file(body: UploadArticleFileMultipartDC) -> str:
    """ Загрузка файла к статье.
    """
    print(body.article_id)
    print(body.file.file_name)
    print(body.file.file_data)

    return "OK"
