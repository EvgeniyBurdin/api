""" Модуль для классов данных на параметров (аргументов).
"""
import datetime

from pydantic import Field, StrictStr

from .base import BaseDCRB, BasePP


class NewArticleDCRB(BaseDCRB):
    """ Данные для создания новой статьи.
    """
    header: StrictStr = Field(description="Заголовок")
    content: StrictStr = Field(description="Содержание")


class ArticleCreatedPP(datetime.date, BasePP):
    """ Дата создания статьи."""
