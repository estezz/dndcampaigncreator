""" This module tests the replicate client with live access to the API"""

from moto import mock_aws
import logging
import os
from pathlib import Path
import pytest
from moto import mock_aws
from replicate_image_client import ReplicateImageClient

base_path = Path(__file__).parent
log_file = base_path / "../logs/test.log"
logging.basicConfig(filename=log_file, level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-2"


@pytest.fixture
def mocked_aws(aws_credentials):  # pylint: disable=redefined-outer-name,unused-argument
    """Mock all AWS interactions for a test function."""
    with mock_aws():
        yield

@pytest.fixture
def setup_env():
    """ setup up the text environment"""
    os.unsetenv("FLASK_DEBUG")


def test_generate_images(setup_env, mocked_aws):
    """This test the generate images method"""
    logger.debug("test method")
    client = ReplicateImageClient()
    prompts = ["dog with a bone", "cat and ball", "singing bird"]
    urls =  client.generate_images(prompts)
    assert len(urls) == len(prompts)
    for key, value in urls.items():
        assert value.startswith("http")
    logger.info(urls)