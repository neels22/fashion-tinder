import os
from typing import List, Dict

import dotenv
from google import genai
from google.genai import types
from google.genai.errors import ClientError
from PIL import Image
from pillow_heif import register_heif_opener
from ..prompts_dir.prompts import prompts_arr

# Register HEIF opener so PIL can read HEIC files
register_heif_opener()

dotenv.load_dotenv()
client = genai.Client()

# INPUT_IMAGE_PATH = "input_images/male-mannequin.jpg"
OUTPUT_DIR = "generated_images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

INPUT_IMAGE_PATH = None
def load_base_image() -> Image.Image:
    if INPUT_IMAGE_PATH is None:
        raise ValueError("Input image path is not set")
    return Image.open(INPUT_IMAGE_PATH)

def set_input_image_path(filename: str) -> None:
    global INPUT_IMAGE_PATH
    INPUT_IMAGE_PATH = f"input_images/{filename}"

def create_multiple_images() -> List[Dict]:
    base_image = load_base_image()
    results: List[Dict] = []

    for idx, prompt in enumerate(prompts_arr, start=1):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=[prompt, base_image],
            )
        except ClientError as e:
            # You can log this; return partial success upstream
            results.append({"prompt": prompt, "error": str(e)})
            continue

        image_path = None
        text_parts: List[str] = []

        for part in response.parts:
            if part.text is not None:
                text_parts.append(part.text)
            elif part.inline_data is not None:
                generated_image = part.as_image()
                image_path = f"{OUTPUT_DIR}/generated_image_{idx}.png"
                generated_image.save(image_path)

        results.append(
            {
                "prompt": prompt,
                "texts": text_parts,
                "image_path": image_path,
            }
        )

    return results


prompts_for_single_image = prompts_arr[1]   
def create_single_image(prompt: str = prompts_for_single_image) -> Dict:
    base_image = load_base_image()

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[prompt, base_image],
        )
    except ClientError as e:
        return {"prompt": prompt, "error": str(e)}

    image_path = None
    text_parts: List[str] = []

    for part in response.parts:
        if part.text is not None:
            text_parts.append(part.text)
        elif part.inline_data is not None:
            generated_image = part.as_image()
            image_path = f"{OUTPUT_DIR}/generated_image.png"
            generated_image.save(image_path)

    return {
        "prompt": prompt,
        "texts": text_parts,
        "image_path": image_path,
    }


if __name__ == "__main__":
    print(create_multiple_images())
    print(create_single_image(prompts_for_single_image))