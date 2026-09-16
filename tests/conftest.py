import pytest

from riskintel.demo import seed_repository


@pytest.fixture
def repo():
    return seed_repository()
