""" Модуль для класса абстрактного хранилища.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class AbstractStorage(ABC):

    @abstractmethod
    async def create(
        self, table_name: str, row: Dict[str, Any]
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def read(
        self, table_name: str, ids: Optional[list] = None
    ) -> List[Dict[str, Any]]:
        pass
