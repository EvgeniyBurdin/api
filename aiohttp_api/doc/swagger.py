""" Модуль для подключения swagger к приложению.
"""
from copy import deepcopy
from typing import List, Type

import yaml
from aiohttp import web
from aiohttp_swagger3 import (RapiDocUiSettings, ReDocUiSettings, SwaggerDocs,
                              SwaggerInfo, SwaggerUiSettings)
from aiohttp_swagger3.routes import _SWAGGER_SPECIFICATION
from pydantic import BaseModel

from .maker import swagger_preparation


def add_routes_and_doc_to_app(
    app: web.Application,
    routes: List[web.RouteDef],
    json_api_routes: List[web.RouteDef],
    multipart_data_class: Type[BaseModel],
    base_file_data_class: Type[BaseModel],
    url_query_data_class: Type[BaseModel],
    error_data_class: Type[BaseModel],
    request_body_arg_name: str,
    api_doc_url: str,
    app_name: str,
    is_auth: bool = False,
):
    """ Добавляет routes в app и формирует сваггер-доку для app.

    :app:             Экземпляр приложения.
    :routes:          Все routes приложения. Добавляются в app.
    :json_api_routes: routes апи-методов. Используются для формирования
                      описания данных.
    :multipart_data_class: Класс данных для идентификации multipart
                           (используется для загрузки файлов).
    :url_query_data_class: Класс данных для идентификации данных, которые
                           приходят в запросе в урле (после вопр.знака)
    :error_data_class:     Класс данных для описания ответа с ошибкой.
    :api_doc_url: Урл, по которому будет доступна документация.
    :app_name:    Имя приложения, которое будет отображено в документации.
    :is_auth:     Включена или нет авторизация.
    """

    definitions = swagger_preparation(
        routes=json_api_routes,
        request_body_arg_name=request_body_arg_name,
        multipart_data_class=multipart_data_class,
        base_file_data_class=base_file_data_class,
        url_query_data_class=url_query_data_class,
        error_data_class=error_data_class,
    )

    swagger = SwaggerDocs(
        app,
        swagger_ui_settings=SwaggerUiSettings(path=f"{api_doc_url}/"),
        redoc_ui_settings=ReDocUiSettings(path=f"{api_doc_url}_re/"),
        rapidoc_ui_settings=RapiDocUiSettings(path=f"{api_doc_url}_ra/"),
        info=SwaggerInfo(title=app_name, version="1.0.0"),
        validate=False,  # Нам не нужна валидация запросов в доке
    )

    if is_auth:
        swagger.spec["components"] = {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                },
            },
        }
        swagger.spec["security"] = [{"bearerAuth": []}]

    # Немного "грязновато", но иначе не подсунуть json-схемы классов данных
    # (при создании swagger они читаются из файла, но создавать из-за этого
    # файл - ещё хуже... ведь схемы у нас уже есть в словаре definitions)
    swagger.spec["components"].update({"schemas": definitions})
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
