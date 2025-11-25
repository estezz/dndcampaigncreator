import json
import os
from src.gemini_client import GeminiClient
from jinja2 import Environment, FileSystemLoader    

from flask import Flask, jsonify, request, send_file, send_from_directory

app = Flask(__name__)

@app.route("/")
def index():
    return send_file('web/index.html')


@app.route("/api/generate", methods=["POST"])
def generate_api():
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
    campaign_json = gemini_client.generate_text(prompt=clean_prompt)
    clean_campaign_json = campaign_json.replace("\n", " ")  


    ## Create HTML from the campaign JSON
    template = env.get_template('./resources/turn_json_to_html.j2')
    prompt = template.render(json=clean_campaign_json)
    html = gemini_client.generate_text(prompt=prompt)
    clean_html = html.replace("\n", " ")  

    with open("clean.html", "w") as file:
        file.write(clean_html)

    return clean_html

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
