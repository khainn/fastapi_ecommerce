from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.db import get_session
from app.models.models import Order, CartItem, Product
from uuid import UUID

router = APIRouter()

@router.post("/")
def create_order(cart_id: UUID, name: str, phone: str, address: str, session: Session = Depends(get_session)):
    items = session.exec(select(CartItem).where(CartItem.cart_id == cart_id)).all()
    total = sum([session.get(Product, item.product_id).price * item.quantity for item in items])

    for item in items:
        product = session.get(Product, item.product_id)
        product.total_sold += item.quantity
        product.quantity_in_stock -= item.quantity

    order = Order(cart_id=cart_id, customer_name=name, customer_phone=phone,
                  customer_address=address, total_price=total)
    session.add(order)
    session.commit()
    return order
