"""This module contains an interface for generating images"""

from abc import ABC, abstractmethod


class ImageGenerationInterface(ABC): #pylint: disable=too-few-public-methods
    """This is an interface to interact with the Replicate API"""

    @abstractmethod
    def generate_images(self, prompts):
        """This method generates images and returns a dictionary of prompt to image url"""
        

   
