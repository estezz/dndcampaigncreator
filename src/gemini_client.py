
from google import genai
import os
import boto3, json
from botocore.exceptions import ClientError

class GeminiClient:
    def __init__(self):
        """Initializes the GeminiClient with API credentials."""
        os.environ["GEMINI_API_KEY"] = self.get_gemini_api_key()

    def get_gemini_api_key(self):

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
            print(get_secret_value_response)
            # Decrypts secret using the associated KMS key.
            # Depending on whether the secret was a string or binary, one of these fields will be populated.
            if 'SecretString' in get_secret_value_response:
                secret = get_secret_value_response['SecretString']
                print(secret)
                # Secrets are often stored as JSON strings, so you might need to parse them
                json = json.loads(secret)
                api_key = secret["GEMINI_API_KEY"]
        
        print(api_key)
        return api_key

        
    def generate_text(self, prompt, schema, model_name="gemini-2.0-flash-lite"):
        """Generates text using the specified model."""

        # model = genai.GenerativeModel(str(model_name))
        # response = model.generate_content(prompt)
        client = genai.Client()

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": schema
            })
        return response.text

    def generate_html(self, prompt, model_name="gemini-2.0-flash-lite"):
        """Generates HTML using the specified model."""
        client = genai.Client()

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text
    
    def generate_image(self, prompt, model_name="imagen-3.0-generate-002"):
        """Generates an image based on the prompt."""
        print(prompt)
        prompt = "create an image from this text : " + prompt
        
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)

        # Process the response to extract and save the generated image
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                # Assuming the generated content is an image in inline_data
                image_data = part.inline_data.data
                image = Image.open(BytesIO(image_data))
                image.save("generated_futuristic_city.png")
                print("Image saved as generated_futuristic_city.png")
                return image
            elif part.text is not None:
                print("Text part of response:", part.text)
        return None