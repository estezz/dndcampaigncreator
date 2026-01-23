"""This module test the integration with the Gemini API"""

import unittest
import os
import logging
import json
from pathlib import Path
import pytest
from moto import mock_aws
import boto3
from gemini_text_client import GeminiTextClient


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


@mock_aws
class TestGeminiClient(unittest.TestCase): # pylint: disable=too-few-public-methods
    """test the campaign generator"""

    def set_secret(self):
        """set a secret in the mocked environment"""
        
        region = 'us-east-2'
        client = boto3.client("secretsmanager", region_name=region)
        secret_name = "GEMINI_API_KEY"
        api_key = os.environ["GEMINI_API_KEY"]
        secret_value = json.dumps({"GEMINI_API_KEY": api_key})

        # 2. Create the secret in the mocked environment
        # The create_secret call returns an ARN, but we should use the name
        # for retrieval within Moto.
        client.create_secret(
            Name=secret_name,
            SecretString=secret_value
        )


    def test_generate_text(self):
        """Test the live Gemini API."""
        
        self.set_secret()
        gemini_client = GeminiTextClient()
        result = gemini_client.generate_text("Generate a DnD story", schema={})
        self.assertIsNotNone(result)
