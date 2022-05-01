""" Модуль для настроек приложения.
"""
from os import getenv


APP_NAME = getenv("APP_NAME", "api_examle")
APP_PORT = getenv("APP_PORT", "5000")

ROOT_URL = getenv("ROOT_URL", "")

HEALTH_CHECK_URL = getenv("HEALTH_CHECK_URL", "/health_check")
API_DOC_URL = getenv("API_DOC_URL", "/api_doc")

IS_DEBUG = getenv("IS_DEBUG", "false").lower() in ('true', '1')
IS_AUTH = getenv("IS_AUTH", "true").lower() in ('true', '1')

# Имя аргумента у обработчика, в который будет передаваться тело запроса
# уже декодированное из json
REQUEST_BODY_ARG_NAME = "body"
