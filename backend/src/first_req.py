

import dotenv
from google import genai
from google.genai import types
dotenv.load_dotenv()

from PIL import Image

client = genai.Client()


image = Image.open("male-mannequin.jpg")
# aspect_ratio = "5:4"
resolution = "2k"
prompt = input("Enter a prompt: ")

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=[prompt, image],
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
        image_config=types.ImageConfig(
            # aspect_ratio=aspect_ratio,
            image_size=resolution
        ),
    )
)


for part in response.parts:
    if part.text is not None:
        print(part.text)
    elif part.inline_data is not None:
        image = part.as_image()
        image.save("generated_image.png")