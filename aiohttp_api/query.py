""" Модуль для работы с запросом.
"""
from dataclasses import dataclass
from typing import Any, Optional

from aiohttp.web import Request


@dataclass
class InputData:
    request_body: Any = None
    url_parts: Optional[dict] = None
    url_params: Optional[dict] = None


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
            request_body[part.name] = {
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
    url_params = dict(request.query)

    return InputData(request_body, url_parts, url_params)
