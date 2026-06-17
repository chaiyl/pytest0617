import pytest


@pytest.mark.smoke
def test_framework_is_ready(logger):
    logger.info("pytest framework is ready---")
    assert True
