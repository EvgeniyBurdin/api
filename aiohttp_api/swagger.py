from aiohttp import web
from aiohttp_swagger3 import (RapiDocUiSettings, ReDocUiSettings, SwaggerDocs,
                              SwaggerUiSettings)
from aiohttp_swagger3.routes import _SWAGGER_SPECIFICATION
from core.data_classes.results import ErrorResultDC

from .doc_makers import swagger_preparation
from .routes import json_api_routes
from .settings import API_DOC_URL, APP_NAME, REQUEST_BODY_ARG_NAME


def add_swagger_to_app(app: web.Application, is_debug: bool = True):

    definitions = swagger_preparation(
        handlers=[route.handler for route in json_api_routes],
        # Имя аргумента в обработчиках по аннотации к которому будет
        # создаваться документация для входящих данных
        arg_name=REQUEST_BODY_ARG_NAME,
        # Классы оболочек запроса к серверу и его ответа
        # request_wrap=ServerWrap(ServerRequest, "params"),
        # response_wrap=ServerWrap(ServerResponse, "result"),
        # Покажем и ошибки
        error_class=ErrorResultDC
    )

    swagger = SwaggerDocs(
        app,
        swagger_ui_settings=SwaggerUiSettings(path=f"{API_DOC_URL}/"),
        redoc_ui_settings=ReDocUiSettings(path=f"{API_DOC_URL}_re/"),
        rapidoc_ui_settings=RapiDocUiSettings(path=f"{API_DOC_URL}_ra/"),
        title=APP_NAME,
        version="1.0.0",
        validate=False,  # Нам не нужна валидация запросов в доке
    )
    # Немного "грязновато", но иначе не подсунуть json-схемы классов данных
    # (при создании swagger они читаются из файла, но создавать из-за этого
    # файл - ещё хуже... ведь схемы у нас уже есть в словаре definitions)
    swagger.spec["components"] = {"schemas": definitions}
    if not is_debug:
        swagger.spec["components"]["securitySchemes"] = {
            "basicAuth": {"type": "http", "scheme": "basic"},
        }
        swagger.spec["security"] = [{"basicAuth": []}]
    swagger._app[_SWAGGER_SPECIFICATION] = swagger.spec
    # Роуты для всех JSON API методов добавляются так:
    swagger.add_routes(json_api_routes)
    # (это "странность" библиотеки aiohttp_swagger3, скорее всего они применили
    # такой подход для реализации возможности валидации запросов в доке)
