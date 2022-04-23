""" Модуль для классов данных на параметров (аргументов).
"""
from pydantic import Field, StrictStr

from .base import BaseDCRB, BaseDCUQ


class NewArticleDCRB(BaseDCRB):
    """ Данные для создания новой статьи.
    """
    header: StrictStr = Field(description="Заголовок")
    content: StrictStr = Field(description="Содержание")


class ReadArticlesDCUQ(BaseDCUQ):
    """ Данные для чтения статей.
    """
    header_prefix: StrictStr = Field(
        description="Прификс заголовка для фильтрации статей"
    )
