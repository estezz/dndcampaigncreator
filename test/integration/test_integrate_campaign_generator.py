
import pytest
import src.campaign_generator as campaign_generator

def test_generate_caampaign():
    parameter_dict = {
        "campaignSetting": "A fantasy world",
        "partySize": "4",
        "characterLevel": "5",
        "numberOfSessions": "2",
        "numberOfHoursPerSession": "4",
        "storyLine": "The beer has been poisoned"

    }
    campaign_generator.generate_campaign(parameter_dict=parameter_dict)