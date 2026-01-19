import pytest
from moto import mock_aws
from unittest.mock import MagicMock, patch
from campaign_generator import CampaignGenerator, string_to_json
from campaign import Campaign
import campaign_generator as campaign_generator_utils
import os
from pathlib import Path


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
class TestCampaignGenerator:
    """test the campaign generator"""

    @patch("campaign_generator.GeminiClient")
    def test_generate_campaign(self, MockGeminiClient):
        """ test the generate_campaign method"""

        mock_gemini_client = MockGeminiClient.return_value
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

        generator = CampaignGenerator()
        generator.gemini_client = mock_gemini_client
        base_path = Path(__file__).parent
        generator.templates_path = (base_path / "templates").resolve()
        generator.__init__()
        
        parameter_dict = {
            "campaignSetting": "A fantasy world",
            "partySize": "4",
            "characterLevel": "5",
            "numberOfSessions": "2",
            "numberOfHoursPerSession": "4",
            "storyLine": "The beer has been poisoned"
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


# def test_string_to_json_with_json():
#     # Arrange
#     input_string = """(```json \n)
#     ({"key": "value"} \n)
#     (``` /n) """
#     expected_json = {"key": "value"}

#     # Act
#     result = string_to_json(input_string)

#     # Assert
#     assert result == expected_json

# def test_string_to_json_no_json():
#     # Arrange
#     input_string = 'this is not json'

#     # Act
#     result = string_to_json(input_string)

#     # Assert
#     assert result == 'this is not json'

# def test_replace_value():
#     campaign = {
#         "image_prompt": "pretty_image1",
#         "key2": "value2",
#         "steps": {"image_prompt": "pretty_image2"}
#     }

#     with_images = {
#         "image_prompt": "foundIt",
#         "key2": "value2",
#         "steps": {"image_prompt": "foundIt"}
#     }
#     campaign_generator_utils.replace_item(campaign, "image_prompt", "foundIt")


#     assert campaign == with_images
