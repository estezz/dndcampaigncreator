import unittest
from moto import mock_aws
import os
from unittest.mock import patch, MagicMock
from gemini_client import GeminiClient

@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-2"
    # Note: Setting dummy credentials is important to prevent boto3 from attempting to use real credentials


@pytest.fixture
def mocked_aws(aws_credentials):
    """Mock all AWS interactions for a test function."""
    with mock_aws():
        yield

@mock_aws
class TestGeminiClient(unittest.TestCase):

    def test_generate_text(self):
        """Test the generate_text method."""
        gemini_client = GeminiClient()
        result = gemini_client.generate_text("Generate a DnD story", schema={})
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
