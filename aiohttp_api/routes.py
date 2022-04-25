""" Связи путей urls и их обработчиков.
"""
from aiohttp import web
from core.handlers import create_article, read_articles, upload_article_file

from .settings import ROOT_URL

json_api_routes = [
    # Адреса для обработчиков JSON API

    web.post(
        ROOT_URL+"/create_article", create_article,
        name="create_article", swagger_handler_tags=["Статьи"],
    ),
    web.get(
        ROOT_URL+"/read_articles/{created}", read_articles,
        name="read_articles", allow_head=False,
        swagger_path_parameters={
            "created": {
                "description": "Дата создания", "example": "2022-04-26",
            }
        },
        swagger_handler_tags=["Статьи"],
    ),
]

multipart_api_routes = [
    web.post(
        ROOT_URL+"/upload_article_file", upload_article_file,
        name="upload_article_file", swagger_handler_tags=["Статьи", "Файлы"],
    ),
]

http_routes = []

json_api_routes = json_api_routes + multipart_api_routes

routes = json_api_routes + http_routes
