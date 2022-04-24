""" Модуль для сборки приложения.
"""
from aiohttp import web

from .args_manager import ArgumentsManager
from .middlewares import KwargsHandler
from .routes import json_api_routes


def get_app(storage, url_query_data_class) -> web.Application:

    app = web.Application()

    # Для обработчиков JSON API
    arguments_manager = ArgumentsManager(
        request_class=web.Request, url_query_data_class=url_query_data_class
    )

    app["storage"] = storage
    # Регистрация имени аргумента обработчика JSON API, в котором
    # будет хранилище
    arguments_manager.reg_app_key("storage")

    # Регистрация имени аргумента обработчика JSON API, в который будут
    # передаваться данные полученные из json-тела запроса
    arguments_manager.reg_request_body("body")

    # Создадим и подключим мидлевару для JSON API методов
    kwargs_handler = KwargsHandler(
        arguments_manager=arguments_manager,
        json_api_routes=json_api_routes,
    )
    app.middlewares.append(kwargs_handler.middleware)

    app.add_routes(json_api_routes)

    return app
