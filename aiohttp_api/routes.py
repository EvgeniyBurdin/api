""" Связи путей urls и их обработчиков.
"""
from aiohttp import web
from core.handlers import create_article, read_articles

from .settings import ROOT_URL

json_api_routes = [
    # Адреса для обработчиков JSON API

    web.post(
        ROOT_URL+"/create_article", create_article,
        name="create_article"
    ),
    web.get(
        ROOT_URL+"/read_articles/{created}", read_articles,
        name="read_articles"
    ),
]

multipart_api_routes = []

http_routes = []

json_api_routes = json_api_routes + multipart_api_routes

routes = json_api_routes + http_routes
