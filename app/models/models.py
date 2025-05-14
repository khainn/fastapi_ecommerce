from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from uuid import uuid4, UUID

from app.common.enums import OrderStatus

class ProductCategory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str = ""
    products: List["Product"] = Relationship(back_populates="category")

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str = ""
    price: int
    quantity_in_stock: int
    image_url: str = ""
    total_sold: int = 0
    category_id: Optional[int] = Field(default=None, foreign_key="productcategory.id")
    category: Optional[ProductCategory] = Relationship(back_populates="products")
    cart_items: List["CartItem"] = Relationship(back_populates="product")

class Cart(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    items: List["CartItem"] = Relationship(back_populates="cart")

class CartItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cart_id: UUID = Field(foreign_key="cart.id")
    product_id: int = Field(foreign_key="product.id")
    quantity: int
    cart: Cart = Relationship(back_populates="items")
    product: Product = Relationship(back_populates="cart_items")

class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cart_id: UUID = Field(foreign_key="cart.id")
    customer_name: str
    customer_phone: str
    customer_address: str
    status: str = Field(default=OrderStatus.PENDING.value)
    total_price: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
