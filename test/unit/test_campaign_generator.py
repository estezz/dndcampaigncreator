import pytest
from unittest.mock import MagicMock, patch
from src.campaign_generator import Campaign_Generator, string_to_json
from src.state_classes import Campaign

class TestCampaignGenerator:
    @patch('src.campaign_generator.GeminiClient')
    def test_generate_campaign(client, MockGeminiClient):
        # Arrange
        mock_gemini_client = MockGeminiClient.return_value
        mock_gemini_client.generate_text.return_value = """```json 
        {"title": "My Campaign"} 
        ``` """
        mock_gemini_client.generate_html.return_value = """```html 
        <h1>My Campaign</h1> 
        ``` """

        generator = Campaign_Generator()
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
        assert campaign.json == {"title": "My Campaign"}
        assert "<h1>My Campaign</h1>" in campaign.html
        mock_gemini_client.generate_text.assert_called_once()

def test_string_to_json_with_json():
    # Arrange
    input_string = """(```json \n)
    ({"key": "value"} \n)
    (``` /n) """
    expected_json = {"key": "value"}

    # Act
    result = string_to_json(input_string)

    # Assert
    assert result == expected_json

def test_string_to_json_no_json():
    # Arrange
    input_string = 'this is not json'

    # Act
    result = string_to_json(input_string)

    # Assert
    assert result == 'this is not json'
