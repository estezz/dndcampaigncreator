
import os
import google.genai as genai
from PIL import Image
from io import BytesIO

# --- Configuration ---
# It is strongly recommended to set your API key as an environment variable
# for security reasons. For example, in your terminal:
# export GOOGLE_API_KEY="YOUR_API_KEY"
#
# If the environment variable isn't set, the script will fall back to the
# hardcoded key below.
# IMPORTANT: Avoid committing API keys directly into version control.
API_KEY = os.environ.get("GEMINI_API_KEY")

# The Imagen model to use for image generation.
IMAGEN_MODEL = "gemini-2.5-flash-image"

# The prompt for the image you want to generate.
PROMPT = "A photorealistic close-up portrait of an elderly Japanese ceramicist with deep, sun-etched wrinkles and a warm, knowing smile. He is carefully inspecting a freshly glazed tea bowl. The setting is his rustic, sun-drenched workshop with pottery wheels and shelves of clay pots in the background. The scene is illuminated by soft, golden hour light streaming through a window, highlighting the fine texture of the clay and the fabric of his apron. Captured with an 85mm portrait lens, resulting in a soft, blurred background (bokeh). The overall mood is serene and masterful."

# The output filename for the generated image.
OUTPUT_FILENAME = "generated_ceramicist_portrait.png"

def generate_image_with_imagen():
    """
    Generates an image using the Imagen model from a text prompt and saves it.
    """
    try:

        client = genai.Client(api_key=API_KEY)

        print("List of models that support generateContent:\n")
        for m in client.models.list():
            for action in m.supported_actions:
                if action == "generateContent":
                    print(m.name)

        print("List of models that support embedContent:\n")
        for m in client.models.list():
            for action in m.supported_actions:
                if action == "embedContent":
                    print(m.name)
        print(f"Initializing Gemini client...")
        print(f"Generating image with the '{IMAGEN_MODEL}' model...")
        print(f"Prompt: {PROMPT[:80]}...")

        # Generate the image content
        response = client.models.generate_content(
            model=IMAGEN_MODEL,
            contents=PROMPT
        )

        print("Processing response...")

        # Extract the raw image data from the response
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            image_parts = [
                part.inline_data.data
                for part in response.candidates[0].content.parts
                if part.inline_data
            ]

            if image_parts:
                # We have image data, save the first image found
                image_data = image_parts[0]

                # Create a PIL Image object from the raw data
                image = Image.open(BytesIO(image_data))

                # Save the image to a file
                image.save(OUTPUT_FILENAME)
                print(f"\nImage successfully generated and saved to '{OUTPUT_FILENAME}'")

                # Optionally, if in a graphical environment, you can display the image
                # image.show()
                return

        # If we get here, no image data was found in the response.
        print("\nImage generation failed. No image data found in the response.")
        print("Full response:", response)

    except Exception as e:
        print(f"\nAn error occurred during image generation: {e}")
        print("\nPlease check the following:")
        print("1. Your API key is correct and has the necessary permissions.")
        print(f"2. The '{IMAGEN_MODEL}' model is available and enabled for your project.")
        print("3. Your prompt is valid and does not violate safety policies.")

if __name__ == "__main__":
    generate_image_with_imagen()
