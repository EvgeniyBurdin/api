""" Модуль для классов данных результатов у обработчиков.
"""
import datetime
import uuid

from pydantic import Field, StrictStr

from .base import BaseDC


class ErrorResultDC(BaseDC):
    """ Ошибка.
    """
    error_type: StrictStr = Field(description="Тип ошибки.")
    error_message: StrictStr = Field(description="Сообщение об ошибке.")


class ArticleDC(BaseDC):
    """ Данные о статье.
    """
    id: uuid.UUID = Field(description="Идентификатор")
    created: datetime.date = Field(description="Дата создания")
    header: StrictStr = Field(description="Заголовок")
    content: StrictStr = Field(description="Содержание")
