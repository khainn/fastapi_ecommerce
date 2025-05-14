from typing import Optional, List
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from uuid import UUID

# CartItem Schemas
class CartItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: int = Field(..., gt=0)

class CartItemInDB(CartItemBase):
    id: int
    cart_id: UUID
    product: Optional["ProductResponse"] = None

    class Config:
        from_attributes = True

class CartItemResponse(CartItemInDB):
    pass

# Cart Schemas
class CartBase(BaseModel):
    pass

class CartCreate(CartBase):
    pass

class CartInDB(CartBase):
    id: UUID
    created_at: datetime
    items: List[CartItemResponse] = []

    class Config:
        from_attributes = True

class CartResponse(CartInDB):
    pass

# Import here to avoid circular imports
from .product import ProductResponse 