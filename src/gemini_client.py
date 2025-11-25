
import google.generativeai as genai
import os

class GeminiClient:
    def __init__(self):
        try:
            api_key = os.environ['GEMINI_API_KEY']
            self.api_key = api_key
            genai.configure(api_key=self.api_key)

        except KeyError:
            print("GEMINI_API_KEY environment variable not set.")
            raise("GEMINI_API_KEY environment variable not set.")

        
    def generate_text(self, prompt, model_name="gemini-2.0-flash-lite"):
        """Generates text using the specified model."""

        model = genai.GenerativeModel(str(model_name))
        response = model.generate_content(prompt)
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