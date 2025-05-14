from typing import Optional, List
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from enum import Enum
from uuid import UUID

class OrderBase(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=100)
    customer_phone: str = Field(..., min_length=1, max_length=20)
    customer_address: str = Field(..., min_length=1, max_length=500)

class OrderCreate(OrderBase):
    cart_id: UUID

class OrderInDB(OrderBase):
    id: int
    cart_id: UUID
    total_price: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class OrderResponse(OrderInDB):
    pass
