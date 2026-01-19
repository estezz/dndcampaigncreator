"""this module tests the campaign generator"""

import os
from pathlib import Path
from unittest.mock import patch
from json import JSONDecodeError
import pytest
from moto import mock_aws
from campaign_generator import CampaignGenerator, string_to_json
from campaign import Campaign
import src.campaign_generator as campaign_generator_utils


@pytest.fixture
def aws_credentials():
    """Mock AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-2"


@pytest.fixture
def mocked_aws(aws_credentials):
    """Mock all AWS interactions for a test function."""
    with mock_aws():
        yield


@mock_aws
class TestCampaignGenerator:
    """test the campaign generator"""

    @patch("campaign_generator.GeminiClient")
    @patch("campaign_generator.ReplicateClient")
    def test_generate_campaign(self, MockGeminiClient, MockReplicateClient):
        """test the generate_campaign method"""

        mock_gemini_client = MockGeminiClient())
        mock_gemini_client.generate_text.return_value = """```json
        {
            \"campaignSetting\": \"A fantasy world\",
            \"partySize\": \"4\",
            \"characterLevel\": \"4\",
            \"characterLevel\": \"5\",
            \"numberOfSessions\": \"2\",
            \"numberOfHoursPerSession\": \"4\",
            \"storyLine\": \"The beer has been poisoned\"
        } 
        ``` """

        mock_replicate_client = MockReplicateClient()
        mock_replicate_client.generate_images.return_value = {"prompt1": "url1"}
        generator = CampaignGenerator()
        generator.gemini_client = mock_gemini_client
        generator.replicate_client = mock_replicate_client

        base_path = Path(__file__).parent
        generator.templates_path = (base_path / "templates").resolve()
        generator.__init__()  # pylint: disable=C2801

        parameter_dict = {
            "campaignSetting": "A fantasy world",
            "partySize": "4",
            "characterLevel": "5",
            "numberOfSessions": "2",
            "numberOfHoursPerSession": "4",
            "storyLine": "The beer has been poisoned",
        }

        # Act
        campaign = generator.generate_campaign(parameter_dict)

        # Assert
        assert campaign.json["campaignSetting"] == "A fantasy world"
        assert campaign.json["partySize"] == "4"
        assert campaign.json["characterLevel"] == "5"
        assert campaign.json["numberOfSessions"] == "2"
        assert campaign.json["numberOfHoursPerSession"] == "4"
        assert campaign.json["storyLine"] == "The beer has been poisoned"

        mock_gemini_client.generate_text.assert_called_once()

    def test_string_to_json_with_json(self):
        """test the string_to_json method"""
        # Arrange
        input_string = """```json 
        {"key": "value"}
        ``` """
        expected_json = {"key": "value"}

        # Act
        result = string_to_json(input_string)

        # Assert
        assert result == expected_json

    def test_string_to_json_no_json(self):
        """test the string_to_json method with no non JSON string"""
        with pytest.raises(JSONDecodeError) as execinfo:
            # Arrange
            input_string = "this is not json"

            # Act
            string_to_json(input_string)

            # Assert
            assert "Expecting value" in str(execinfo.value)

    def test_replace_value(self):
        """test the replace_value method"""

        campaign = {
            "image_prompt": "pretty_image1",
            "key2": "value2",
            "steps": {"image_prompt": "pretty_image2"},
        }

        with_images = {
            "image_prompt": "foundIt",
            "key2": "value2",
            "steps": {"image_prompt": "foundIt"},
        }
        campaign_generator_utils.replace_item(campaign, "image_prompt", "foundIt")

        assert campaign == with_images
