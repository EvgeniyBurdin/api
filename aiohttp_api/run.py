""" Модуль для запуска сервиса.
"""
from aiohttp import web
from core.data_classes.base import BaseDCA
from core.storages import Storage

from aiohttp_api.app import get_app
from aiohttp_api.settings import APP_PORT

app = get_app(storage=Storage(), uro_query_data_class=BaseDCA)

web.run_app(app=app, port=APP_PORT)
