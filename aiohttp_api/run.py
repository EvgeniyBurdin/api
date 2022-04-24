""" Модуль для запуска сервиса.
"""
from aiohttp import web
from core.data_classes.base import BaseDCA
from core.storages import Storage

from aiohttp_api.app import get_app
from aiohttp_api.settings import APP_PORT
from aiohttp_api.swagger import add_swagger_to_app

app = get_app(storage=Storage(), url_query_data_class=BaseDCA)

add_swagger_to_app(app)

web.run_app(app=app, port=APP_PORT)
