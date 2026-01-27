
import json
from jinja2 import Environment, FileSystemLoader

# Set up the Jinja2 environment
env = Environment(loader=FileSystemLoader('src/templates'))
template = env.get_template('player_character_sheets.html')

# Load the character data from the JSON file
with open('test/resources/character_wizard.json', 'r') as f:
    character_data = json.load(f)

# Render the template with the character data
rendered_html = template.render(character_data)

# Write the rendered HTML to a new file
with open('character_sheet.html', 'w') as f:
    f.write(rendered_html)

print("Successfully created character_sheet.html")
