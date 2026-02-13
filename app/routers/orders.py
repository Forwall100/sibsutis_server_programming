from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime
from app.core.database import orders_collection, products_collection
from app.schemas.order import OrderCreate, OrderResponse, OrderItem
from app.routers.auth import get_current_user
from bson import ObjectId

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/", response_model=List[OrderResponse])
def get_orders(current_user: dict = Depends(get_current_user)):
    orders = list(orders_collection.find({"user_id": current_user["sub"]}))
    return [
        OrderResponse(
            id=str(o["_id"]),
            user_id=o["user_id"],
            items=[OrderItem(**item) for item in o["items"]],
            total=o["total"],
            status=o.get("status", "pending"),
            created_at=o.get("created_at", datetime.utcnow()),
        )
        for o in orders
    ]


@router.post("/", response_model=OrderResponse)
def create_order(order: OrderCreate, current_user: dict = Depends(get_current_user)):
    total = sum(item.price * item.quantity for item in order.items)

    order_data = {
        "user_id": current_user["sub"],
        "items": [item.model_dump() for item in order.items],
        "total": total,
        "status": "pending",
        "created_at": datetime.utcnow(),
    }

    result = orders_collection.insert_one(order_data)
    order_data["_id"] = result.inserted_id

    return OrderResponse(
        id=str(order_data["_id"]),
        user_id=order_data["user_id"],
        items=order_data["items"],
        total=order_data["total"],
        status=order_data["status"],
        created_at=order_data["created_at"],
    )
