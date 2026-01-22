"""This module is a local version of the ReplicateClientInterface"""

from image_generation_interface import ImageGenerationInterface


class MockImageClient(ImageGenerationInterface):
    """ This is a mock of the ReplicateClientInterface that returns static data for testing"""
    
    def generate_images(self, prompts):
        """ This method returns static image data for testing"""

        image_dict = {}
        for prompt in prompts:
            image_dict[prompt] = "https://picsum.photos/200/300"

        return image_dict
    
        
 