
import pytest
from src.campaign_generator import CampaignGenerator

def test_generate_caampaign():
    parameter_dict = {
        "campaignSetting": "A fantasy world",
        "partySize": "4",
        "characterLevel": "5",
        "numberOfSessions": "2",
        "numberOfHoursPerSession": "4",
        "storyLine": "The beer has been poisoned"

    }
    campaign_generator = CampaignGenerator()
    campaign_generator.generate_campaign(parameter_dict=parameter_dict)

def test_edit_campaign_text():
    parameter_dict = {
        "campaignSetting": "A fantasy world",
        "partySize": "4",
        "characterLevel": "5",
        "numberOfSessions": "2",
        "numberOfHoursPerSession": "4",
        "storyLine": "The beer has been poisoned"

    }
    campaign_generator = CampaignGenerator()

    new_text = campaign_generator.edit_campaign_text("build a new setup", "setup", parameter_dict)
    print(new_text)