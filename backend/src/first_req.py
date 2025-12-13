

import dotenv
from google import genai
dotenv.load_dotenv()

from PIL import Image

client = genai.Client()


image = Image.open("first.png")
prompt = "Create a picture where the table cloth is black in the image"

response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=[prompt, image]
)


for part in response.parts:
    if part.text is not None:
        print(part.text)
    elif part.inline_data is not None:
        image = part.as_image()
        image.save("generated_image.png")