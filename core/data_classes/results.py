""" Модуль для классов данных результатов.
"""
import datetime
import uuid

from pydantic import Field, StrictStr

from .base import BaseDC


class ArticleResultsDC(BaseDC):
    """ Данные о статье.
    """
    id: uuid.UUID = Field(description="Идентификатор")
    created: datetime.date = Field(description="Дата создания")
    header: StrictStr = Field(description="Заголовок")
    content: StrictStr = Field(description="Содержание")
