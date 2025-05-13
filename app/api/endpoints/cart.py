from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.core.db import get_session
from app.models.models import Cart, CartItem, Product
from uuid import UUID
from typing import List

router = APIRouter()

@router.post("/add")
def add_to_cart(cart_id: UUID, product_id: int, quantity: int, session: Session = Depends(get_session)):
    item = CartItem(cart_id=cart_id, product_id=product_id, quantity=quantity)
    session.add(item)
    session.commit()
    return {"message": "Added to cart"}

@router.get("/{cart_id}")
def view_cart(cart_id: UUID, session: Session = Depends(get_session)):
    items = session.exec(select(CartItem).where(CartItem.cart_id == cart_id)).all()
    return items

@router.put("/item/{item_id}")
def update_cart_item(item_id: int, quantity: int, session: Session = Depends(get_session)):
    item = session.get(CartItem, item_id)
    item.quantity = quantity
    session.commit()
    return item

@router.delete("/item/{item_id}")
def delete_cart_item(item_id: int, session: Session = Depends(get_session)):
    item = session.get(CartItem, item_id)
    session.delete(item)
    session.commit()
    return {"message": "Deleted"}
