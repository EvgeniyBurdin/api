""" Модуль для классов данных аргументов у обработчиков.
"""
import datetime
from typing import Optional

from pydantic import Field, StrictStr

from .base import BaseDC, BaseDCA


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
        description="Префикс заголовка для фильтрации статей"
    )
