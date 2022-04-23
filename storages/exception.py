""" Модуль для классов исключений хранилища.
"""


class StorageError(Exception):
    pass


class StorageTableDoesNotExistError(StorageError):
    pass
