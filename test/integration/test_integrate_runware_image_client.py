import logging
import pytest
from src.runware_image_client import RunwareImageClient

logger = logging.getLogger(__name__)


@pytest.fixture
def client():
    return RunwareImageClient(api_key="test_key")


def test_generate_images():
    client = RunwareImageClient()
    input = [{"prompt": "a dragon gone wild", "context": "a fantasy world"}, {"prompt": "a hobit", "context": "the shire"}]
    urls = client.generate_images(input)

    assert len(urls) == len(input)
    for key, value in urls.items():
        assert value.startswith("http")
    logger.info(urls)
