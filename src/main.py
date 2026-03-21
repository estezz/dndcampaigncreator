"""This is the main entry point for this flaskk application"""

import os
import json
import uuid
import logging
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
from flask import (
    Flask,
    jsonify,
    request,
    send_file,
    send_from_directory,
    render_template,
    session,
)
from campaign_generator import CampaignGenerator

load_dotenv()
log_dir = "./logs"

logging.basicConfig(filename=f"{log_dir}/dnd.log", level=logging.DEBUG)
logger = logging.getLogger(__name__)


from flask import Flask


def clean_log_dir():
    dir_path = Path(log_dir)
    prefix = "campaign_"

    files_to_delete = []
    for item in dir_path.iterdir():
        # Check if it's a file and if its name starts with the prefix
        if item.is_file() and item.name.startswith(prefix):
            files_to_delete.append(item)

    # --- Deletion ---
    for file_path in files_to_delete:
        try:
            file_path.unlink()
            logger.debug(f"Deleted: {file_path}")
        except OSError as e:
            logger.error(f"Error deleting {file_path}: {e}")


def create_app():
    clean_log_dir()

    app = Flask(__name__, template_folder="templates")
    app.secret_key = os.urandom(24)
    app.permanent_session_lifetime = timedelta(
        minutes=5
    )  # Set session timeout to 5 minutes

    with app.app_context():
        # Code to run at startup goes here
        print("Function running at application startup within the app context.")
        # Example: initialize database
        # init_db()

    return app


app = create_app()


@app.route("/")
def index():
    """entry point for base url"""
    return send_file("web/index.html")


@app.route("/api/generate/campaign", methods=["POST"])
def generate_campaign_api():
    """
    This api method generates a campaign from the initial user input.
    This is the main method that is called from the frontend.
    It creates a dictionary of the state of the campaign.

    It then creates HTML from the campaign state that is returned to the frontend.
    """

    campaign_generator = CampaignGenerator()
    campaign_input = request.get_json()
    logger.debug(campaign_input)
    if campaign_input is None or campaign_input == {}:
        return jsonify({"error": "Invalid request"}), 400

    campaign = campaign_generator.generate_campaign(campaign_input)

    original_filename = f"{log_dir}/campaign.json"
    name, extension = os.path.splitext(original_filename)
    campaign_filename = f"{name}_{uuid.uuid4()}{extension}"
    session["campaign.id"] = campaign_filename

    # save the campaign to a file
    with open(file=campaign_filename, encoding="utf-8", mode="w") as json_file:
        json.dump(campaign.json, json_file, indent=4)

    return campaign.html


@app.route("/api/edit/campaign", methods=["POST"])
def edit_campaign_api():
    """this edits the campaign from the user input"""

    campaign_generator = CampaignGenerator()
    campaign_filename = session["campaign.id"]
    input_json = request.get_json()

    with open(file=campaign_filename, encoding="utf-8", mode="r") as json_file:
        campaign_dict = json.load(json_file)

    element_id = input_json["elementID"]
    prompt = input_json["prompt"]
    logger.debug("loaded the campaign from file")
    campaign_text = campaign_generator.edit_campaign_text(
        prompt, element_id, campaign_dict
    )

    return campaign_text


@app.route("/<path:path>")
def serve_static(path):
    """this serves the static files"""

    return send_from_directory("web", path)


@app.errorhandler(404)
def page_not_found(e):
    """this is for the 404 error page"""

    logger.exception("Page Not Found: %s", e)
    # Render custom 404.html template
    return render_template("404.html"), 404


@app.errorhandler(Exception)
def internal_server_error(e):
    """this is for the 500 error page"""

    logger.exception("Internal Server Error: %s", e)
    return render_template("500.html"), 500


