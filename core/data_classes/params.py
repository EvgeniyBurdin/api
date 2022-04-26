""" Модуль для классов данных аргументов у обработчиков.
"""
import datetime
import uuid
from typing import Optional

from pydantic import Field, StrictStr

from .base import BaseDC, BaseDCA, BaseFileDC, BaseMultipartDC


class NewArticleDC(BaseDC):
    """ Данные для создания новой статьи.
    """
    header: StrictStr = Field(description="Заголовок")
    content: StrictStr = Field(description="Содержание")
    created: Optional[datetime.date] = Field(description="Дата создания")


class ReadArticlesDCA(BaseDCA):
    """ Данные для чтения статей.
    """
    header_prefix: Optional[StrictStr] = Field(
        description="Префикс заголовка для фильтрации статей",
        example="Статья о нов"
    )


class UploadArticleFileMultipartDC(BaseMultipartDC):
    """ "Мультиформа" запроса для загрузки файла к статье.
    """
    article_id: uuid.UUID = Field(
        description="Форма для идентификатора cтатьи "
                    "`content_type='application/json'`"
    )
    file: BaseFileDC = Field(
        description="Форма для файла "
                    "`content_type='application/octet-stream'`"
    )
