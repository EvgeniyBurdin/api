""" Модуль для базовых классов данных.
"""
from typing import Any, Dict, Type

from pydantic import BaseModel, Extra, StrictStr


class BaseDC(BaseModel):
    """ Базовый класс данных.
    """
    class Config:

        # Следует ли игнорировать (ignore), разрешать (allow) или
        # запрещать (forbid) дополнительные атрибуты во время инициализации
        # модели, подробнее:
        # https://pydantic-docs.helpmanual.io/usage/model_config/
        extra = Extra.forbid

        @staticmethod
        def schema_extra(
            schema: Dict[str, Any], model: Type['BaseDC']
        ) -> None:
            """ Убирает у полей из схемы атрибут 'title'.
            """
            for prop in schema.get('properties', {}).values():
                prop.pop('title', None)


class BaseDCA(BaseDC):
    """ Базовый класс данных, которые имеют аннотацию одним из
        классов-наследников (для точной идентификации аргумента функции).
    """


class BaseFileDC(BaseDC):
    """ Базовый класс для загрузки файла.
    """
    file_name: StrictStr
    file_data: Any


class BaseMultipartDC(BaseDC):
    """ Базовый класс для данных "multipart".
    """
    pass
