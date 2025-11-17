import replicate
import os

class ReplicateClient:
    def __init__(self, api_token):
        self.api_token = api_token

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
