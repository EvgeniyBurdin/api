from aiohttp import web


async def health_check(request: web.Request) -> web.Response:
    """
    Проверка состояния сервера

    ---
    summary: Проверка состояния сервера
    tags:
        - служебные
    description: Проверка состояния сервера
    responses:
        '200':
            description: Успешная операция.
    """
    return web.Response(text="OK")
