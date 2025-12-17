from fastapi import FastAPI
from image_generation import create_multiple_images, create_single_image
app = FastAPI()


@app.get("/multiple_images")
async def generate_multiple_images():
    return create_multiple_images()

@app.get("/single_image")
async def generate_single_image():
    return create_single_image()