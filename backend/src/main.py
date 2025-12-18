from fastapi import FastAPI, Query, HTTPException, status, Body
from fastapi.middleware.cors import CORSMiddleware
from .scripts.image_generation import create_multiple_images, create_single_image
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/multiple_images")
async def generate_multiple_images():
    return create_multiple_images()

@app.get("/single_image")
async def generate_single_image():
    return create_single_image()