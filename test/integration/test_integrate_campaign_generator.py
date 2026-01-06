
import pytest
from src.campaign_generator import Campaign_Generator

def test_generate_caampaign():
    parameter_dict = {
        "campaignSetting": "A fantasy world",
        "partySize": "4",
        "characterLevel": "5",
        "numberOfSessions": "2",
        "numberOfHoursPerSession": "4",
        "storyLine": "The beer has been poisoned"

    }
    campaign_generator = Campaign_Generator()
    campaign_generator.generate_campaign(parameter_dict=parameter_dict)