""" Модуль для классов данных результатов.
"""
from uuid import UUID

from pydantic import Field, StrictStr

from .base import BaseDC


class ArticleResultsDC(BaseDC):
    """ Данные о статье.
    """
    id: UUID = Field(description="Идентификатор")
    header: StrictStr = Field(description="Заголовок")
    content: StrictStr = Field(description="Содержание")
