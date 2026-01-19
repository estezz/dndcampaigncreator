"""test the campaign_generator with live AI APIs"""

import os
import json
import pytest
import boto3
from moto import mock_aws
from campaign_generator import CampaignGenerator


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


@mock_aws
class TestCampaignGenerator:  # pylint: disable=too-few-public-methods
    """test the campaign generator"""

    def set_secret(self):
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
    def test_generate_campaign(self):
        """Test the generate_campaign method with live AI APIs"""
        
        self.set_secret()

        parameter_dict = {
            "campaignSetting": "A fantasy world",
            "partySize": "4",
            "characterLevel": "5",
            "numberOfSessions": "2",
            "numberOfHoursPerSession": "4",
            "storyLine": "The beer has been poisoned",
        }
        campaign_generator = CampaignGenerator()
        campaign_generator.generate_campaign(parameter_dict=parameter_dict)

    def test_edit_campaign_text(self):
        """Test the edit_campaign_text method with live AI APIs"""

        self.set_secret()
        
        parameter_dict = {
            "campaignSetting": "A fantasy world",
            "partySize": "4",
            "characterLevel": "5",
            "numberOfSessions": "2",
            "numberOfHoursPerSession": "4",
            "storyLine": "The beer has been poisoned",
        }
        campaign_generator = CampaignGenerator()

        new_text = campaign_generator.edit_campaign_text(
            "build a new setup", "setup", parameter_dict
        )
        print(new_text)
