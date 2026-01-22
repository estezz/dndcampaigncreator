"""This module provides a client for interacting with the Replicate API."""

import os
import random
import json
import logging
import asyncio
import boto3
import replicate
from botocore.exceptions import ClientError
from image_generation_interface import ImageGenerationInterface



logger = logging.getLogger(__name__)


class ReplicateImageClient(ImageGenerationInterface):
    """This class interacts with the Replicate API"""

    def __init__(self):
        logger.debug("Initializing replicate client")
        api_token = self.get_replicate_api_key()
        self.client = replicate.Client(api_token=api_token)

        self.api_token = api_token

    def get_replicate_api_key(self):
        """This method look for the Replicate API Key as a environment variable
        then as a secret in AWS Secrets Manager"""
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
                    logger.debug("An errImageor occurred: %s", e.response["Error"]["Code"])
                raise

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
        """This method generates text for a prompt using the replicate API"""

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
        """This method generates images using the replicate API"""

        logger.debug("starting async_generate_images")

        image_dict = {}
        try:
            image_dict = asyncio.run(self.async_generate_images(prompts))
        except* ValueError as eg:
            # Handle specifically ValueError within the group
            logger.exception(eg)
            raise

        logger.debug("finished async_generate_images")
        logger.debug(image_dict)
        return image_dict

    async def async_generate_images(self, prompts):
        """This method generates images asycronously using the replicate API"""

        model_version = "bytedance/seedream-4"
        image_dict = {}

        #create images in parallel
        async with asyncio.TaskGroup() as tg:
            tasks = [
                tg.create_task(
                    self.client.async_run(model_version, input={"prompt": prompt})
                )
                for prompt in prompts
            ]

        results = await asyncio.gather(*tasks)
        for index, result in enumerate(results):
            image_dict[prompts[index]] = result[0].url
        return image_dict
