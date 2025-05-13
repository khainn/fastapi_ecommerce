from typing import Optional, List
from pydantic import BaseModel, Field
from decimal import Decimal

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
    cart_id: int
    product: Optional["ProductResponse"] = None
    subtotal: Decimal

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
    id: int
    user_id: int
    items: List[CartItemResponse] = []
    total: Decimal = Decimal("0.00")

    class Config:
        from_attributes = True

class CartResponse(CartInDB):
    pass

# Import here to avoid circular imports
from .product import ProductResponse 