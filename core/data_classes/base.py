""" Модуль для базового класса данных."""
from typing import Any, Dict, Type

from pydantic import BaseModel, Extra


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
            schema: Dict[str, Any], model: Type['BaseDCRB']
        ) -> None:
            """ Убирает у полей из схемы атрибут 'title'.
            """
            for prop in schema.get('properties', {}).values():
                prop.pop('title', None)


class BaseDCRB(BaseDC):
    """ Базовый класс данных, которые могут приходить в теле HTTP запроса.
    (в терминалогии swagger эти данные в ключе requestBody)
    """


class BasePP:
    """ Базовый класс данных, которые могут приходить в пути HTTP запроса.
    (в терминалогии swagger это поле в ключе parameters c ключем in=path)
    """
