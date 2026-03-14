import asyncio
import os
import base64
import logging
import time
from runware import Runware, IImageInference
from image_generation_interface import ImageGenerationInterface


logger = logging.getLogger(__name__)


class RunwareImageClient(ImageGenerationInterface):

    model = "runware:400@4"

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

    async def async_generate_images(self, input_dict):
        # Initialize the SDK
        api_key = os.environ["RUNWARE_API_KEY"]

        runware = Runware(api_key=api_key)
        await runware.connect()

        # 2. Create a list of tasks (coroutines) for each prompt
        tasks = []
        for prompt_dict in input_dict:
            prompt = prompt_dict["prompt"]
            context = prompt_dict["context"]

            final_prompt = f"create a image from this prompt: {prompt} in the dungeons and dragons world with context {context}"

            request = IImageInference(
                positivePrompt=final_prompt[:999],
                model=self.model,
                outputType="URL",  # Returns raw base64 string
                outputFormat="JPG",  # Specify your preferred extension
                numberResults=1,
                width=1024,
                height=1024,
            )
            tasks.append(runware.imageInference(requestImage=request))

        print("Generating...")
        results = await asyncio.gather(*tasks)

        # 4. Process the results
        image_dict = {}
        for index, result in enumerate(results):
            image_dict[input_dict[index]['prompt']] = result[0].imageURL

        # 5. Close the connection
        await runware.disconnect()
        return image_dict
