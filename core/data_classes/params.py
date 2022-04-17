""" Модуль для классов данных на параметров (аргументов).
"""
import datetime

from pydantic import Field, StrictStr

from .base import BaseDCRB, BasePP


class CreateArticleDCRB(BaseDCRB):
    """ Данные для создания новой статьи.
    """
    header: StrictStr = Field(description="Заголовок")
    content: StrictStr = Field(description="Содержание")


class ArticleCreatedDatePP(datetime.date, BasePP):
    """ Дата создания статьи."""
