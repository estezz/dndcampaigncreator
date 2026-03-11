import logging
import pytest
from src.runware_image_client import RunwareImageClient

logger = logging.getLogger(__name__)

@pytest.fixture
def client():
    return RunwareImageClient(api_key="test_key")

def test_generate_images():
    client = RunwareImageClient()
    prompts = ["a cat", "a dog"]
    urls = client.generate_images(prompts)

    assert len(urls) == len(prompts)
    for key, value in urls.items():
        assert value.startswith("http")
    logger.info(urls)