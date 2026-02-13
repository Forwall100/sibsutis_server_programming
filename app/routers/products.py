from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.core.database import products_collection
from app.schemas.product import ProductCreate, ProductResponse
from app.schemas.user import UserResponse
from app.routers.auth import get_current_user
from app.utils.password import verify_password
from bson import ObjectId

router = APIRouter(prefix="/products", tags=["products"])


def get_admin_user(current_user: dict = Depends(get_current_user)) -> dict:
    from app.core.database import users_collection

    user = users_collection.find_one({"_id": ObjectId(current_user["sub"])})
    if not user or not user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.get("/", response_model=List[ProductResponse])
def get_products():
    products = list(products_collection.find())
    return [
        ProductResponse(
            id=str(p["_id"]),
            name=p["name"],
            description=p.get("description"),
            price=p["price"],
            stock=p.get("stock", 0),
        )
        for p in products
    ]


@router.post("/", response_model=ProductResponse)
def create_product(product: ProductCreate, admin: dict = Depends(get_admin_user)):
    product_data = product.model_dump()
    result = products_collection.insert_one(product_data)
    product_data["_id"] = result.inserted_id

    return ProductResponse(
        id=str(product_data["_id"]),
        name=product_data["name"],
        description=product_data.get("description"),
        price=product_data["price"],
        stock=product_data.get("stock", 0),
    )
