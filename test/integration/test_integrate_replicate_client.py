import pytest
from replicate_image_client import ReplicateImageClient
import logging
logging.basicConfig(filename='dnd.log', level=logging.DEBUG)


def test_generate_images():
    logger = logging.getLogger(__name__)
    logger.debug("test method")
    client = ReplicateClient()
    prompts = ["dog with a bone", "cat and ball", "singing bird"]
    urls =  client.generate_images(prompts)
    assert len(urls) == len(prompts)
    for url in urls:
        assert url.startswith("http")
    print(urls)