import json
import os
import re, html
from pathlib import Path
from src.gemini_client import GeminiClient
from src.campaign import Campaign_Schema
from src.campaign import Campaign
from src.replicate_client import ReplicateClient

from jinja2 import Environment, FileSystemLoader, select_autoescape
import base64

campaign = Campaign()
replicate_client = ReplicateClient()


class Campaign_Generator:

    def generate_campaign(self, parameter_dict):
        # Set up the Jinja2 environment to load templates from the current directory
        base_path = Path(__file__).parent
        print(f"test location {base_path}")

        # Join the base path with the filename
        templates_path = (base_path / "templates" ).resolve()
        env = Environment(
                loader=FileSystemLoader(templates_path),  # Assuming templates are in src/templates
                autoescape=select_autoescape(["html", "js"])
            )
        # Load the template
        template = env.get_template("campaign_prompt.j2")

        # Render the template with the provided data
        prompt = template.render(parameter_dict)
        clean_prompt = prompt.replace("\n", " ")

        gemini_client = GeminiClient()
        campaign_json_string = gemini_client.generate_text(
            prompt=clean_prompt, schema=Campaign_Schema.model_json_schema()
        )
        clean_campaign_json = string_to_json(campaign_json_string)
        campaign.json = clean_campaign_json

        print(f"before Images: {json.dumps(campaign.json)}")
        self.add_images_to_json(campaign.json)
        print(f"after Images: {json.dumps(campaign.json)}")

        ## Create HTML from the campaign JSON
        template = env.get_template("main_campaign_template.html")
        campaign.html = html.unescape(template.render(campaign.json))
        print(f"campaign html: {campaign.html}")
        print("returning campaign")

        return campaign

    def add_images_to_json(self, dictionary):
        """use the promt in the json to create an image
        then add the image to the json
        """
        for key, value in dictionary.items():
            if isinstance(value, dict):
                self.add_images_to_json(dictionary=value)
            elif isinstance(value, list):
                for item in value:
                    self.add_images_to_json(dictionary=item)
            if "Image" in key or "image" in key:
                print(f"prompt: {value['prompt']}")
                image_url = replicate_client.generate_image_url(value["prompt"])
                value["url"] = image_url

        return dictionary


def generate_image():
    # image = campaign_generator_utils.file_to_base64_string('my-image.png')
    replicate_client = ReplicateClient()
    image = replicate_client.generate_image_url("a dog in a park")

    html = f'<img src="{image}" class="img-fluid" alt="Description of the image">'
    return html


def string_to_json(input_string):
    match = re.search(r"json\s*([\s\S]*?)\s*", input_string, re.DOTALL)

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


# Source - https://stackoverflow.com/a/45335542
# Posted by Farmer Joe, modified by community. See post 'Timeline' for change history
# Retrieved 2025-12-13, License - CC BY-SA 3.0


def replace_item(obj, key, replace_value):
    for k, v in obj.items():
        if isinstance(v, dict):
            obj[k] = replace_item(v, key, replace_value)
    if key in obj:
        obj[key] = replace_value
    return obj


def file_to_base64_string(filename):
    """
    Reads a file into memory and returns its content as a Base64-encoded string.
    """
    try:
        # Step 1 & 2: Open file in binary mode and read bytes
        with open(filename, "rb") as file_in:
            file_content_bytes = file_in.read()

        # Step 3: Encode the bytes into Base64 format (results in bytes again)
        encoded_content_bytes = base64.b64encode(file_content_bytes)

        # Step 4: Decode the Base64 bytes into a standard ASCII string
        base64_string = encoded_content_bytes.decode("ascii")

        return base64_string

    except FileNotFoundError:
        return f"Error: The file '{filename}' was not found."
    except Exception as e:
        return f"An error occurred: {e}"
