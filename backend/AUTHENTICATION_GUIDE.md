# JWT Authentication Setup Guide for Fashion Tinder Backend

**Date:** January 4, 2026  
**Author:** Based on implementation with Indraneel Sarode  
**Technology Stack:** FastAPI, SQLModel, JWT, Bcrypt, Neon Postgres

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Step-by-Step Implementation](#step-by-step-implementation)
4. [Code Walkthrough](#code-walkthrough)
5. [Errors Encountered & Solutions](#errors-encountered--solutions)
6. [Testing the Implementation](#testing-the-implementation)
7. [Security Considerations](#security-considerations)

---

## Overview

This guide documents the complete implementation of JWT (JSON Web Token) authentication in the Fashion Tinder backend application. The authentication system provides:

- **User Registration** with password hashing
- **User Login** with JWT token generation
- **Protected Routes** requiring authentication
- **OAuth2 Integration** with FastAPI's Swagger UI

### Key Features

✅ Secure password hashing using bcrypt  
✅ JWT tokens with expiration  
✅ Email-based authentication  
✅ SQLModel for database operations  
✅ FastAPI dependency injection for auth  
✅ Swagger UI OAuth2 integration  

---

## Architecture

### Authentication Flow

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       │ 1. POST /register
       │    {name, email, password}
       ▼
┌─────────────────────────────┐
│  Registration Endpoint      │
│  - Check if email exists    │
│  - Hash password (bcrypt)   │
│  - Save user to database    │
└──────┬──────────────────────┘
       │
       │ 2. POST /login
       │    {username: email, password}
       ▼
┌─────────────────────────────┐
│  Login Endpoint             │
│  - Verify credentials       │
│  - Create JWT token         │
│  - Return access_token      │
└──────┬──────────────────────┘
       │
       │ 3. GET /users/me
       │    Header: Authorization: Bearer <token>
       ▼
┌─────────────────────────────┐
│  get_current_user()         │
│  - Extract token            │
│  - Verify token signature   │
│  - Check expiration         │
│  - Load user from DB        │
│  - Return USER object       │
└─────────────────────────────┘
```

### JWT Token Structure

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNzY3NTcwNTU5fQ.a0hs1gHDk8cuc5D0UEYo6Pn8E0r5npCLiAQVEVwB8N8
│                                    │                                                                │
│         HEADER                     │                  PAYLOAD                                       │         SIGNATURE
│                                    │                                                                │
│  {                                 │  {                                                            │  HMACSHA256(
│    "alg": "HS256",                 │    "sub": "user@example.com",                                 │    base64UrlEncode(header) + "." +
│    "typ": "JWT"                    │    "exp": 1767570559                                          │    base64UrlEncode(payload),
│  }                                 │  }                                                            │    SECRET_KEY
│                                    │                                                                │  )
```

---

## Step-by-Step Implementation

### Step 1: Install Required Dependencies

First, add the authentication packages to your project:

```bash
uv add pyjwt "passlib[bcrypt]" "bcrypt<4.0.0"
```

**Why these packages?**
- `pyjwt`: For creating and verifying JWT tokens
- `passlib[bcrypt]`: For password hashing utilities
- `bcrypt<4.0.0`: Specific version to avoid compatibility issues with passlib

**Changes made to `pyproject.toml`:**
```toml
dependencies = [
    "bcrypt<4.0.0",
    "passlib[bcrypt]>=1.7.4",
    "pyjwt>=2.10.1",
    # ... other dependencies
]
```

### Step 2: Configure Environment Variables

Add authentication configuration to your `.env` file:

```env
# Existing database configuration
DATABASE_URL=postgresql://user:password@host/dbname

# New authentication configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Configuration Explanation:**
- `SECRET_KEY`: Used to sign and verify JWT tokens. **MUST be kept secret!**
- `ALGORITHM`: Hashing algorithm for JWT (HS256 is HMAC with SHA-256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: How long tokens remain valid (30 minutes)

⚠️ **Security Warning:** Generate a strong SECRET_KEY in production:
```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 3: Update User Model with Schemas

**File:** `backend/src/models/user.py`

Added three new schema classes to handle different data representations:

```python
from datetime import datetime
from sqlmodel import Field, SQLModel
from pydantic import EmailStr


# Database model (with table=True)
class USER(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str 
    email: str = Field(unique=True, index=True)
    password: str  # Stores the HASHED password
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Schema for user registration (accepts plain password)
class UserCreate(SQLModel):
    name: str
    email: EmailStr
    password: str


# Schema for API responses (never exposes password)
class UserResponse(SQLModel):
    id: int
    name: str
    email: str


# Schema for JWT token response
class Token(SQLModel):
    access_token: str
    token_type: str
```

**Why different schemas?**
- `USER`: Database model with all fields including hashed password
- `UserCreate`: Accepts input from clients (with plain password)
- `UserResponse`: Returns user data WITHOUT the password (security!)
- `Token`: Standardized JWT token response format

### Step 4: Extend Database Session Management

**File:** `backend/src/db/database.py`

Added a new function for FastAPI dependency injection:

```python
import os
import dotenv
from sqlmodel import Session, create_engine
from typing import Generator
from contextlib import contextmanager

dotenv.load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")
    
engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True)

# For use with 'with' statements (existing code)
@contextmanager
def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

# For use with FastAPI Depends() (NEW)
def get_db_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
```

**Why two functions?**
- `get_session()`: Context manager for script usage: `with get_session() as session:`
- `get_db_session()`: Generator for FastAPI dependencies: `session = Depends(get_db_session)`

The `@contextmanager` decorator makes a function incompatible with FastAPI's dependency injection, so we need both.

### Step 5: Create Authentication Module

**File:** `backend/src/auth/authentication.py` (NEW FILE)

This is the core authentication module. Let's break it down section by section:

#### 5.1 Imports and Configuration

```python
import os
from datetime import datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlmodel import Session, select
from dotenv import load_dotenv

from ..db.database import get_db_session
from ..models.user import USER, UserCreate, UserResponse, Token

load_dotenv()

# Config
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
```

**What's happening:**
- Loading environment variables for JWT configuration
- Importing all necessary FastAPI and security libraries
- Setting up defaults in case env vars are missing

#### 5.2 Password Hashing Setup

```python
# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
```

**`CryptContext` explained:**
- Creates a password hashing context using bcrypt algorithm
- `schemes=["bcrypt"]`: Use bcrypt for hashing
- `deprecated="auto"`: Automatically update hash format if needed
- This object provides `hash()` and `verify()` methods

#### 5.3 OAuth2 Scheme

```python
# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
```

**`OAuth2PasswordBearer` explained:**
- Tells FastAPI where to get the authentication token
- `tokenUrl="login"`: Points to the `/login` endpoint
- Automatically extracts the token from `Authorization: Bearer <token>` header
- Integrates with Swagger UI for authentication

⚠️ **Important:** The `tokenUrl` must match your login endpoint name!

#### 5.4 Password Utilities

```python
# Password utilities
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
```

**Function purposes:**
- `verify_password()`: Checks if a plain password matches a hashed one (for login)
- `get_password_hash()`: Converts plain password to bcrypt hash (for registration)

**How bcrypt works:**
```python
plain = "mypassword"
hashed = get_password_hash(plain)
# Result: "$2b$12$IwABdbdf8b.jGGWDIyZQmeow5JjE1dDP8UBzEteAHEuQ3D91B8ITO"

verify_password(plain, hashed)  # Returns True
verify_password("wrongpass", hashed)  # Returns False
```

#### 5.5 Token Utilities

```python
# Token utilities
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

**What this does:**
1. Copies the input data (usually `{"sub": "user@example.com"}`)
2. Adds expiration time (`exp`) to the payload
3. Encodes and signs the JWT using SECRET_KEY
4. Returns the token string

**Example:**
```python
token = create_access_token(data={"sub": "user@example.com"})
# Result: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNzY3NTcwNTU5fQ..."
```

```python
def verify_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except jwt.PyJWTError:
        return None
```

**What this does:**
1. Decodes the JWT token using SECRET_KEY
2. Validates the signature and expiration
3. Extracts the email from the "sub" (subject) claim
4. Returns email on success, None on failure

**Security checks performed:**
- ✅ Signature validation (ensures token wasn't tampered with)
- ✅ Expiration check (token must not be expired)
- ✅ Algorithm verification (prevents algorithm confusion attacks)

#### 5.6 Get Current User Dependency

```python
# Dependency to get current user
def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[Session, Depends(get_db_session)]
) -> USER:
    email = verify_token(token)
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = session.exec(select(USER).where(USER.email == email)).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

**This is a FastAPI dependency function. Here's the flow:**

1. **Extract token:** `oauth2_scheme` automatically gets the token from the Authorization header
2. **Verify token:** Calls `verify_token()` to validate and extract email
3. **Check validity:** If token is invalid/expired, return 401 Unauthorized
4. **Get database session:** `get_db_session` provides a DB connection
5. **Query user:** Looks up user by email from token
6. **Check existence:** If user doesn't exist, return 404
7. **Return user:** Returns the complete USER object

**Usage in endpoints:**
```python
@app.get("/protected")
def protected_route(current_user: USER = Depends(get_current_user)):
    return {"message": f"Hello {current_user.name}!"}
```

FastAPI automatically:
- Calls `get_current_user()`
- Injects the USER object into `current_user`
- Returns 401 if authentication fails

### Step 6: Add Authentication Endpoints to Main

**File:** `backend/src/main.py`

#### 6.1 New Imports

```python
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
```

**New imports explained:**
- `Depends`: For dependency injection
- `OAuth2PasswordRequestForm`: Standard form for username/password
- `Annotated`: For better type hints with dependencies
- `select`: For SQLModel queries
- `UserCreate, UserResponse, Token`: Schemas from user model
- Auth functions from authentication module
- `get_db_session`: Database session dependency

#### 6.2 Registration Endpoint

```python
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
        password=get_password_hash(user.password)  # Hash the password!
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user
```

**Step-by-step breakdown:**

1. **Endpoint definition:**
   - `@app.post("/register")`: HTTP POST to /register
   - `response_model=UserResponse`: Automatically excludes password from response

2. **Input validation:**
   - `user: UserCreate`: Pydantic validates name, email (EmailStr), password

3. **Check for duplicates:**
   - Query database for existing email
   - Return 400 error if email already exists

4. **Hash password:**
   - **NEVER store plain passwords!**
   - `get_password_hash()` converts "mypassword" to bcrypt hash

5. **Save to database:**
   - Create USER object with hashed password
   - Add to session and commit
   - Refresh to get the auto-generated ID

6. **Return user:**
   - FastAPI automatically converts to UserResponse
   - Password is excluded from response

**Example request:**
```bash
POST /register
{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "securepassword123"
}
```

**Example response:**
```json
{
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com"
}
```

#### 6.3 Login Endpoint

```python
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
```

**Step-by-step breakdown:**

1. **Endpoint definition:**
   - `@app.post("/login")`: HTTP POST to /login
   - `response_model=Token`: Returns JWT token

2. **OAuth2 form data:**
   - `OAuth2PasswordRequestForm`: Standard OAuth2 format
   - Expects `username` and `password` fields
   - In our case, `username` contains the email

3. **Find user:**
   - Query database by email (`form_data.username`)
   - Email is stored in `username` field per OAuth2 standard

4. **Verify credentials:**
   - Check if user exists
   - Verify password matches hash using bcrypt
   - Return 401 if invalid (don't reveal which part failed!)

5. **Create JWT token:**
   - `create_access_token()` generates signed JWT
   - Payload contains email in "sub" claim
   - Token expires after ACCESS_TOKEN_EXPIRE_MINUTES

6. **Return token:**
   - Client receives token to use in future requests
   - `token_type: "bearer"` indicates Bearer authentication

**Example request (form-data):**
```bash
POST /login
Content-Type: application/x-www-form-urlencoded

username=john@example.com&password=securepassword123
```

**Example response:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huQGV4YW1wbGUuY29tIiwiZXhwIjoxNzY3NTcwNTU5fQ.a0hs1gHDk8cuc5D0UEYo6Pn8E0r5npCLiAQVEVwB8N8",
    "token_type": "bearer"
}
```

#### 6.4 Protected Endpoint Example

```python
@app.get("/users/me", response_model=UserResponse)
def read_current_user(current_user: Annotated[USER, Depends(get_current_user)]):
    return current_user
```

**How this works:**

1. **Dependency injection:**
   - `Depends(get_current_user)` automatically handles authentication
   - FastAPI calls `get_current_user()` before the endpoint function

2. **Authentication flow:**
   - Client sends: `Authorization: Bearer <token>`
   - `oauth2_scheme` extracts the token
   - `verify_token()` validates and extracts email
   - Database query loads the user
   - User object injected into `current_user`

3. **Automatic responses:**
   - If no token: 401 Unauthorized
   - If invalid token: 401 Unauthorized
   - If user not found: 404 Not Found
   - If valid: Returns user data (without password)

**Example request:**
```bash
GET /users/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Example response:**
```json
{
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com"
}
```

---

## Code Walkthrough

### How Everything Connects

```
┌──────────────────────────────────────────────────────────────────┐
│                         Client Request                           │
│  GET /users/me                                                   │
│  Authorization: Bearer eyJhbGci...                               │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│              FastAPI Route Handler                               │
│  @app.get("/users/me")                                           │
│  def read_current_user(                                          │
│      current_user: USER = Depends(get_current_user)  ◄───┐      │
│  )                                                        │      │
└───────────────────────────────────────────────────────────┼──────┘
                                                            │
                     ┌──────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────────┐
│           get_current_user() Dependency                          │
│  1. token = Depends(oauth2_scheme)  ◄────┐                      │
│  2. session = Depends(get_db_session)  ◄─┼──┐                   │
│  3. email = verify_token(token)  ◄───────┼──┼──┐                │
│  4. user = session.query(email)          │  │  │                │
│  5. return user                          │  │  │                │
└──────────────────────────────────────────┼──┼──┼────────────────┘
                                           │  │  │
          ┌────────────────────────────────┘  │  │
          ▼                                    │  │
┌───────────────────────────────────────┐     │  │
│     oauth2_scheme                     │     │  │
│  - Extracts "Bearer <token>"          │     │  │
│  - Returns token string               │     │  │
└───────────────────────────────────────┘     │  │
                                              │  │
                 ┌────────────────────────────┘  │
                 ▼                                │
┌───────────────────────────────────────┐        │
│     get_db_session()                  │        │
│  - Creates database session           │        │
│  - Yields session                     │        │
│  - Closes after use                   │        │
└───────────────────────────────────────┘        │
                                                 │
                    ┌────────────────────────────┘
                    ▼
┌───────────────────────────────────────┐
│     verify_token(token)               │
│  - jwt.decode(token, SECRET_KEY)      │
│  - Validates signature                │
│  - Checks expiration                  │
│  - Extracts email from "sub"          │
│  - Returns email or None              │
└───────────────────────────────────────┘
```

### Key Concepts

#### 1. Dependency Injection in FastAPI

FastAPI's dependency injection system is powerful:

```python
# Dependencies are functions that run before endpoint
def get_current_user(token: str = Depends(oauth2_scheme)):
    # This runs first
    return validate(token)

# Endpoint uses the dependency
@app.get("/protected")
def protected(user = Depends(get_current_user)):
    # user is the return value from get_current_user()
    return {"user": user}
```

**Dependencies can depend on other dependencies:**
```python
oauth2_scheme  →  get_current_user  →  protected_endpoint
     ↓                  ↓                      ↓
  extract token    validate token      use user data
```

#### 2. SQLModel vs SQLAlchemy

We use **SQLModel** which combines SQLAlchemy + Pydantic:

```python
# With table=True: Database model
class USER(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True)

# Without table=True: Just a Pydantic schema
class UserResponse(SQLModel):
    id: int
    email: str
```

**Benefits:**
- Single source of truth for models
- Automatic validation (Pydantic)
- Database operations (SQLAlchemy)
- Type hints throughout

#### 3. Password Security

**Why bcrypt?**
- Slow by design (prevents brute force)
- Automatically includes salt
- Adapts to hardware improvements

```python
# Hashing is slow (good for security!)
hash1 = get_password_hash("password123")
# "$2b$12$IwABdbdf8b.jGGWDIyZQmeow5JjE1dDP8UBzEteAHEuQ3D91B8ITO"

# Same password produces different hash each time (salt)
hash2 = get_password_hash("password123")
# "$2b$12$XyZ789abc...different..."

# But verification still works!
verify_password("password123", hash1)  # True
verify_password("password123", hash2)  # True
```

#### 4. JWT Token Lifecycle

```
Registration/Login
      ↓
Server creates JWT
  Header: {"alg": "HS256", "typ": "JWT"}
  Payload: {"sub": "user@example.com", "exp": 1767570559}
  Signature: HMACSHA256(header + payload, SECRET_KEY)
      ↓
Client receives token
      ↓
Client stores token (localStorage, cookie, etc.)
      ↓
Client includes in requests
  Authorization: Bearer <token>
      ↓
Server verifies signature & expiration
      ↓
Server extracts user info from payload
      ↓
Server processes request
```

---

## Errors Encountered & Solutions

### Error 1: Bcrypt Version Incompatibility

**Error Message:**
```
(trapped) error reading bcrypt version
Traceback (most recent call last):
  File ".../passlib/handlers/bcrypt.py", line 620, in _load_backend_mixin
    version = _bcrypt.__about__.__version__
AttributeError: module 'bcrypt' has no attribute '__about__'

ValueError: password cannot be longer than 72 bytes, truncate manually if necessary
```

**Root Cause:**
- Newer versions of `bcrypt` (4.0+) removed the `__about__` attribute
- `passlib` expected this attribute to exist
- This caused initialization failures

**Solution:**
```bash
uv add "bcrypt<4.0.0"
```

Downgrade bcrypt to 3.x which is compatible with passlib.

**Alternative Solutions:**
1. Use bcrypt directly without passlib
2. Wait for passlib update (not maintained actively)
3. Switch to argon2 (more modern but different setup)

**Why this works:**
- Bcrypt 3.x has the `__about__` module
- Passlib can properly detect the version
- Password hashing works correctly

---

### Error 2: Token Endpoint Not Found (404)

**Error Message:**
```
INFO: 127.0.0.1:51353 - "POST /token HTTP/1.1" 404 Not Found
Auth Error Error: Not Found
```

**Root Cause:**
- Swagger UI was configured to call `/token` endpoint
- Our endpoint was named `/login`
- `OAuth2PasswordBearer(tokenUrl="token")` didn't match

**Solution Option 1:** Change endpoint name to match tokenUrl
```python
# In main.py
@app.post("/token", response_model=Token)  # Was "/login"
def login(...):
    ...
```

**Solution Option 2:** Change tokenUrl to match endpoint (USED)
```python
# In authentication.py
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")  # Was "token"
```

**Why this matters:**
- `tokenUrl` tells Swagger UI where to send credentials
- Must match the actual endpoint path exactly
- Case-sensitive!

**Lesson Learned:**
- Endpoint naming consistency is critical
- OAuth2 has standardized endpoint names (`/token`)
- But custom names work if configured properly

---

### Error 3: .env File Parsing Warnings

**Warning Message:**
```
python-dotenv could not parse statement starting at line 20
python-dotenv could not parse statement starting at line 21
```

**Root Cause:**
- User accidentally pasted JSON data into `.env` file
- `.env` files only support `KEY=value` format

**Example of what was wrong:**
```env
SECRET_KEY=abc123
ALGORITHM=HS256
{
  "access_token": "eyJhbGci...",  ← This caused error
  "token_type": "bearer"
}
```

**Solution:**
Remove non-environment variable content from `.env`:
```env
SECRET_KEY=abc123
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**`.env` File Rules:**
- One variable per line
- Format: `KEY=value`
- No quotes needed (usually)
- No JSON, YAML, or other formats
- Comments start with `#`

---

### Error 4: Context Manager vs Generator for Dependencies

**Error (Conceptual):**
Using `@contextmanager` decorated function with FastAPI dependencies doesn't work.

**Problem Code:**
```python
@contextmanager
def get_session():
    with Session(engine) as session:
        yield session

# This fails!
@app.get("/users")
def get_users(session = Depends(get_session)):
    ...
```

**Why it fails:**
- `@contextmanager` wraps the function
- Returns a context manager object, not a generator
- FastAPI expects a plain generator function

**Solution:**
Create separate functions:
```python
# For 'with' statements in scripts
@contextmanager
def get_session():
    with Session(engine) as session:
        yield session

# For FastAPI Depends()
def get_db_session():
    with Session(engine) as session:
        yield session
```

**Usage:**
```python
# In scripts
with get_session() as session:
    users = session.exec(select(USER)).all()

# In FastAPI
@app.get("/users")
def get_users(session = Depends(get_db_session)):
    users = session.exec(select(USER)).all()
```

---

## Testing the Implementation

### Using Swagger UI (http://localhost:8000/docs)

#### Step 1: Register a User

1. Navigate to `POST /register`
2. Click "Try it out"
3. Enter request body:
```json
{
  "name": "Test User",
  "email": "test@example.com",
  "password": "securepassword123"
}
```
4. Click "Execute"
5. Should receive 200 response with user data (no password)

#### Step 2: Authenticate in Swagger

1. Click the 🔓 **Authorize** button at the top
2. In the OAuth2 dialog:
   - **username:** `test@example.com` (your email)
   - **password:** `securepassword123`
   - Leave client_id and client_secret empty
3. Click **Authorize**
4. Should see "Authorized" with a ✅

#### Step 3: Test Protected Endpoint

1. Navigate to `GET /users/me`
2. Click "Try it out"
3. Click "Execute"
4. Should receive 200 response with your user data

### Using curl

#### Register:
```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "securepassword123"
  }'
```

#### Login:
```bash
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=securepassword123"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Access Protected Route:
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X GET "http://localhost:8000/users/me" \
  -H "Authorization: Bearer $TOKEN"
```

### Using httpie (cleaner syntax)

```bash
# Register
http POST localhost:8000/register \
  name="Test User" \
  email=test@example.com \
  password=securepassword123

# Login
http --form POST localhost:8000/login \
  username=test@example.com \
  password=securepassword123

# Protected route
http GET localhost:8000/users/me \
  "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Testing Token Expiration

To test token expiration:

1. Set short expiration in `.env`:
```env
ACCESS_TOKEN_EXPIRE_MINUTES=1
```

2. Login and get token
3. Wait 2 minutes
4. Try to access `/users/me`
5. Should receive 401 Unauthorized

---

## Security Considerations

### ✅ What We Implemented

1. **Password Hashing**
   - Passwords never stored in plain text
   - Bcrypt with automatic salt
   - Slow hashing prevents brute force

2. **JWT Tokens**
   - Cryptographically signed
   - Cannot be tampered with
   - Expiration built-in

3. **Email Validation**
   - Pydantic EmailStr validates format
   - Prevents invalid emails in database

4. **Response Models**
   - UserResponse excludes password
   - Never exposes sensitive data

### ⚠️ Production Considerations

#### 1. SECRET_KEY Management

**Current (Development):**
```env
SECRET_KEY=your-super-secret-key-change-this
```

**Production:**
- Generate strong random key
- Store in secure secrets manager (AWS Secrets Manager, Azure Key Vault, etc.)
- Rotate periodically
- Never commit to git

```bash
# Generate secure key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### 2. HTTPS Only

**Issue:** Tokens sent in plain text over HTTP can be intercepted

**Solution:**
- Enforce HTTPS in production
- Use secure cookies for token storage
- Set HSTS headers

```python
# Add to main.py for production
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

if os.getenv("ENVIRONMENT") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
```

#### 3. Token Refresh

**Current:** Tokens expire, users must login again

**Better:**
- Implement refresh tokens
- Access tokens expire quickly (15 minutes)
- Refresh tokens expire slowly (7 days)
- Rotate tokens on each refresh

#### 4. Rate Limiting

**Issue:** Unlimited login attempts enable brute force

**Solution:**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/login")
@limiter.limit("5/minute")  # 5 attempts per minute
def login(...):
    ...
```

#### 5. CORS Configuration

**Current (Development):**
```python
allow_origins=["*"]  # Allows all origins!
```

**Production:**
```python
allow_origins=[
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]
```

#### 6. Database Connection Security

**Checklist:**
- ✅ Use connection pooling
- ✅ Enable SSL for database connections
- ✅ Use prepared statements (SQLModel does this)
- ✅ Implement connection retry logic

#### 7. Token Storage (Frontend)

**Options:**

| Storage      | XSS Vulnerable | CSRF Vulnerable | Best For               |
|--------------|----------------|-----------------|------------------------|
| localStorage | ✅ Yes          | ❌ No           | Simple SPAs            |
| sessionStorage| ✅ Yes         | ❌ No           | Tab-scoped sessions    |
| Cookie (HttpOnly)| ❌ No       | ✅ Yes          | Production (with CSRF) |
| Memory only  | ❌ No          | ❌ No           | Maximum security       |

**Recommendation:** HttpOnly cookies with CSRF protection

#### 8. Logging & Monitoring

**What to log:**
- ✅ Failed login attempts
- ✅ Token validation failures
- ✅ Unusual access patterns
- ❌ Never log passwords or tokens!

```python
import logging

logger = logging.getLogger(__name__)

@app.post("/login")
def login(...):
    if not user:
        logger.warning(f"Failed login attempt for {form_data.username}")
        ...
```

#### 9. Account Security Features

**Consider adding:**
- Email verification on registration
- Password reset flow
- Two-factor authentication (2FA)
- Account lockout after failed attempts
- Login notification emails
- Session management (logout all devices)

---

## Summary

### What We Built

✅ Complete JWT authentication system  
✅ Secure password hashing with bcrypt  
✅ User registration and login  
✅ Protected routes with dependencies  
✅ Swagger UI OAuth2 integration  
✅ SQLModel for type-safe database operations  

### Key Files Modified/Created

| File | Purpose |
|------|---------|
| `src/auth/authentication.py` | Core authentication logic |
| `src/models/user.py` | User model and schemas |
| `src/db/database.py` | Database session management |
| `src/main.py` | Authentication endpoints |
| `.env` | Configuration (SECRET_KEY, etc.) |
| `pyproject.toml` | Dependencies |

### Testing Checklist

- [ ] Register new user
- [ ] Login with correct credentials
- [ ] Login with wrong credentials (should fail)
- [ ] Access `/users/me` without token (should fail)
- [ ] Access `/users/me` with valid token (should work)
- [ ] Access `/users/me` with expired token (should fail)
- [ ] Try to register duplicate email (should fail)

### Next Steps

1. **Implement refresh tokens** for better UX
2. **Add password reset** via email
3. **Implement rate limiting** on auth endpoints
4. **Add email verification** on registration
5. **Set up monitoring** and alerting
6. **Review and harden** security for production
7. **Add unit tests** for authentication functions
8. **Document API** with OpenAPI tags

---

## Appendix: Quick Reference

### Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Authentication
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Common Commands

```bash
# Install dependencies
uv add pyjwt "passlib[bcrypt]" "bcrypt<4.0.0"

# Generate secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Run server
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Test with httpie
http POST localhost:8000/register name="User" email=user@example.com password=pass123
http --form POST localhost:8000/login username=user@example.com password=pass123
http GET localhost:8000/users/me "Authorization: Bearer <token>"
```

### Useful Links

- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT.io - Decode Tokens](https://jwt.io/)
- [PyJWT Documentation](https://pyjwt.readthedocs.io/)
- [Passlib Documentation](https://passlib.readthedocs.io/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)

---

**End of Guide**

This documentation was created on January 4, 2026, based on the actual implementation process, including all errors encountered and their solutions. It serves as both a reference and a learning resource for understanding JWT authentication in FastAPI.

