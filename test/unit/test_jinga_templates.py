"""This module test the Jinja2 templates"""

import json
import logging
from pathlib import Path
import pytest
from jinja2 import Environment, FileSystemLoader, select_autoescape

base_path = Path(__file__).parent
log_file = base_path / "test.log"
logging.basicConfig(filename=log_file, level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestCampaignTemplates:
    """This class test the Campaign Jinja2 templates"""

    @pytest.fixture
    def env(self):
        # Configure Jinja2 environment to load templates from a specific directory
        # For a real project, this path would point to your actual templates directory
        base_path = Path(__file__).parent
        print(f"test location {base_path}")

        # Join the base path with the filename
        templates_path = (base_path / ".." / ".." / "src" / "templates").resolve()
        return Environment(
            loader=FileSystemLoader(
                templates_path
            ),  # Assuming templates are in src/templates
            autoescape=select_autoescape(["html", "js"]),
        )

    def test_campaign_template_renders_correctly(self, env):
        """This test that the complete campaign template renders correctly"""

        template = env.get_template("main_campaign_template.html")

        # Join the base path with the filename
        file_path = (base_path / ".." / "resources" / "campaign.json").resolve()
        with open(file_path) as f:
            context = json.load(f)

        rendered_content = template.render(context)
        logger.info(rendered_content)

        assert "You have a limited well of stamina" in rendered_content
        assert "always polite and respectful." in rendered_content
        assert "A nervous young woman " in rendered_content
        assert "A former city guard looking for adventure" in rendered_content

    def test_player_character_template(self, env):
        """test the player_character_sheets.html"""
        template = env.get_template("player_character_sheets.html")

        # Join the base path with the filename
        json_file_path = (base_path / ".." / "resources" / "character_wizard.json").resolve()
        with open(json_file_path, mode="r", encoding="utf-8") as f:
            context = json.load(f)

        rendered_content = template.render(context)

        output_file_path = (base_path / "player.html")
        with open(file=output_file_path, mode='w', encoding='utf-8') as pl:
            pl.write(rendered_content)
