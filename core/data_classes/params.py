""" Модуль для классов данных на параметров (аргументов).
"""
from pydantic import StrictStr, Field

from .base import BaseDC


class CreateArticleParamsDC(BaseDC):
    """ Данные для создания новой статьи.
    """
    header: StrictStr = Field(description="Заголовок")
    content: StrictStr = Field(description="Содержание")
