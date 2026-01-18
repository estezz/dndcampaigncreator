from campaign_generator import Campaign_Generator
import campaign_generator as campaign_generator_utils
from replicate_client import ReplicateClient
from flask import Flask, jsonify, request, send_file, send_from_directory, render_template, session
import os
from pathlib import Path
import json
import uuid
import logging
logging.basicConfig(filename='../logs/dnd.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)


app = Flask(__name__, template_folder="templates")
app.secret_key = 'your_super_secret_key'
campaign_dict = {}
campaign_generator = Campaign_Generator()


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
    campaign_input = request.get_json()
    logger.debug(campaign_input)
    campaign = campaign_generator.generate_campaign(campaign_input)
    try:
        original_filename = '../logs/campaign.json'
        name, extension = os.path.splitext(original_filename)
        campaign_filename = f"{name}_{uuid.uuid4()}{extension}"
        session['campaign.id'] = campaign_filename

        """ save the campaign to a file """
        with open(campaign_filename, 'w') as json_file:
            json.dump(campaign.json, json_file, indent=4)
    except Exception as e:
        logger.exception(e)
    
    return campaign.html

@app.route("/api/edit/campaign", methods=["POST"])
def edit_campaign_api():
    campaign_filename = session['campaign.id']
    input = request.get_json()

    with open(campaign_filename, 'r') as json_file:
        campaign_dict = json.load(json_file)

    element_id = input["elementID"]
    prompt = input["prompt"]
    logger.debug("loaded the campaign from file")
    campaign_text = campaign_generator.edit_campaign_text(prompt, element_id, campaign_dict)
    
    return campaign_text

@app.route('/api/image', methods=['GET'])
def generate_image():
    #image = campaign_generator_utils.file_to_base64_string('my-image.png')
    replicate_client = ReplicateClient()
    image = replicate_client.generate_image_url("a dog in a park");

    html = f"<img src=\"{image}\" class=\"img-fluid\" alt=\"Description of the image\">"
    return html

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('web', path)

@app.errorhandler(404)
def page_not_found(e):
    # Render custom 404.html template
    return render_template('404.html'), 404

@app.errorhandler(Exception)
def internal_server_error(e):
    logger.exception(f"Internal Server Error: {e}")
    return render_template("500.html"), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 8080)))
