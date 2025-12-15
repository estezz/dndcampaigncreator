import replicate
import os, boto3, json

class ReplicateClient:
    def __init__(self):
        api_token = self.get_gemini_api_key()
        replicate.Client(api_token=api_token)

        self.api_token = api_token
    def get_gemini_api_key(self):

        secret_name = "REPLICATE_API_KEY"
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
                api_key = json_secret["REPLICATE_API_KEY"]
        
        return api_key

    def generate_image(self, prompt):
        
        output = replicate.run(
            "bytedance/seedream-4",
            input={
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
        )

        # To access the file URL:
        print(output[0].url)
        #=> "http://example.com"

        # To write the file to disk:
        with open("my-image.png", "wb") as file:
            file.write(output[0].read())



def main():
    token = os.environ["REPLICATE_API_TOKEN"] 
    client = ReplicateClient(token)
    client.generate_image("A top-down battle map of a subterranean grotto, with a large, dark pool of water in the center. A crude stone altar covered in black mud sits on a raised dais, glowing with a faint, purple light from a dark crystal. Tattered cages holding prisoners line one wall, and multiple dripping tunnels lead into the chamber.");

if __name__ == "__main__":
    main()
