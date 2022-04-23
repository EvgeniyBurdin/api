import pytest
from core.storages import Storage


@pytest.fixture(scope="session")
def storage():
    return Storage()
