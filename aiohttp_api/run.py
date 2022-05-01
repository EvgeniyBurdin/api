""" Модуль для запуска сервиса.
"""
from aiohttp import web
from core.data_classes.base import BaseDCA, BaseMultipartDC
from core.data_classes.results import ErrorResultDC
from core.storages import Storage
from aiohttp_api.routes import routes

from aiohttp_api.app import get_app
from aiohttp_api.settings import APP_PORT
from aiohttp_api.doc.swagger import add_routes_and_doc_to_app

app = get_app(storage=Storage(), url_query_data_class=BaseDCA)

add_routes_and_doc_to_app(
    app=app,
    routes=routes,
    multipart_data_class=BaseMultipartDC,
    url_query_data_class=BaseDCA,
    error_data_class=ErrorResultDC,
)

web.run_app(app=app, port=APP_PORT)
