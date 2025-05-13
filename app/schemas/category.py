from typing import Optional, List
from pydantic import BaseModel, Field

# Base Schema
class ProductCategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)

# Input Schemas
class ProductCategoryCreate(ProductCategoryBase):
    pass

class ProductCategoryUpdate(ProductCategoryBase):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

# Output Schemas
class ProductCategoryInDB(ProductCategoryBase):
    id: int

    class Config:
        from_attributes = True

class ProductCategoryResponse(ProductCategoryInDB):
    pass

# List Response Schema
class ProductCategoryList(BaseModel):
    items: List[ProductCategoryResponse]
    total: int 