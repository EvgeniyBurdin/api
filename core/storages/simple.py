""" Модуль для класса простого хранилища на основе словаря.
"""
from typing import Any, Dict, List, Optional
from uuid import uuid4

from .abstract import AbstractStorage
from .exception import StorageTableDoesNotExistError

_ID_FIELD_NAME = "id"


class SimpleStorage(AbstractStorage):

    def __init__(self) -> None:

        self.db: Dict[str, List[Dict[str, Any]]] = {}

    async def create(
        self, table_name: str, row: Dict[str, Any]
    ) -> Dict[str, Any]:

        row[_ID_FIELD_NAME] = uuid4()

        if table_name not in self.db:
            self.db[table_name] = []

        self.db[table_name].append(row)

        return row

    async def read(
        self, table_name: str, filters: Optional[Dict[str, list]] = None
    ) -> List[Dict[str, Any]]:

        table_data = self._try_get_table_data(table_name)

        if filters is None:
            return table_data

        filtered_table_data = self._apply_filters(table_data, filters)

        return filtered_table_data

    def _apply_filters(
        self, table_data: List[Dict[str, Any]], filters: Dict[str, list]
    ) -> List[Dict[str, Any]]:

        result = []

        for row in table_data:
            for name, value in filters.items():
                if name not in row or value != row[name]:
                    break
            else:
                result.append(row)

        return result

    def _try_get_table_data(self, table_name: str) -> List[Dict[str, Any]]:

        result = self.db.get(table_name)

        if result is None:
            message = f"Table '{table_name}' does not exist"
            raise StorageTableDoesNotExistError(message)

        return result
