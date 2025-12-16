import google.generativeai as genai
import os
import json

class GeminiClient:
    """A client for interacting with the Gemini API."""

    def __init__(self):
        """Initializes the Gemini client with an API key."""
        self.api_key = self._get_api_key()
        genai.configure(api_key=self.api_key)

    def _get_api_key(self):
        api_key=""
        """
        Retrieves the Gemini API key from environment variables or a JSON file.

        This function first checks for the "GEMINI_API_KEY" environment variable.
        If not found, it looks for a "secrets.json" file in the parent directory,
        expecting a "GEMINI_API_KEY" key within the JSON.

        Returns:
            The Gemini API key.

        Raises:
            SystemExit: If the API key is not found in either the environment
                        variables or the "secrets.json" file.
        """
        if "GEMINI_API_KEY" in os.environ:
            return os.environ["GEMINI_API_KEY"]
        else:
            # Look for secrets.json in the parent directory
            # This is not a robust way to handle secrets in a production application
            # but is used for this sample.
            # See https://cloud.google.com/secret-manager/docs/best-practices
            # for more information on how to handle secrets.
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            secrets_path = os.path.join(parent_dir, "secrets.json")

            if os.path.exists(secrets_path):
                with open(secrets_path) as f:
                    secrets = json.load(f)
                    if "GEMINI_API_KEY" in secrets:
                        return secrets["GEMINI_API_KEY"]

            # For secrets stored in Google Cloud Secret Manager
            if "GEMINI_API_KEY_SECRET" in os.environ:
                secret_id = os.environ["GEMINI_API_KEY_SECRET"]
                
                # Import the Secret Manager client library.
                from google.cloud import secretmanager

                # Create the Secret Manager client.
                client = secretmanager.SecretManagerServiceClient()

                # Build the resource name of the secret version.
                name = f"{secret_id}/versions/latest"

                # Access the secret version.
                response = client.access_secret_version(request={"name": name})
                
                # Get the secret payload.
                secret = response.payload.data.decode("UTF-8")
                
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

        # model = genai.GenerativeModel(str(model_name))
        # response = model.generate_content(prompt)
        client = genai.Client()

        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": schema
            })
        return response.text
