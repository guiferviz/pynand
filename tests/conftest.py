import pytest


@pytest.fixture(params=[True, False])
def only_nand(request):
    return request.param
