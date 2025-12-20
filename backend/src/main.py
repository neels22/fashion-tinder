from fastapi import FastAPI, Query, HTTPException, status, Body, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .scripts.image_generation import create_multiple_images, create_single_image
import uuid
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("input_images")
UPLOAD_DIR.mkdir(exist_ok=True)

# Mount the generated_images directory as static files
app.mount("/images", StaticFiles(directory="generated_images"), name="images")
app.mount("/input_images", StaticFiles(directory=str(UPLOAD_DIR)), name="input_images")


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

@app.post("/upload_image")
async def upload_image(file: UploadFile = File(...)):
    # 1. Validate content type (simple check)
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    # 2. Generate a safe unique filename
    ext = Path(file.filename).suffix  # keeps .png / .jpg / etc.
    new_filename = f"{uuid.uuid4().hex}{ext}"
    save_path = UPLOAD_DIR / new_filename #Using / on Path objects joins paths.

    # 3. Save to disk (reads the whole file into memory; fine for small images)
    try:
        file_bytes = await file.read()
        save_path.write_bytes(file_bytes)
    finally:
        await file.close()

    # 4. Return info (including public URL)
    return {
        "filename": new_filename,
        "url": f"/input_images/{new_filename}", #Using / on strings joins them.
        "content_type": file.content_type,
        "size_bytes": len(file_bytes),
    }   


# todo figure out a way to provide the uploaded image to the image generation script 
"""
to pick up the image uplaoded by user -- we need to identify which image did the user upload
- right now there no way to identify which image did the user upload
- so which ever is the latest image uploaded by the user will be used for the image generation
- so when user uploads a new image maybe we can update the input_image path with the name of this new image
- so when user clicks on generate image button we can use the updated input_image path for the image generation
- this is good for now for a single user use case 
- but for a multi user use case we need to identify which image did the user upload
"""