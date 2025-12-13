import json
import os
import re
from src.gemini_client import GeminiClient
from src.state_classes import Campaign_Schema
from src.state_classes import Campaign

from jinja2 import Environment, FileSystemLoader    

campaign = Campaign()

class Campaign_Generator:

    def generate_campaign(self, parameter_dict):
        # Set up the Jinja2 environment to load templates from the current directory
        env = Environment(loader=FileSystemLoader('.'))

        # Load the template
        template = env.get_template('./resources/campaign_prompt.j2')

        # Render the template with the provided data
        prompt = template.render(parameter_dict)
        clean_prompt = prompt.replace("\n", " ")  

        gemini_client = GeminiClient();
        campaign_json_string = gemini_client.generate_text(prompt=clean_prompt, schema=Campaign_Schema.model_json_schema())
        clean_campaign_json = string_to_json(campaign_json_string)
        campaign.json = clean_campaign_json
        prompt = template.render(json=clean_campaign_json)

        ## Create HTML from the campaign JSON

        template = env.get_template('./resources/campaign_html_template.j2')
        campaign.html = template.render( clean_campaign_json )     
        print("returning campaign")
        
        return campaign

def string_to_json(input_string):
    match = re.search(r'json\s*([\s\S]*?)\s*', input_string, re.DOTALL) 
    
    json_string = input_string

    clean_string = json_string
    clean_string = clean_string.replace("\n", " ") 
    clean_string = clean_string.replace("```json", "")
    clean_string = clean_string.replace("```", "")
    clean_json = {}
    try:
        clean_json = json.loads(clean_string)
    except Exception as e:
        print(f"Error: {e}")
    return clean_json


def find_key_recursive(obj, target_key, return_dict):

    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == target_key:
                print(f"Found '{target_key}' with value: {value} and name {value['name']}")
                return_dict[value['name']] = value
            else:
                find_key_recursive(value, target_key, return_dict=return_dict)
    elif isinstance(obj, list):
        for item in obj:
            find_key_recursive(item, target_key,return_dict=return_dict)
            