import replicate
import os, boto3, json
from botocore.exceptions import ClientError
from replicate.exceptions import ReplicateError
import random
import asyncio
import logging
logger = logging.getLogger(__name__)

class ReplicateClient:
    def __init__(self):
        logger.debug("Initializing replicate client")
        if not "FLASK_DEBUG" in os.environ:
            api_token = self.get_replicate_api_key()
            self.client = replicate.Client(api_token=api_token)

            self.api_token = api_token

    def get_replicate_api_key(self):

        secret_name = "REPLICATE_API_KEY"
        region_name = "us-east-2"

        # Create a Secrets Manager client
        session = boto3.session.Session()
        aws_client = session.client(
            service_name="secretsmanager", region_name=region_name
        )

        api_key = ""
        if secret_name in os.environ:
            api_key = os.environ[secret_name]
        else:
            try:
                get_secret_value_response = aws_client.get_secret_value(
                    SecretId=secret_name
                )
            except ClientError as e:
                # Handle exceptions as appropriate for your application
                if e.response["Error"]["Code"] == "ResourceNotFoundException":
                    logger.debug(f"The requested secret {secret_name} was not found.")
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
                    logger.debug(f"An error occurred: {e.response['Error']['Code']}")
                raise
            else:
                # Decrypts secret using the associated KMS key.
                # Depending on whether the secret was a string or binary, one of these fields will be populated.
                if "SecretString" in get_secret_value_response:
                    secret = get_secret_value_response["SecretString"]
                    logger.debug("Found the secret {secret_name}")

                    # Secrets are often stored as JSON strings, so you might need to parse them
                    json_secret = json.loads(secret)
                    api_key = json_secret["REPLICATE_API_KEY"]

        return api_key

    def generate_text(self, prompt):
        output = replicate.run(
            "openai/gpt-5",
            input={
                "prompt": "Are you AGI?",
                "messages": [],
                "verbosity": "medium",
                "image_input": [],
                "reasoning_effort": "minimal",
            },
        )

        return output

    def generate_images(self, prompts):
        logger.debug("starting async_generate_images")

        """ for testing without paying for replicate """
        if "FLASK_DEBUG" in os.environ:
            image_dict = {}
            for prompt in prompts:
                image_dict[prompt] = "https://picsum.photos/200/300"
            return image_dict
        image_dict = asyncio.run(self.async_generate_images(prompts))
        logger.debug("finished async_generate_images")
        logger.debug(results)
        return image_dict    
            

    async def async_generate_images(self, prompts):
        model_version = "bytedance/seedream-4"
        image_dict = {}

        """ create images in parallel """
        async with asyncio.TaskGroup() as tg:
            tasks = [
                tg.create_task(
                    self.client.async_run(model_version, input={"prompt": prompt})
                )
                for prompt in prompts
            ]

        results = await asyncio.gather(*tasks)
        for index, result in enumerate(results) :
                image_dict[prompts[index]] = result[0].url
        return image_dict

    def generate_image_url(self, prompt):
        if "FLASK_DEBUG" in os.environ:
            return "https://picsum.photos/200/300"
        try:
            output = self.client.run(
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
                    "sequential_image_generation": "disabled",
                },
            )
        except ReplicateError as e:
            logger.debug(e)
            logger.debug(f"prompt: {prompt} ")

        # To access the file URL:
        logger.debug(output[0].url)
        # => "http://example.com"

        return output[0].url


def main():
    token = os.environ["REPLICATE_API_TOKEN"]
    client = ReplicateClient(token)
    client.generate_image_url(
        "A top-down battle map of a subterranean grotto, with a large, dark pool of water in the center. A crude stone altar covered in black mud sits on a raised dais, glowing with a faint, purple light from a dark crystal. Tattered cages holding prisoners line one wall, and multiple dripping tunnels lead into the chamber."
    )


if __name__ == "__main__":
    main()
