
import unittest
import os
from unittest.mock import patch, MagicMock
from gemini_client import GeminiClient

class TestGeminiClient(unittest.TestCase):

   
    def test_generate_text(self):
        """Test the generate_text method."""
        client = GeminiClient()
        result = client.generate_text("Generate a DnD story");
        self.assertIsNotNone(result)


    def test_generate_image(self):
        """Test the generate_image method."""
        client = GeminiClient()
        prompt = "a dog on a skateboard"
        result = client.generate_image(prompt)
        self.assertIsNotNone(result)
        print(result)


if __name__ == '__main__':
    unittest.main()
