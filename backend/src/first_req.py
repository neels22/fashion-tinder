

import dotenv
from google import genai
from google.genai import types
from PIL import Image
from prompts_dir.prompts import prompts_arr
dotenv.load_dotenv()
client = genai.Client()


base_image = Image.open("input_images/male-mannequin.jpg")
# aspect_ratio = "5:4"
resolution = "2k"


id =0
for prompt in prompts_arr:
    id += 1
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[prompt, base_image],
        # config=types.GenerateContentConfig(
        #     response_modalities=['TEXT', 'IMAGE'],
        #     image_config=types.ImageConfig(
        #         # aspect_ratio=aspect_ratio,
        #         image_size=resolution
        #     ),
        # )
    )

    for part in response.parts:
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            generated_image = part.as_image()
            generated_image.save(f"generated_images/generated_image_{id}.png")

# response = client.models.generate_content(
#         model="gemini-3-pro-image-preview",
#         contents=[prompts_arr[0], base_image],
#         # config=types.GenerateContentConfig(
#         #     response_modalities=['TEXT', 'IMAGE'],
#         #     image_config=types.ImageConfig(
#         #         image_size=resolution
#         #     ),
#         # )
#     )

# for part in response.parts:
#     if part.text is not None:
#         print(part.text)
#     elif part.inline_data is not None:
#         generated_image = part.as_image()
#         generated_image.save(f"generated_image.png")


