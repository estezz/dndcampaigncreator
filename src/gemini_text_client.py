"""This module provides a client for interacting with the Gemini API."""

import json
import logging
import os
from google import genai
import boto3
from botocore.exceptions import ClientError
from text_generation_interface import TextGenerationInterface


logger = logging.getLogger(__name__)


class GeminiTextClient(TextGenerationInterface): #pylint: disable=too-few-public-methods
    """A client for interacting with the Gemini API."""

    def __init__(self):
        """Initializes the Gemini client with an API key."""
        self.api_key = self._get_api_key()

        self.client = genai.Client(api_key=self.api_key)

    def _get_api_key(self):
        secret_name = "GEMINI_API_KEY"
        region_name = "us-east-2"

        if secret_name in os.environ:
            return os.environ[secret_name]

        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(service_name="secretsmanager", region_name=region_name)

        api_key = ""

        try:
            get_secret_value_response = client.get_secret_value(SecretId=secret_name)
            # Decrypts secret using the associated KMS key.
            # Depending on whether the secret was a string or binary,
            # one of these fields will be populated.
            if "SecretString" in get_secret_value_response:
                secret = get_secret_value_response["SecretString"]
                logger.debug("Found the secret {secret_name}")

                # Secrets are often stored as JSON strings, so you might need to parse them
                json_secret = json.loads(secret)
                api_key = json_secret["GEMINI_API_KEY"]

            return api_key
        except ClientError as e:
            # Handle exceptions as appropriate for your application
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                logger.debug("The requested secret %s was not found.", secret_name)
            elif e.response["Error"]["Code"] == "DecryptionFailureException":
                # Secrets Manager can't decrypt the protected secret text using the provided KMS key
                logger.debug("Secrets Manager can't decrypt the secret value.")
            elif e.response["Error"]["Code"] == "InternalServiceErrorException":
                # An error occurred on the server side
                logger.debug("An internal service error occurred.")
            elif e.response["Error"]["Code"] == "InvalidParameterException":
                logger.debug("The request had invalid parameters.")
            elif e.response["Error"]["Code"] == "InvalidRequestException":
                logger.debug(
                    "The request was invalid, e.g., secret is scheduled for deletion."
                )
            else:
                logger.debug("An error occurred: %s", e.response['Error']['Code'])
            raise
            

    def generate_text(self, prompt, schema, model_name="gemini-2.5-flash"):
        """Generates text using the specified model."""

        response = self.client.models.generate_content(
            model=model_name,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": schema,
            },
        )
        return response.text
