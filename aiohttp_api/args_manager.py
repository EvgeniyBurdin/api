""" Различные классы и функции.
"""
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from aiohttp import web


@dataclass
class RawDataForArgument:

    request: web.Request
    request_body: Any
    arg_name: Optional[str] = None


class ArgumentsManager:
    """ Менеджер для аргументов обработчика.

        Связывает имя аргумента с действием, которое надо совершить для
        получения значения аргумента.
    """

    def __init__(self) -> None:

        self.getters: Dict[str, Callable] = {}

    # Тело json запроса ------------------------------------------------------

    def reg_request_body(self, arg_name) -> None:
        """ Регистрация имени аргумента для тела запроса.
        """
        self.getters[arg_name] = self.get_request_body

    def get_request_body(self, raw_data: RawDataForArgument):
        return raw_data.request_body

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
