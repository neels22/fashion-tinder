import dotenv
from google import genai
from google.genai import types
from PIL import Image
from prompts_dir.prompts import prompts_arr
dotenv.load_dotenv()
client = genai.Client()


response = client.models.generate_content(
    model="gemini-2.5-flash-image", contents="Explain how AI works in a few words"
)
print(response.text)

for part in response.parts:
    if part.text is not None:
        print(part.text)
    elif part.inline_data is not None:
        image = part.as_image()
        image.save("generated_image.png")