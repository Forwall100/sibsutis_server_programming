from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.core.database import users_collection
from app.schemas.user import UserCreate, UserResponse
from app.utils.password import hash_password, verify_password
from app.utils.auth import create_access_token, verify_token
from bson import ObjectId

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate):
    existing = users_collection.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_data = {
        "email": user.email,
        "username": user.username,
        "password_hash": hash_password(user.password),
        "is_admin": False,
    }
    result = users_collection.insert_one(user_data)
    user_data["_id"] = result.inserted_id

    return UserResponse(
        id=str(user_data["_id"]),
        email=user_data["email"],
        username=user_data["username"],
        is_admin=user_data["is_admin"],
    )


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_collection.find_one({"email": form_data.username})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        {"sub": str(user["_id"]), "email": user["email"]}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: dict = Depends(get_current_user)):
    user = users_collection.find_one({"_id": ObjectId(current_user["sub"])})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(
        id=str(user["_id"]),
        email=user["email"],
        username=user["username"],
        is_admin=user.get("is_admin", False),
    )
