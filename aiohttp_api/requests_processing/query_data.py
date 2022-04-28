""" Модуль для работы с данными запроса.
"""
from dataclasses import dataclass
from typing import Any

from aiohttp.web import Request


@dataclass
class InputData:
    """ Класс данных, которые могут быть переданы в запросе.
    """
    request_body: Any  # json-тело запроса
    url_parts: dict    # данные в частях урла
    url_query: dict    # данные из запроса в урле (в конце, через знак вопроса)


async def extract_multipart_request_body(request: Request) -> dict:
    """ Читает данные из multipart.

        Внимание!
        Части могут быть только с content_type="application/json" или
        content_type="application/octet-stream".
    """
    request_body = {}

    multipart_reader = await request.multipart()

    while True:

        part = await multipart_reader.next()
        if part is None:
            break

        if part.filename is None:
            # Получили content_type="application/json"
            data = await part.json()
            request_body[part.name] = data
        else:
            # Получили content_type="application/octet-stream"
            data = await part.read(decode=False)
            request_body[part.name] = {  # TODO: доработать класс для файла
                "file_name": part.filename,
                "file_data": data,
            }

    return request_body


async def extract_request_body(request: Request,  is_multipart: bool) -> Any:
    """ Вытаскивает из запроса json или multipart, декодирует его в объект
        python, и возвращает его.
    """
    request_body = None

    if is_multipart:
        request_body = await extract_multipart_request_body(request)
    elif request.body_exists:
        request_body = await request.json()

    return request_body


async def extract_input_data(
    request: Request, is_multipart: bool
) -> InputData:
    """ Извлекает из запроса все входящие данные и возвращает их.
    """
    request_body = await extract_request_body(request, is_multipart)
    url_parts = dict(request.match_info)
    url_query = dict(request.query)

    return InputData(
        request_body=request_body, url_parts=url_parts, url_query=url_query
    )
