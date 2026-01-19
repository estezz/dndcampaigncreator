"""This module makes these pytest fixtures available to all test modules in this directory"""

import os
from moto import mock_aws
import pytest


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
def mocked_aws(aws_credentials): # pylint: disable=redefined-outer-name,unused-argument
    """Mock all AWS interactions for a test function."""
    with mock_aws():
        yield
