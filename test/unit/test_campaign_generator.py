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
def set_test_env():
    """set the test environment"""
    os.environ["FLASK_DEBUG"] = "True"
    

@mock_aws
class TestCampaignGenerator:
    """test the campaign generator"""

    def test_generate_campaign(self, set_test_env):
        """test the generate_campaign method"""

        generator = CampaignGenerator()

        parameter_dict = {
            "campaignSetting": "Forgotten Realms",
            "partySize": 4,
            "characterLevel": 5,
            "numberOfSessions": 2,
            "numberOfHoursPerSession": 4,
            "storyLine": "The beer has been poisoned",
        }

        # Act
        campaign = generator.generate_campaign(parameter_dict)

        # Assert
        assert campaign.json["campaignSetting"] == parameter_dict["campaignSetting"]
        assert campaign.json["partySize"] == parameter_dict["partySize"]
        assert campaign.json["characterLevel"] == parameter_dict["characterLevel"]
        assert campaign.json["numberOfSessions"] == parameter_dict["numberOfSessions"]
        assert campaign.json["numberOfHoursPerSession"] == parameter_dict["numberOfHoursPerSession"]
        assert campaign.json["storyLine"] == parameter_dict["storyLine"]

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
