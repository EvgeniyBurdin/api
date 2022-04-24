""" Модуль для классов данных на параметров (аргументов).
"""
from typing import Optional

from pydantic import Field, StrictStr

from .base import BaseDC, BaseDCA


class NewArticleDC(BaseDC):
    """ Данные для создания новой статьи.
    """
    header: StrictStr = Field(description="Заголовок")
    content: StrictStr = Field(description="Содержание")


class ReadArticlesDCA(BaseDCA):
    """ Данные для чтения статей.
    """
    header_prefix: Optional[StrictStr] = Field(
        description="Прификс заголовка для фильтрации статей"
    )
