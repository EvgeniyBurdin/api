""" Модуль для класса абстрактного хранилища.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List


class AbstractStorage(ABC):

    @abstractmethod
    def read(self) -> List[Dict[str, Any]]:
        pass
