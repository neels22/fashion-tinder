from fastapi import FastAPI, Query, HTTPException, status, Body, File, UploadFile, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from typing import Annotated
from sqlmodel import select

from .scripts.image_generation import create_multiple_images, create_single_image, set_input_image_path
import uuid
from .models.user import USER, UserCreate, UserResponse, Token
from .scripts.init_db import create_user, read_users
from .auth.authentication import (
    get_password_hash, 
    verify_password, 
    create_access_token,
    get_current_user
)
from .db.database import get_db_session
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
async def generate_multiple_images(current_user: Annotated[USER, Depends(get_current_user)]):
    results = create_multiple_images()
    for result in results:
        if result.get("image_path"):
            filename = result["image_path"].replace("\\", "/").split("/")[-1]
            result["image_url"] = f"/images/{filename}"
    return results

@app.get("/single_image")
async def generate_single_image(current_user: Annotated[USER, Depends(get_current_user)]):
    result = create_single_image()
    # Convert the file path to a URL path
    if result.get("image_path"):
        filename = result["image_path"].replace("\\", "/").split("/")[-1]
        result["image_url"] = f"/images/{filename}"
    return result

@app.post("/upload_image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: Annotated[USER, Depends(get_current_user)]
):
    # 1. Validate content type (simple check)
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    # 2. Generate a safe unique filename
    ext = Path(file.filename).suffix  # keeps .png / .jpg / etc.
    new_filename = f"{uuid.uuid4().hex}{ext}"
    save_path = UPLOAD_DIR / new_filename #Using / on Path objects joins paths.

    set_input_image_path(new_filename)
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



@app.post("/create_user")
async def create_user_api(user: USER):
    return create_user(user)

@app.get("/read_users")
async def read_users_api():
    return read_users()


# Authentication endpoints
@app.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, session = Depends(get_db_session)):
    # Check if email exists
    existing = session.exec(select(USER).where(USER.email == user.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user with hashed password
    new_user = USER(
        name=user.name,
        email=user.email,
        password=get_password_hash(user.password)
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


@app.post("/login", response_model=Token)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session = Depends(get_db_session)):
    user = session.exec(select(USER).where(USER.email == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=UserResponse)
def read_current_user(current_user: Annotated[USER, Depends(get_current_user)]):
    return current_user