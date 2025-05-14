from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.core.db import get_session
from app.models.models import Order, CartItem, Cart
from app.schemas.order import OrderCreate, OrderResponse
from app.common.enums import OrderStatus
from uuid import UUID
from typing import List

router = APIRouter()

def get_order_or_404(session: Session, order_id: int) -> Order:
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order with id {order_id} not found")
    return order

def get_cart_or_404(session: Session, cart_id: UUID) -> Cart:
    cart = session.get(Cart, cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail=f"Cart with id {cart_id} not found")
    return cart

@router.post("/", response_model=OrderResponse)
def create_order(
    order_data: OrderCreate,
    session: Session = Depends(get_session)
):
    """Create a new order from a cart."""
    get_cart_or_404(session, order_data.cart_id)
    
    cart_items = session.exec(
        select(CartItem)
        .options(selectinload(CartItem.product))
        .where(CartItem.cart_id == order_data.cart_id)
    ).all()
    
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    total_price = 0
    for item in cart_items:
        if not item.product:
            raise HTTPException(status_code=404, detail=f"Product with id {item.product_id} not found")
        
        if item.product.quantity_in_stock < item.quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Not enough stock for {item.product.name}. Available: {item.product.quantity_in_stock}, Requested: {item.quantity}"
            )
        
        total_price += item.product.price * item.quantity
    
    for item in cart_items:
        product = item.product
        product.total_sold += item.quantity
        product.quantity_in_stock -= item.quantity
        session.add(product)
    
    # Create the order
    order = Order(
        cart_id=order_data.cart_id,
        customer_name=order_data.customer_name,
        customer_phone=order_data.customer_phone,
        customer_address=order_data.customer_address,
        total_price=total_price
    )
    session.add(order)
    session.commit()
    session.refresh(order)
    
    return order
