"""Функции для создания документации."""

import json
import re
from dataclasses import dataclass
from typing import List, Optional, Tuple, Type

from aiohttp import web
from pydantic import create_model
from pydantic.main import BaseModel
from pydantic.schema import schema


@dataclass
class HandlerDoc:
    """  Документация из докстринга обработчика.

        (после согласования формата докстринга, может быть дополнен/изменен)
    """
    title: str
    content: str


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


def parse_handler_docstring(docstring: str) -> HandlerDoc:
    """ Парсит докстринг обработчика и возращает разделы документации.

        (после согласования формата докстринга, может быть дополнен/изменен)
    """

    docstring = docstring or "no description"

    strings = docstring.split("\n")
    strings = [s.strip() for s in strings if s]

    title = content = strings[0]

    if len(strings) > 1:
        content = "\n".join(strings[1:]).strip()

    return HandlerDoc(title=title, content=content)


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


def make_parameters_in_path(route: web.RouteDef) -> List[dict]:
    """ Создает описание для параметров в пути к методу и возвращает его.
    """
    result = []

    param_names = re.findall(r"{(.*?)}", route.path)

    for param_name in param_names:

        # Каждый параметр в пути к методу, должен быть аргументом у метода,
        # и иметь аннотацию
        annotation = route.handler.__annotations__.get(param_name)

        # Для создания схемы воспользуемся временным классом Tmp
        tmp_class = create_schema_class(None, "Tmp", param_name, annotation)
        # Извлечем из схемы этого класса свойства для параметра
        props = tmp_class.schema()["properties"][param_name]
        # Созданим описание для параметра
        parameter = {
            "name": param_name,
            "in": "path",
            "required": True,
            "schema": {"type": props["type"]}
        }
        format_ = props.get("format")
        if format_ is not None:
            parameter["schema"]["format"] = format_

        # При создании роута можно дополнительно указать любые свойства для
        # параметра. Так как из аннотации к аргументу нам не доступны
        # description и example, то их можно указать там (см. модуль routes.py)
        if "swagger_path_parameters" in route.kwargs:
            if param_name in route.kwargs["swagger_path_parameters"]:
                add = route.kwargs["swagger_path_parameters"][param_name]
                parameter.update(add)

        result.append(parameter)

    return result


def get_tags(route: web.RouteDef, default: List[str]) -> List[str]:
    """ Извлекает из роута тэги для метода и возвращает их.
    """
    # При создании роута можно дополнительно указать тэги для метода.
    # (см. модуль routes.py)
    if "swagger_handler_tags" in route.kwargs:
        return route.kwargs["swagger_handler_tags"]
    else:
        return default


def make_parameters_in_query(
    route: web.RouteDef, url_query_data_class: Type[BaseModel],
) -> List[dict]:
    """ Создает описание для параметров запроса в пути к методу и
        возвращает его.
    """
    result = []

    for ann in route.handler.__annotations__.values():
        if isinstance(ann, type) and issubclass(ann, url_query_data_class):
            schema = ann.schema()
            required = schema.get("required", [])
            # Извлечем из схемы класса свойства для его полей
            for name, props in schema["properties"].items():
                # Созданим описание для параметра
                parameter = {
                    "name": name,
                    "in": "query",
                    "required": name in required,
                    "schema": {"type": props["type"]}
                }

                example_ = props.get("example")
                if example_ is not None:
                    parameter["example"] = example_

                description_ = props.get("description")
                if description_ is not None:
                    parameter["description"] = description_

                format_ = props.get("format")
                if format_ is not None:
                    parameter["schema"]["format"] = format_

                result.append(parameter)

    return result


def swagger_preparation(
    routes: List[web.RouteDef],
    request_body_arg_name: str,
    multipart_data_class: Type[BaseModel],
    url_query_data_class: Type[BaseModel],
    error_data_class: Optional[Type[BaseModel]] = None,
    error_descriptions: Tuple[ServerError] = (
        ServerError("400", "Неправильный, некорректный запрос"),
        ServerError("401", "Ошибка авторизации"),
        ServerError("500", "Внутренняя ошибка сервера")
    )
) -> dict:
    """ Подготовка документации для использования библиотекой aiohttp_swagger.

        :handlers:              Список обработчиков апи-методов.
        :request_body_arg_name: Имя аргумента у апи-метода по аннотации
                                которого будет формироваться документация для
                                входящих данных запроса.
        :error_class:           Класс для ответа с ошибкой.
        :error_descriptions:    Описания ошибок

        1. Изменяет у каждого обработчика docstring (вставляет в docstring
        схему для аргумента с именем arg_name и для результата).

        2. Собирает словарь result_definitions со схемами всех, используемых
        в приложении, классов данных.

        Возвращает словарь result_definitions.
    """
    result_definitions = {}

    server_classes = []
    if error_data_class is not None:
        server_classes.append(error_data_class)

    if server_classes:
        server_schema = schema(
            server_classes, ref_prefix='#/components/schemas/'
        )
        result_definitions.update(server_schema["definitions"])

    for route in routes:

        handler = route.handler

        input_annotation = handler.__annotations__.get(request_body_arg_name)
        output_annotation = handler.__annotations__["return"]

        schema_classes = tuple()

        request_root_name: Optional[str] = None
        Request: Optional[Type[BaseModel]] = None
        if input_annotation is not None:
            request_root_name = "request"
            Request = create_schema_class(
                None, "Request", request_root_name, input_annotation
            )
            schema_classes += (Request, )

        output_annotation = handler.__annotations__["return"]
        response_root_name = "response"
        Response = create_schema_class(
            None, "Response", response_root_name, output_annotation
        )
        schema_classes += (Response, )

        handler_schema = schema(
            schema_classes, ref_prefix="#/components/schemas/"
        )

        definitions = handler_schema["definitions"]

        request_schema = {}
        if Request is not None:
            request_schema = definitions["Request"]
            request_schema = request_schema["properties"][request_root_name]

        r200_schema = definitions["Response"]
        r200_schema = r200_schema["properties"][response_root_name]

        handler_docstring = parse_handler_docstring(handler.__doc__)

        docstring = {
            "summary": handler_docstring.title,
            "tags": get_tags(route, ["Общие"]),
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
            if issubclass(input_annotation, multipart_data_class):
                docstring["requestBody"] = make_multipart_request_body(
                    input_annotation
                )

        if error_data_class is not None:
            for error in error_descriptions:
                docstring["responses"][error.code] = {
                    "description": error.description,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref":
                                f"#/components/schemas/{error_data_class.__name__}"  # noqa
                            }
                        }
                    }
                }

        parameters_in_path = make_parameters_in_path(route)
        parameters_in_query = make_parameters_in_query(
            route, url_query_data_class
        )

        if parameters_in_path or parameters_in_query:
            docstring["parameters"] = parameters_in_path + parameters_in_query

        handler.__doc__ = json.dumps(docstring)

        # Следующая строка только для работы с либой aiohttp_swagger3
        handler.__doc__ = " \n --- \n " + handler.__doc__

        definitions.pop("Request", None)
        definitions.pop("Response")

        result_definitions.update(definitions)

    return result_definitions
