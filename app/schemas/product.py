from typing import Optional, List
from pydantic import BaseModel, Field, condecimal
from decimal import Decimal

# Base Schema
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)
    price: Decimal = Field(..., ge=0)
    quantity_in_stock: int = Field(..., ge=0)
    category_id: int

# Input Schemas
class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    price: Optional[Decimal] = Field(None, ge=0)
    quantity_in_stock: Optional[int] = Field(None, ge=0)
    category_id: Optional[int] = None

# Output Schemas
class ProductInDB(ProductBase):
    id: int
    category: Optional["ProductCategoryResponse"] = None

    class Config:
        from_attributes = True

class ProductResponse(ProductInDB):
    pass

# List Response Schema
class ProductList(BaseModel):
    items: List[ProductResponse]
    total: int

# Import here to avoid circular imports
from .category import ProductCategoryResponse 