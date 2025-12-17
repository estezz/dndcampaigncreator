from google import genai
from google.genai import types
import os
import json
import boto3
from botocore.exceptions import ClientError


class GeminiClient:
    """A client for interacting with the Gemini API."""

    def __init__(self):
        """Initializes the Gemini client with an API key."""
        if not "FLASK_DEBUG" in os.environ:
            self.api_key = self._get_api_key()
            print(f"Using API key: {self.api_key}")

            self.client = genai.Client(api_key=self.api_key)

    def _get_api_key(self):
        secret_name = "GEMINI_API_KEY"
        region_name = "us-east-2"

        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )

        api_key=""
        
        try:
            get_secret_value_response = client.get_secret_value(
                SecretId=secret_name
            )
        except ClientError as e:
            # Handle exceptions as appropriate for your application
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"The requested secret {secret_name} was not found.")
            elif e.response['Error']['Code'] == 'DecryptionFailureException':
                # Secrets Manager can't decrypt the protected secret text using the provided KMS key
                print("Secrets Manager can't decrypt the secret value.")
            elif e.response['Error']['Code'] == 'InternalServiceErrorException':
                # An error occurred on the server side
                print("An internal service error occurred.")
            elif e.response['Error']['Code'] == 'InvalidParameterException':
                print("The request had invalid parameters.")
            elif e.response['Error']['Code'] == 'InvalidRequestException':
                print("The request was invalid, e.g., secret is scheduled for deletion.")
            else:
                print(f"An error occurred: {e.response['Error']['Code']}")
            raise
        else:
            # Decrypts secret using the associated KMS key.
            # Depending on whether the secret was a string or binary, one of these fields will be populated.
            if 'SecretString' in get_secret_value_response:
                secret = get_secret_value_response['SecretString']
                print("Found the secret {secret_name}")
                
                # Secrets are often stored as JSON strings, so you might need to parse them
                json_secret = json.loads(secret)
                api_key = json_secret["GEMINI_API_KEY"]
        
        return api_key
  
    def generate_text(self, prompt, schema, model_name="gemini-2.5-flash"):
        """Generates text using the specified model."""
        
        if "FLASK_DEBUG" in os.environ:
            try:
                # In debug mode, read from a file instead of calling the API
                filename = "test/resources/campain.json"
                with open(filename, 'r') as file:
                    return file.read()
            except FileNotFoundError:
                print(f"Error: The file '{filename}' was not found.")
                return "Mock response not found."

        response = self.client.models.generate_content(
            model=model_name,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": schema
            })
        return response.text
