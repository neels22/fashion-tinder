from fastapi import FastAPI, Query, HTTPException, status, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .scripts.image_generation import create_multiple_images, create_single_image
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mount the generated_images directory as static files
app.mount("/images", StaticFiles(directory="generated_images"), name="images")


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/multiple_images")
async def generate_multiple_images():
    return create_multiple_images()

@app.get("/single_image")
async def generate_single_image():
    result = create_single_image()
    # Convert the file path to a URL path
    if result.get("image_path"):
        filename = result["image_path"].replace("\\", "/").split("/")[-1]
        result["image_url"] = f"/images/{filename}"
    return result