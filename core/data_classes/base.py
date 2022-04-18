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
    """ Базовый класс данных, которые могут приходить в теле запроса в json
    (в терминалогии swagger эти данные в ключе requestBody, чтобы это
    подчеркнуть, имя класса имеет окончание "RB").
    """


class BaseDCPQ(BaseDC):
    """ Базовый класс данных, которые могут приходить в полях указанных за
    путем к ресурсу (в терминалогии swagger это поле в ключе parameters c
    ключем in=query, чтобы это подчеркнуть, имя класса имеет окончание "PQ").
    """


class BasePP:
    """ Базовый класс данных, которые могут приходить в пути к ресурсу
    (в терминалогии swagger это поле в ключе parameters c ключем in=path,
    чтобы это подчеркнуть, имя класса имеет окончание "PP").
    """
