"""Функции для создания документации."""

import json
from dataclasses import dataclass
from typing import Optional, Type, Callable, Tuple, List

from pydantic import create_model
from pydantic.main import BaseModel
from pydantic.schema import schema

from core.data_classes.base import BaseMultipartDC


TAGS_DOCSTRING_MARKER = ":swagger_tags:"


@dataclass
class HandlerDoc:
    """  Документация из докстринга обработчика.

        (после согласования формата докстринга, может быть дополнен/изменен)
    """
    title: str
    content: str
    tags: List[str]


@dataclass
class ServerWrap:
    """ Описание класса-оболочки."""

    wrap_class: Type[BaseModel]
    # Имя свойства у wrap_class в котором должна быть структура из
    # аннотации обработчика (например "params" для текущей оболочки запроса
    # или "result" для ответа)
    root_name: str


@dataclass
class ServerError:
    """ Описание ошибки."""

    code: str
    description: str


def extract_tags(strings: List[str]) -> List[str]:

    pos = None
    for i, string in enumerate(strings):
        if string.startswith(TAGS_DOCSTRING_MARKER):
            pos = i

    result = ["Общие"]
    if pos is not None:
        str_tags = strings.pop(pos)
        str_tags = str_tags.replace(TAGS_DOCSTRING_MARKER, "")
        str_tags = str_tags.strip()
        tags = str_tags.split(",")
        result = [tag.strip() for tag in tags if tag]

    return result


def parse_handler_docstring(docstring: str) -> HandlerDoc:
    """ Парсит докстринг обработчика и возращает разделы документации.

        (после согласования формата докстринга, может быть дополнен/изменен)
    """

    docstring = docstring or "no description"

    strings = docstring.split("\n")
    strings = [s.strip() for s in strings if s]

    tags = extract_tags(strings)

    title = content = strings[0]

    if len(strings) > 1:
        content = "\n".join(strings[1:]).strip()

    return HandlerDoc(title=title, content=content, tags=tags)


def create_schema_class(
    wrap: Optional[ServerWrap], class_name: str, root_name: str, annotation
) -> Type[BaseModel]:
    """ Создает и возвращает класс, который будет использован для формирования
        схемы запроса/ответа сервера.
    """
    if wrap is None:
        base_class = None
    else:
        root_name = wrap.root_name
        base_class = wrap.wrap_class

    return create_model(
        class_name,
        **{root_name: (annotation, ...), "__base__": base_class}
    )


def make_multipart_request_body(input_annotation) -> dict:

    s = input_annotation.schema()
    s.pop("definitions", None)

    for k, v in s["properties"].items():
        if "$ref" in v:
            if v["$ref"] == "#/definitions/BaseFileDC":
                s["properties"][k] = {"type": "string", "format": "binary"}
        if "allOf" in v:
            if v["allOf"][0]["$ref"] == "#/definitions/BaseFileDC":
                v["allOf"][0] = {"type": "string", "format": "binary"}

    return {"content": {"multipart/form-data": {"schema": s}}}


def swagger_preparation(
    handlers: List[Callable],
    arg_name: str,
    request_wrap: Optional[ServerWrap] = None,
    response_wrap: Optional[ServerWrap] = None,
    error_class: Optional[Type[BaseModel]] = None,
    error_descriptions: Tuple[ServerError] = (
        ServerError("400", "Неправильный, некорректный запрос"),
        ServerError("401", "Ошибка авторизации"),
        ServerError("403", "Доступ запрещен"),
        ServerError("500", "Внутренняя ошибка сервера")
    )
) -> dict:
    """ Подготовка документации для использования библиотекой aiohttp_swagger.

        :handlers: Список обработчиков апи-методов.
        :arg_name: Имя аргумента у апи-метода по аннотации которого будет
                   формироваться документация для входящих данных запроса.
        :request_wrap:  Описание класса для обертки входящих данных сервера.
        :response_wrap: Описание класса для обертки исходящих данных сервера.
        :error_class:   Класс для ответа с ошибкой.
        :error_descriptions: Описания ошибок

        1. Изменяет у каждого обработчика docstring (вставляет в docstring
        схему для аргумента с именем arg_name и для результата).

        2. Собирает словарь result_definitions со схемами всех, используемых
        в приложении, классов данных.

        Возвращает словарь result_definitions.

        (словарь result_definitions затем передается в вызове
        aiohttp_swagger.setup_swagger(..., definitions=result_definitions, ...)
        при старте приложения)
    """
    result_definitions = {}

    server_classes = [
        wrap.wrap_class for wrap in (request_wrap, response_wrap)
        if wrap is not None
    ]
    if error_class is not None:
        server_classes.append(error_class)

    if server_classes:
        server_schema = schema(
            server_classes, ref_prefix='#/components/schemas/'
        )
        result_definitions.update(server_schema["definitions"])

    for handler in handlers:

        input_annotation = handler.__annotations__.get(arg_name)
        output_annotation = handler.__annotations__["return"]

        schema_classes = tuple()

        request_root_name: Optional[str] = None
        Request: Optional[Type[BaseModel]] = None
        if input_annotation is not None:
            request_root_name = "request"
            Request = create_schema_class(
                request_wrap, "Request", request_root_name, input_annotation
            )
            schema_classes += (Request, )

        output_annotation = handler.__annotations__["return"]
        response_root_name = "response"
        Response = create_schema_class(
            response_wrap, "Response", response_root_name, output_annotation
        )
        schema_classes += (Response, )

        handler_schema = schema(
            schema_classes, ref_prefix="#/components/schemas/"
        )

        definitions = handler_schema["definitions"]

        request_schema = {}
        if Request is not None:
            request_schema = definitions["Request"]
            if request_wrap is None:
                request_schema = request_schema[
                    "properties"
                ][request_root_name]

        r200_schema = definitions["Response"]

        if response_wrap is None:
            r200_schema = r200_schema["properties"][response_root_name]

        handler_docstring = parse_handler_docstring(handler.__doc__)

        docstring = {
            "summary": handler_docstring.title,
            "tags": handler_docstring.tags,
            "description": handler_docstring.content,
            "responses": {
                "200": {
                    "description": "Успешная операция",
                    "content": {
                        "application/json": {
                            "schema": r200_schema
                        }
                    }
                },
            },
        }

        if request_schema:
            docstring["requestBody"] = {
                "required": True,
                "content": {
                    "urlencoded": {
                        "schema": request_schema
                    }
                }
            }
        if input_annotation is not None:
            if issubclass(input_annotation, BaseMultipartDC):
                docstring["requestBody"] = make_multipart_request_body(
                    input_annotation
                )

        if request_wrap is not None and request_schema:
            docstring["parameters"] = [{
                "in": "body",
                "name": arg_name,
                "required": True,
                "schema": request_schema["properties"][request_wrap.root_name]
            }]

        if error_class is not None:
            for error in error_descriptions:
                docstring["responses"][error.code] = {
                    "description": error.description,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref":
                                f"#/components/schemas/{error_class.__name__}"
                            }
                        }
                    }
                }

        handler.__doc__ = json.dumps(docstring)

        # Следующая строка только для работы с либой aiohttp_swagger3
        handler.__doc__ = " \n --- \n " + handler.__doc__

        definitions.pop("Request", None)
        definitions.pop("Response")

        result_definitions.update(definitions)

    return result_definitions
