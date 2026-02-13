from pydantic import BaseModel
from typing import List
from datetime import datetime


class OrderItem(BaseModel):
    product_id: str
    name: str
    quantity: int
    price: float


class OrderCreate(BaseModel):
    items: List[OrderItem]


class OrderResponse(BaseModel):
    id: str
    user_id: str
    items: List[OrderItem]
    total: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
