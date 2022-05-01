""" Модуль для подключения swagger к приложению.
"""
from copy import deepcopy
from typing import List, Type

import yaml
from aiohttp import web
from aiohttp_swagger3 import (RapiDocUiSettings, ReDocUiSettings, SwaggerDocs,
                              SwaggerInfo, SwaggerUiSettings)
from aiohttp_swagger3.routes import _SWAGGER_SPECIFICATION

from ..settings import API_DOC_URL, APP_NAME, REQUEST_BODY_ARG_NAME
from .maker import swagger_preparation


def add_routes_and_doc_to_app(
    app: web.Application,
    routes: List[web.RouteDef],
    multipart_data_class: Type,
    url_query_data_class: Type,
    error_data_class: Type,
    is_debug: bool = True
):

    definitions = swagger_preparation(
        routes=routes,
        # Имя аргумента в обработчиках по аннотации к которому будет
        # создаваться документация для входящих данных
        request_body_arg_name=REQUEST_BODY_ARG_NAME,
        multipart_data_class=multipart_data_class,
        url_query_data_class=url_query_data_class,
        error_data_class=error_data_class,
    )

    swagger = SwaggerDocs(
        app,
        swagger_ui_settings=SwaggerUiSettings(path=f"{API_DOC_URL}/"),
        redoc_ui_settings=ReDocUiSettings(path=f"{API_DOC_URL}_re/"),
        rapidoc_ui_settings=RapiDocUiSettings(path=f"{API_DOC_URL}_ra/"),
        info=SwaggerInfo(title=APP_NAME, version="1.0.0"),
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

    # Удалим ключи, который aiohttp_swagger3 "не хочет" принимать
    # (схему для сваггера мы уже сделали, и они уже и не нужны)
    for route in routes:
        route.kwargs.pop("swagger_path_parameters", None)
        route.kwargs.pop("swagger_handler_tags", None)

    # (это "странность" библиотеки aiohttp_swagger3, скорее всего они применили
    # такой подход для реализации возможности валидации запросов в доке)
    # Роуты для всех методов добавляем так:
    swagger.add_routes(routes)

    data = deepcopy(swagger.spec)
    components = data.pop("components", None)
    add_data = {"components": components}

    with open('shema.yml', 'w') as outfile:
        yaml.dump(data, outfile, allow_unicode=True)
        yaml.dump(add_data, outfile, allow_unicode=True)
