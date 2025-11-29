import json
import os
import re
from src.gemini_client import GeminiClient
from jinja2 import Environment, FileSystemLoader    

from flask import Flask, jsonify, request, send_file, send_from_directory

app = Flask(__name__)
campaign_dict = {}

@app.route("/")
def index():
    return send_file('web/index.html')

"""
    This api method generates a campaign from the initial user input. 
    This is the main method that is called from the frontend. 
    It creates a dictionary of the state of the campaign.

    It then creates HTML from the campaign state that is returned to the frontend.
"""
@app.route("/api/generate/campaign", methods=["POST"])
def generate_campaign_api():
    request_json = request.json
    print(request_json)
    
    # Set up the Jinja2 environment to load templates from the current directory
    env = Environment(loader=FileSystemLoader('.'))

    # Load the template
    template = env.get_template('./resources/campaign_prompt.j2')

    # Render the template with the provided data
    prompt = template.render(request_json)
    clean_prompt = prompt.replace("\n", " ")  

    gemini_client = GeminiClient();
    campaign_json_string = gemini_client.generate_text(prompt=clean_prompt)

    clean_campaign_json = string_to_json(campaign_json_string)
    prompt = template.render(json=clean_campaign_json)

    ## Create HTML from the campaign JSON
    template = env.get_template('./resources/turn_json_to_html.j2')
    prompt = template.render(json=clean_campaign_json)
    html = gemini_client.generate_text(prompt=prompt)
    clean_html = html.replace("```html", "")
    clean_html = clean_html.replace("```", "")

    with open("clean.html", "w") as file:
        file.write(clean_html)

    return clean_html

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
            
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('web', path)


if __name__ == "__main__":
    app.run(port=int(os.environ.get('PORT', 80)))
