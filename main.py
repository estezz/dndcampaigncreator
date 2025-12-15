from src.campaign_generator import Campaign_Generator
import src.campaign_generator as campaign_generator_utils
from src.replicate_client import ReplicateClient
from flask import Flask, jsonify, request, send_file, send_from_directory
import os

app = Flask(__name__)
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
    campaign_dict = request.get_json()
    print(campaign_dict)
    campaign = campaign_generator.generate_campaign(campaign_dict)
   
    return campaign.html

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 80)))
