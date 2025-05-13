from typing import Optional, List
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

# OrderItem Schemas
class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    price: Decimal = Field(..., ge=0)

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemInDB(OrderItemBase):
    id: int
    order_id: int
    product: Optional["ProductResponse"] = None
    subtotal: Decimal

    class Config:
        from_attributes = True

class OrderItemResponse(OrderItemInDB):
    pass

# Order Schemas
class OrderBase(BaseModel):
    shipping_address: str = Field(..., min_length=1, max_length=500)
    status: OrderStatus = OrderStatus.PENDING

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    shipping_address: Optional[str] = Field(None, min_length=1, max_length=500)

class OrderInDB(OrderBase):
    id: int
    user_id: int
    items: List[OrderItemResponse] = []
    total: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class OrderResponse(OrderInDB):
    pass

# List Response Schema
class OrderList(BaseModel):
    items: List[OrderResponse]
    total: int

# Import here to avoid circular imports
from .product import ProductResponse 