"""This module mocks a text_image_interface"""

from text_generation_interface import TextGenerationInterface
from pathlib import Path

class MockTextClient(TextGenerationInterface):
    """This class mocks a text generation interface"""
    
    def generate_text(self, prompt, schema):
        """This method returns static JSON data for testing"""
        
        base_path = Path(__file__).parent
        campaign_static_file = (base_path / "../test/resources/campaign.json").resolve()
        with open(file=campaign_static_file, mode="r", encoding="utf-8") as f:
             return f.read()
