""" Модуль для запуска сервиса.
"""
from aiohttp import web
from core.data_classes.base import BaseDCA, BaseMultipartDC
from core.data_classes.results import ErrorResultDC
from core.storages import Storage

from aiohttp_api.app import get_app
from aiohttp_api.doc.swagger import add_routes_and_doc_to_app
from aiohttp_api.routes import json_api_routes, routes
from aiohttp_api.settings import (API_DOC_URL, APP_NAME, APP_PORT, IS_AUTH,
                                  ROOT_URL)

REQUEST_BODY_ARG_NAME = "body"


app = get_app(
    storage=Storage(),
    url_query_data_class=BaseDCA,
    request_body_arg_name=REQUEST_BODY_ARG_NAME,
)


add_routes_and_doc_to_app(
    app=app,
    routes=routes,
    json_api_routes=json_api_routes,
    multipart_data_class=BaseMultipartDC,
    url_query_data_class=BaseDCA,
    error_data_class=ErrorResultDC,
    request_body_arg_name=REQUEST_BODY_ARG_NAME,
    api_doc_url=ROOT_URL+API_DOC_URL,
    app_name=APP_NAME,
    is_auth=IS_AUTH,
)

web.run_app(app=app, port=APP_PORT)
