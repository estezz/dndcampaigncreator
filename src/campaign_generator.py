"""this module creates campaigns using a prompt and AI"""

import json
import os
import html
import base64
import logging
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape, meta
from gemini_text_client import GeminiTextClient
from campaign import CampaignSchema
from campaign import Campaign
from replicate_image_client import ReplicateImageClient
from mock_text_client import MockTextClient
from mock_image_client import MockImageClient
import campaign_generator as campaign_generator_utils


logger = logging.getLogger(__name__)


class CampaignGenerator:
    """this class creates campaigns using a prompt and AI"""

    base_path = Path(__file__).parent
    templates_path = (base_path / "templates").resolve()

    def __init__(self):
        self.campaign = Campaign()

        if "FLASK_DEBUG" in os.environ and os.environ["FLASK_DEBUG"] == "True":
            self.image_client = MockImageClient()
            self.text_client = MockTextClient()
        else:
            self.image_client = ReplicateImageClient()
            self.text_client = GeminiTextClient()

        # Set up the Jinja2 environment to load templates from the current directory
        self.main_campaign_template = "main_campaign_template.html"
        self.campaign_prompt_template = "campaign_prompt.j2"

        env = Environment(
            loader=FileSystemLoader(
                self.templates_path
            ),  # Assuming templates are in src/templates
            autoescape=select_autoescape(["html", "js", "j2"]),
        )

        # Load the templates
        self.campaign_template = env.get_template(self.campaign_prompt_template)
        self.html_template = env.get_template(self.main_campaign_template)

    def generate_campaign(self, parameter_dict):
        """this method uses AI and templates to create a DnD Campaign in HTML format"""

        # Render the template with the provided data
        prompt = self.campaign_template.render(parameter_dict)
        clean_prompt = prompt.replace("\n", " ")

        campaign_json_string = self.text_client.generate_text(
            prompt=clean_prompt, schema=CampaignSchema.model_json_schema()
        )
        clean_campaign_json = string_to_json(campaign_json_string)
        self.campaign.json = clean_campaign_json
        # print(self.gemini_client.generate_text())
        self.add_images_to_json(self.campaign.json)

        ## Create HTML from the campaign JSON
        self.campaign.html = html.unescape(
            self.html_template.render(self.campaign.json)
        )
        logger.debug("returning campaign")

        return self.campaign

    def add_images_to_json(self, dictionary):
        """This uses the promt in the json to create an image
        then add the image to the json
        """

        # get all the image prompts and create images from the json
        images_prompts = []
        self.collect_images_prompts(dictionary, images_prompts)
        image_dict = self.image_client.generate_images(images_prompts)

        # add the images to the json
        self.add_images(dictionary, image_dict)
        return image_dict

    def collect_images_prompts(self, dictionary, images_prompts):
        """get all the image prompts from the json"""

        for key, value in dictionary.items():
            if isinstance(value, dict):
                self.collect_images_prompts(
                    dictionary=value, images_prompts=images_prompts
                )
            elif isinstance(value, list):
                for item in value:
                    self.collect_images_prompts(
                        dictionary=item, images_prompts=images_prompts
                    )
            if "Image" in key or "image" in key:
                images_prompts.append(value["prompt"])

    def add_images(self, dictionary, image_dict):
        """add images to campaign  json"""

        for key, value in dictionary.items():
            if isinstance(value, dict):
                self.add_images(dictionary=value, image_dict=image_dict)
            elif isinstance(value, list):
                for item in value:
                    self.add_images(dictionary=item, image_dict=image_dict)
            if "Image" in key or "image" in key:
                value["url"] = image_dict[value["prompt"]]

    def edit_campaign_text(self, prompt, element_id, campaign_json):
        """generate a new value for the element id"""

        env = Environment(
            loader=FileSystemLoader(
                self.templates_path
            ),  # Assuming templates are in src/templates
            autoescape=select_autoescape(["html", "js"]),
        )
        # Load the template
        template_name = f"{element_id}.html"
        section_template = env.get_template(template_name)
        template_source = env.loader.get_source(env, template_name)[0]
        template_variables = meta.find_undeclared_variables(env.parse(template_source))

        prompt_with_instructions = f""" edit the '{template_variables}' element in this JSON
         using this prompt : {prompt}, \n
        {campaign_json}"""

        campaign_json_string = self.text_client.generate_text(
            prompt=prompt_with_instructions,
            schema=CampaignSchema.model_json_schema(),
        )
        self.campaign.json = json.loads(campaign_json_string)

        section_html = html.unescape(section_template.render(self.campaign.json))

        return section_html


def string_to_json(input_string):
    """This method takes a JSON-ish string and cleans it up and loads it into a json object"""

    clean_string = input_string
    clean_string = clean_string.replace("\n", " ")
    clean_string = clean_string.replace("```json", "")
    clean_string = clean_string.replace("```", "")
    clean_json = {}

    clean_json = json.loads(clean_string)

    return clean_json


def replace_item(obj, key, replace_value):
    """This method finds a key in a dictionary and replaces
    the value with the supplied replace_value"""
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
