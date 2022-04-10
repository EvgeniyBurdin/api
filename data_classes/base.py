""" Базовый класс данных.

    Должен обязательно иметь метод dict(), который возвращает экземпляр в
    виде словаря.

    Пример получения словаря data из экземпляра:
        data = instance.dict()
"""
from pydantic import BaseModel, Extra


class Base(BaseModel):
    """ Базовый класс данных
    """
    class Config:

        # Следует ли игнорировать (ignore), разрешать (allow) или
        # запрещать (forbid) дополнительные атрибуты во время инициализации
        # модели, подробнее:
        # https://pydantic-docs.helpmanual.io/usage/model_config/
        extra = Extra.forbid
