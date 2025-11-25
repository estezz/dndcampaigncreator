
import pytest
from unittest.mock import patch, MagicMock
from replicate_client import ReplicateClient

class TestReplicateClient:

    def test_initialization(self):
        """Tests that the client initializes with an API token."""
        api_token = "test_token"
        client = ReplicateClient(api_token=api_token)
        assert client.api_token == api_token

    @patch('web.prototype.replicate_client.replicate.run')
    @patch('builtins.open', new_callable=MagicMock)
    @patch('builtins.print')
    def test_generate_image(self, mock_print, mock_open, mock_replicate_run):
        """Tests the generate_image method, mocking the replicate API call and file operations."""
        # Arrange
        # Mock the return value of replicate.run
        mock_output_item = MagicMock()
        mock_output_item.url.return_value = "http://example.com/fake_image.png"
        mock_output_item.read.return_value = b"fake_image_bytes"
        mock_replicate_run.return_value = [mock_output_item]

        api_token = "test_token"
        client = ReplicateClient(api_token=api_token)
        prompt = "a test prompt"
        
        expected_input = {
            "size": "2K",
            "width": 2048,
            "height": 2048,
            "prompt": prompt,
            "max_images": 1,
            "image_input": [],
            "aspect_ratio": "4:3",
            "enhance_prompt": True,
            "sequential_image_generation": "disabled"
        }

        # Act
        client.generate_image(prompt)

        # Assert
        # Check if replicate.run was called correctly
        mock_replicate_run.assert_called_once_with(
            "bytedance/seedream-4",
            input=expected_input
        )

        # Check if the output URL was printed
        mock_print.assert_called_with("http://example.com/fake_image.png")

        # Check if the file was opened for writing in binary mode
        mock_open.assert_called_once_with("my-image.png", "wb")

        # Check if the image data was written to the file
        mock_open().__enter__().write.assert_called_once_with(b"fake_image_bytes")

