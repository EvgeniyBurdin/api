""" Модуль для оболочек запросов.
"""
from copy import copy
from dataclasses import asdict
from typing import Any, Callable, List, Optional, Tuple

from aiohttp import web
from valdec.errors import ValidationArgumentsError

from .args_manager import ArgumentsManager, RawDataForArgument
from .json_utils import json_dumps
from .query_data import InputData, extract_input_data


class MiddlewaresError(Exception):
    pass


class InvalidHandlerArgument(MiddlewaresError):
    pass


class InputDataValidationError(MiddlewaresError):
    pass


class KwargsHandler:
    """ Класс для middleware которая работает с обработчиками json-api методов.
        Методы могут иметь произвольное количество аргументов.

        Каждый аргумент обработчика должен иметь аннотацию.

        Маппинг значений, полученных из запроса, в аргументы обработчика
        производит arguments_manager.

        Все обработчики должны возвращать объекты питон, которые потом
        кодируются в json функцией json_dumps.
    """
    def __init__(
        self,
        arguments_manager: ArgumentsManager,
        json_api_routes: List[web.RouteDef],
        multipart_api_routes: Optional[List[web.RouteDef]] = None,
    ) -> None:

        self.arguments_manager = arguments_manager

        self.json_api_handlers = set([
            route.handler for route in json_api_routes
        ])

        if multipart_api_routes is None:
            multipart_api_routes = []
        self.multipart_api_handlers = set([
            route.handler for route in multipart_api_routes
        ])

    def build_error_message_for_invalid_handler_argument(
        self, handler: Callable, arg_name: str, annotation: Any
    ) -> str:
        """ Создает и возвращает строку с сообщением об ошибке для исключения
            InvalidHandlerArgument.
        """
        message = f"KeyError, invalid handler '{handler}' argument: "
        message += f"'{arg_name}': {annotation}'"

        return message

    def make_handler_kwargs(
        self, request: web.Request, handler: Callable, input_data: InputData
    ) -> dict:
        """ Собирает и возвращает словарь kwargs для последующего его
            использования при вызове обработчика.

            Внимание! Все аргументы у обработчиков должны иметь аннотации.
        """
        kwargs = {}

        annotations = copy(handler.__annotations__)
        annotations.pop("return", None)

        raw_data = RawDataForArgument(request=request, input_data=input_data)

        for arg_name, annotation in annotations.items():
            try:
                kwargs[arg_name] = self.arguments_manager.extract_arg_value(
                    raw_data=raw_data,
                    arg_name=arg_name,
                    annotation=annotation,
                )
            except KeyError:
                msg = self.build_error_message_for_invalid_handler_argument(
                    handler, arg_name, annotation
                )
                raise InvalidHandlerArgument(msg)

        return kwargs

    def get_error_body(self, error: Exception) -> dict:
        """ Отдает словарь с телом ответа с ошибкой.
        """
        error_type = str(type(error))[8:-2]

        return {"error_type": error_type, "error_message": f"{error}"}

    def is_json_api_handler(self, handler: Callable) -> bool:
        """ Проверяет, является ли handler обработчиком json-api сервиса.
        """
        return handler in self.json_api_handlers

    async def run_handler(
        self, request: web.Request, handler: Callable, input_data: InputData
    ) -> Any:
        """ Запуск реального обработчика.
            Возвращает результат его работы.
        """
        kwargs = self.make_handler_kwargs(request, handler, input_data)

        return await handler(**kwargs)

    async def get_response_body_and_status(
        self, request: web.Request, handler: Callable, input_data: InputData
    ) -> Tuple[Any, int]:
        """ Вызывает метод запуска обработчика и обрабатывает возможные
            ошибки.
            Возвращает объект с телом для ответа и код статуса ответа.
        """
        try:
            response_body = await self.run_handler(
                request, handler, input_data
            )
            status = 200

        except ValidationArgumentsError as error:
            input_validation_error = InputDataValidationError(str(error))
            response_body = self.get_error_body(input_validation_error)
            status = 400

        except Exception as error:
            response_body = self.get_error_body(error)
            status = 500

        return response_body, status

    async def get_response_text_and_status(
        self, response_body: Any, status: int
    ) -> Tuple[str, int]:
        """ Возвращает json-строку для ответа и код статуса ответа.
        """
        try:
            text = json_dumps(response_body)

        except Exception as error:
            error_body = self.get_error_body(error)
            text = json_dumps(error_body)
            status = 500

        return text, status

    @web.middleware
    async def middleware(
        self, request: web.Request, handler: Callable
    ) -> web.Response:
        """ middleware для json api.
        """
        if not self.is_json_api_handler(handler):
            return await handler(request)

        is_multiparts = handler in self.multipart_api_handlers

        try:
            input_data = await extract_input_data(request, is_multiparts)

        except Exception as error:
            response_body = self.get_error_body(error)
            status = 400
            input_data = InputData(None, {}, {})

        else:
            # Запуск обработчика
            response_body, status = await self.get_response_body_and_status(
                request, handler, input_data
            )

        finally:
            # Самостоятельно делаем дамп объекта python (который находится в
            # response_body) в строку json.
            text, status = await self.get_response_text_and_status(
                response_body, status
            )
            if status != 200:  # Логгируем только ошибку
                message = f"API: handler={handler.__name__}, "
                message += f"url={request.rel_url}, "
                message += f"error={text}, status={status}, "
                message += f"input_data={asdict(input_data)}"

        return web.Response(
            text=text, status=status, content_type="application/json",
        )
