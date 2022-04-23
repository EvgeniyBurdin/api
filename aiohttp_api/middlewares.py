from copy import copy
from typing import Any, Callable, List, Optional, Tuple

from aiohttp import web
from valdec.errors import ValidationArgumentsError

from .args_manager import ArgumentsManager, RawDataForArgument, json_dumps


class MiddlewaresError(Exception):
    pass


class InvalidHandlerArgument(MiddlewaresError):
    pass


class InputDataValidationError(MiddlewaresError):
    pass


class KwargsHandler:
    """ Класс для middleware которая работает с обработчиками json-api методов,
        которые могут иметь произвольное количество аргументов.

        Для этого, каждый аргумент обработчика должен иметь аннотацию, и имя
        агрумента должно быть предварительно зарегистрировано при создании
        экземпляра web.Application().

        Все аргументы в обработчик передаются именованными, поэтому не важен
        порядок их определения в сигнатуре обработчика.

        Аргумент, который должен принять в обработчик оригинальный request,
        не требует регистрации. Он может иметь в сигнатуре обработчика любое
        имя, но обязательно должен быть аннотирован типом: web.Request

        Все обработчики должны возвращать объекты питон, которые потом
        кодируются в json функцией utils.json_dumps.
    """
    def __init__(
        self,
        arguments_manager: ArgumentsManager,
        json_api_routes: List[web.RouteDef],
        multipart_api_routes: Optional[List[web.RouteDef]] = None,
        file_name_key_name: str = "file_name",
        file_data_key_name: str = "file_data",
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

        self.file_name_key_name = file_name_key_name
        self.file_data_key_name = file_data_key_name

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
        self, request: web.Request, handler: Callable, request_body: Any
    ) -> dict:
        """ Собирает и возвращает kwargs для последующего его использования
            при вызове обработчика.

            Внимание! Все аргументы у обработчиков должны иметь аннотации.
        """
        kwargs = {}

        annotations = copy(handler.__annotations__)
        annotations.pop("return", None)

        raw_data = RawDataForArgument(request, request_body)

        for arg_name, annotation in annotations.items():

            # Если обработчик имеет аргумент с аннотацией aiohttp.web.Request,
            # то передадим в него экземпляр оригинального request
            if annotation is web.Request:
                kwargs[arg_name] = request
                continue

            raw_data.arg_name = arg_name

            try:
                # функция которая затем вернет нам значение для
                # аргумента с arg_name
                get_arg_value = self.arguments_manager.getters[arg_name]

            except KeyError:
                msg = self.build_error_message_for_invalid_handler_argument(
                    handler, arg_name, annotation
                )
                raise InvalidHandlerArgument(msg)

            kwargs[arg_name] = get_arg_value(raw_data)

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
        self, request: web.Request, handler: Callable, request_body: Any
    ) -> Any:
        """ Запуск реального обработчика.
            Возвращает результат его работы.
        """
        kwargs = self.make_handler_kwargs(request, handler, request_body)

        return await handler(**kwargs)

    async def get_response_body_and_status(
        self, request: web.Request, handler: Callable, request_body: Any
    ) -> Tuple[Any, int]:
        """ Вызывает метод запуска обработчика и обрабатывает возможные
            ошибки.
            Возвращает объект с телом для ответа и код статуса ответа.
        """
        try:
            response_body = await self.run_handler(
                request, handler, request_body
            )
            status = 200

        except ValidationArgumentsError as error:
            _error = InputDataValidationError(str(error))
            response_body = self.get_error_body(_error)
            status = 400

        except Exception as error:
            response_body = self.get_error_body(error)
            status = 500

        return response_body, status

    async def get_json_dumps(self, response_body: Any) -> str:
        """ Возвращает json-строку с дампом response_body.
        """
        return json_dumps(response_body)

    async def get_response_text_and_status(
        self, response_body: Any, status: int
    ) -> Tuple[str, int]:
        """ Возвращает json-строку для ответа и код статуса ответа.
        """
        try:
            text = await self.get_json_dumps(response_body)

        except Exception as error:
            error_body = self.get_error_body(error)
            text = await self.get_json_dumps(error_body)
            status = 500

        return text, status

    async def read_multipart_request_body(self, request: web.Request) -> dict:
        """ Читает данные из multipart.

            Внимание!
            Части могут быть только с content_type="application/json" или
            content_type="application/octet-stream".
        """
        request_body = {}

        mp = await request.multipart()

        while True:

            part = await mp.next()
            if part is None:
                break

            if part.filename is None:
                # Получили content_type="application/json"
                data = await part.json()
                request_body[part.name] = data
            else:
                # Получили content_type="application/octet-stream"
                data = await part.read(decode=False)
                request_body[part.name] = {
                    self.file_name_key_name: part.filename,
                    self.file_data_key_name: data,
                }

        return request_body

    async def get_request_body(
        self, request: web.Request, handler: Callable
    ) -> Any:
        """ Вытаскивает из запроса json или multipart, декодирует его в объект
            python, и возвращает его.
        """
        request_body = {}

        if handler in self.multipart_api_handlers:
            request_body = await self.read_multipart_request_body(request)
        elif request.body_exists:
            request_body = await request.json()

        return request_body

    @web.middleware
    async def middleware(
        self, request: web.Request, handler: Callable
    ) -> web.Response:
        """ middleware для json api.
        """
        if not self.is_json_api_handler(handler):
            return await handler(request)

        request_body = None

        try:
            request_body = await self.get_request_body(request, handler)

        except Exception as error:
            response_body = self.get_error_body(error)
            status = 400

        else:
            # Запуск обработчика
            response_body, status = await self.get_response_body_and_status(
                request, handler, request_body
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
                message += f"request_body={request_body}"

        return web.Response(
            text=text, status=status, content_type="application/json",
        )
