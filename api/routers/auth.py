"""
Auth endpoints – register / login / logout / me / profile
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, field_validator
from typing import Optional, Literal

from ..services.auth_service import (
    authenticate_admin,
    create_access_token,
    get_current_admin,
    get_current_user,
)
from ..services import user_service

router = APIRouter(prefix="/auth", tags=["Auth"])

OccupationT = Literal["student", "employee", "freelancer", "self_employed", "other"]
JoinReasonT = Literal["searching_phone", "comparing_prices", "reading_reviews", "browsing"]

# ── Schemas ───────────────────────────────────────────────────────────────────

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str = "user"


class UserInfo(BaseModel):
    username: str
    role: str


class UserProfile(BaseModel):
    id: str
    username: str
    email: str
    age: Optional[int] = None
    occupation: Optional[str] = None
    avatar: Optional[str] = None
    favourite_brand: Optional[str] = None
    current_phone: Optional[str] = None
    join_reason: Optional[str] = None
    created_at: str


class RegisterRequest(BaseModel):
    # ── core credentials
    username: str
    email: str
    password: str
    # ── profile
    age: Optional[int] = None
    occupation: Optional[OccupationT] = None
    avatar: Optional[str] = None          # base64 data-URL
    favourite_brand: Optional[str] = None
    current_phone: Optional[str] = None
    join_reason: Optional[JoinReasonT] = None

    @field_validator("username")
    @classmethod
    def username_valid(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username may only contain letters, numbers, - and _")
        return v

    @field_validator("password")
    @classmethod
    def password_strong(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v

    @field_validator("age")
    @classmethod
    def age_range(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and not (13 <= v <= 100):
            raise ValueError("Age must be between 13 and 100")
        return v


class ProfileUpdateRequest(BaseModel):
    email: Optional[str] = None
    age: Optional[int] = None
    occupation: Optional[OccupationT] = None
    avatar: Optional[str] = None
    favourite_brand: Optional[str] = None
    current_phone: Optional[str] = None
    join_reason: Optional[JoinReasonT] = None

    @field_validator("age")
    @classmethod
    def age_range(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and not (13 <= v <= 100):
            raise ValueError("Age must be between 13 and 100")
        return v


class UserLoginRequest(BaseModel):
    username: str
    password: str


# ── Admin login (OAuth2 form – keeps Swagger UI working) ─────────────────────

@router.post("/login", response_model=TokenResponse)
async def admin_login(form: OAuth2PasswordRequestForm = Depends()):
    """Admin login – returns a JWT bearer token."""
    if not authenticate_admin(form.username, form.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token({"sub": form.username, "role": "admin"})
    return TokenResponse(access_token=token, username=form.username, role="admin")


# ── User register ─────────────────────────────────────────────────────────────

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest):
    """Register a new user account and return a JWT immediately."""
    if user_service.get_by_username(body.username):
        raise HTTPException(status_code=409, detail="Username already taken")
    if user_service.get_by_email(body.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    new_user = user_service.create_user(
        username=body.username,
        email=body.email,
        password=body.password,
        age=body.age,
        occupation=body.occupation,
        avatar=body.avatar,
        favourite_brand=body.favourite_brand,
        current_phone=body.current_phone,
        join_reason=body.join_reason,
    )
    token = create_access_token({"sub": new_user["username"], "role": "user"})
    return TokenResponse(access_token=token, username=new_user["username"], role="user")


# ── User login ────────────────────────────────────────────────────────────────

@router.post("/user-login", response_model=TokenResponse)
async def user_login(body: UserLoginRequest):
    """Regular-user login – JSON body {username, password}."""
    user = user_service.authenticate_user(body.username, body.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = create_access_token({"sub": user["username"], "role": "user"})
    return TokenResponse(access_token=token, username=user["username"], role="user")


# ── Who am I (basic) ─────────────────────────────────────────────────────────

@router.get("/me", response_model=UserInfo)
async def me(current: dict = Depends(get_current_user)):
    """Return role info for the currently authenticated user."""
    return UserInfo(**current)


# ── Full profile ──────────────────────────────────────────────────────────────

@router.get("/me/profile", response_model=UserProfile)
async def get_profile(current: dict = Depends(get_current_user)):
    """Return the full profile of the logged-in user."""
    user = user_service.get_by_username(current["username"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserProfile(**{k: v for k, v in user.items() if k != "hashed_password"})


@router.put("/me/profile", response_model=UserProfile)
async def update_profile(body: ProfileUpdateRequest, current: dict = Depends(get_current_user)):
    """Update mutable profile fields for the logged-in user."""
    role = current.get("role", "user")
    if role == "admin":
        raise HTTPException(status_code=403, detail="Admin profile is not editable here")
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    # Email uniqueness check
    if "email" in updates:
        existing = user_service.get_by_email(updates["email"])
        if existing and existing["username"].lower() != current["username"].lower():
            raise HTTPException(status_code=409, detail="Email already in use by another account")
    updated = user_service.update_user(current["username"], updates)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return UserProfile(**updated)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def pw_strong(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


@router.post("/me/change-password")
async def change_password(body: ChangePasswordRequest, current: dict = Depends(get_current_user)):
    """Change password for the logged-in user."""
    user = user_service.get_by_username(current["username"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user_service.verify_password(body.current_password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    user_service.update_password(current["username"], body.new_password)
    return {"message": "Password updated successfully"}


# ── Logout ───────────────────────────────────────────────────────────────────

@router.post("/logout")
async def logout(_: dict = Depends(get_current_user)):
    """Stateless logout – client should discard the JWT."""
    return {"message": "Logged out successfully"}

