"""This module is for generating images"""

from abc import ABC, abstractmethod

class TextGenerationInterface(ABC): #pylint: disable=too-few-public-methods
    """This is an interface to generate text"""

    @abstractmethod
    def generate_text(self, prompt):
        """This method generates text for a prompt"""