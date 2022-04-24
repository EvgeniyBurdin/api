""" Модуль для менеджера аргументов обработчиков.
"""
from dataclasses import dataclass
from typing import Any, Callable, Dict, Type

from aiohttp import web

from .query import InputData


@dataclass
class RawDataForArgument:

    request: web.Request
    input_data: InputData
    arg_name: Any = None


class ArgumentsManager:
    """ Менеджер для аргументов обработчика.

        Связывает имя аргумента с действием, которое надо совершить для
        получения значения аргумента.
    """

    def __init__(self, request_class: Type, query_class: Type) -> None:

        # Класс для идентификации аргумента для экземпляра web.Request
        self.request_class = request_class

        # Класс для идентификации аргумента для экземпляра класса_данных
        # с данными запроса из урла
        self.query_class = query_class

        self.getters: Dict[str, Callable] = {}

    def make_arg_value(
        self, raw_data: RawDataForArgument, arg_name: str, annotation
    ) -> Any:

        if annotation is self.request_class:
            return raw_data.request

        if issubclass(annotation, self.query_class):
            return raw_data.input_data.url_query

        if arg_name in raw_data.input_data.url_parts:
            return raw_data.input_data.url_parts[arg_name]

        getter = self.getters[arg_name]
        raw_data.arg_name = arg_name

        return getter(raw_data)

    # Тело json запроса ------------------------------------------------------

    def reg_request_body(self, arg_name) -> None:
        """ Регистрация имени аргумента для json-тела запроса.
        """
        self.getters[arg_name] = self.get_request_body

    def get_request_body(self, raw_data: RawDataForArgument):
        return raw_data.input_data.request_body

    # Ключи в request --------------------------------------------------------

    def reg_request_key(self, arg_name) -> None:
        """ Регистрация имени аргумента который хранится в request.
        """
        self.getters[arg_name] = self.get_request_key

    def get_request_key(self, raw_data: RawDataForArgument):
        return raw_data.request[raw_data.arg_name]

    # Ключи в request.app ----------------------------------------------------

    def reg_app_key(self, arg_name) -> None:
        """ Регистрация имени аргумента который хранится в app.
        """
        self.getters[arg_name] = self.get_app_key

    def get_app_key(self, raw_data: RawDataForArgument):
        return raw_data.request.app[raw_data.arg_name]

    # Параметры запроса ------------------------------------------------------

    def reg_match_info_key(self, arg_name) -> None:
        """ Регистрация имени аргумента который приходит в параметрах запроса.
        """
        self.getters[arg_name] = self.get_match_info_key

    def get_match_info_key(self, raw_data: RawDataForArgument):
        return raw_data.request.match_info[raw_data.arg_name]

    # Можно добавить и другие регистраторы...
