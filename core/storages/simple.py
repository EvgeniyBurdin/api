""" Модуль для класса простого хранилища на основе словаря.
"""
from typing import Any, Dict, List, Union
from uuid import uuid4

from .abstract import AbstractStorage
from .exception import StorageTableDoesNotExistError


ID_FIELD_NAME = "id"


class SimpleStorage(AbstractStorage):

    def __init__(self) -> None:
        self.db: Dict[str, List[Dict[str, Any]]] = {}

    def try_get_table_data(self, table_name: str) -> List[Dict[str, Any]]:

        result = self.db.get(table_name)

        if result is None:
            message = f"Table '{table_name}' does not exist"
            raise StorageTableDoesNotExistError(message)

        return result

    async def read(
        self, table_name: str, ids: Union[None, list] = None
    ) -> List[Dict[str, Any]]:

        table_data = self.try_get_table_data(table_name)

        if ids is None:
            return table_data

        return [row for row in table_data if row[ID_FIELD_NAME] in ids]

    async def create(
        self, table_name: str, row: Dict[str, Any]
    ) -> Dict[str, Any]:

        row[ID_FIELD_NAME] = uuid4()

        if table_name not in self.db:
            self.db[table_name] = []

        self.db[table_name].append(row)

        return row
