import pytest
import json
import html
from pathlib import Path


from jinja2 import Environment, FileSystemLoader, select_autoescape

class TestCampaignTemplates:

    @pytest.fixture
    def env(self):
        # Configure Jinja2 environment to load templates from a specific directory
        # For a real project, this path would point to your actual templates directory
        base_path = Path(__file__).parent
        print(f"test location {base_path}")

        # Join the base path with the filename
        templates_path = (base_path / ".." / ".." / "src" / "templates" ).resolve()
        return Environment(
            loader=FileSystemLoader(templates_path),  # Assuming templates are in src/templates
            autoescape=select_autoescape(["html", "js"])
        )

    def test_campaign_template_renders_correctly(self, env):
        template = env.get_template("main_campaign_template.html") # Assuming you have a template named campaign_overview.html
        base_path = Path(__file__).parent
        print(f"test location {base_path}")

        # Join the base path with the filename
        file_path = (base_path / ".." / "resources" / "campaign.json").resolve()
        with open(file_path) as f:
            context = json.load(f)

        rendered_content = template.render(context)

        assert "A Whispered Warning" in rendered_content
        assert "The Iron Crown" in rendered_content
        assert "middle-aged human male" in rendered_content
        assert "Reputation and Renown" in rendered_content

    def test_another_template_renders_correctly(self, env):
        # Example for another template if you have one, e.g., 'character_sheet.html'
        # template = env.get_template("character_sheet.html")
        # context = {"character_name": "Gandalf", "class_name": "Wizard"}
        # rendered_content = template.render(context)
        # assert "Gandalf" in rendered_content
        pass # Placeholder for actual tests
