from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.core.db import get_session
from app.models.models import Cart, CartItem, Product
from app.schemas.cart import (
    CartResponse,
    CartItemCreate,
    CartItemUpdate,
    CartItemResponse,
    CartCreate
)
from uuid import UUID
from typing import List

router = APIRouter()

def get_cart_or_404(session: Session, cart_id: UUID) -> Cart:
    cart = session.get(Cart, cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail=f"Cart with id {cart_id} not found")
    return cart

def get_cart_item_or_404(session: Session, item_id: int) -> CartItem:
    item = session.get(CartItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Cart item with id {item_id} not found")
    return item

def get_product_or_404(session: Session, product_id: int) -> Product:
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found")
    return product

@router.post("/", response_model=CartResponse)
def create_cart(session: Session = Depends(get_session)):
    """Create a new cart. The cart_id will be auto-generated as UUID."""
    db_cart = Cart()
    session.add(db_cart)
    session.commit()
    session.refresh(db_cart)
    return db_cart

@router.post("/{cart_id}/items", response_model=CartItemResponse)
def add_to_cart(
    cart_id: UUID,
    item: CartItemCreate,
    session: Session = Depends(get_session)
):
    """Add an item to an existing cart. If item exists, increment quantity."""
    get_cart_or_404(session, cart_id)
    product = get_product_or_404(session, item.product_id)
    
    existing_item = session.exec(
        select(CartItem).where(
            CartItem.cart_id == cart_id,
            CartItem.product_id == item.product_id
        )
    ).first()
    
    if existing_item:
        new_quantity = existing_item.quantity + item.quantity
        if product.quantity_in_stock < new_quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock. Available: {product.quantity_in_stock}, Current in cart: {existing_item.quantity}"
            )
        
        existing_item.quantity = new_quantity
        session.commit()
        session.refresh(existing_item)
        return existing_item
    
    if product.quantity_in_stock < item.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough stock. Available: {product.quantity_in_stock}"
        )
    
    db_item = CartItem(
        cart_id=cart_id,
        product_id=item.product_id,
        quantity=item.quantity
    )
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

@router.get("/{cart_id}/items", response_model=List[CartItemResponse])
def list_cart_items(cart_id: UUID, session: Session = Depends(get_session)):
    """Get all items in a cart with their product information."""
    get_cart_or_404(session, cart_id)
    
    # Get cart items with product information using relationship
    statement = (
        select(CartItem)
        .options(selectinload(CartItem.product))
        .where(CartItem.cart_id == cart_id)
    )
    items = session.exec(statement).all()
    return items

@router.put("/items/{item_id}", response_model=CartItemResponse)
def update_cart_item(
    item_id: int,
    item_update: CartItemUpdate,
    session: Session = Depends(get_session)
):
    """Update quantity of an item in the cart."""
    # Get item with product using relationship
    statement = (
        select(CartItem)
        .options(selectinload(CartItem.product))
        .where(CartItem.id == item_id)
    )
    db_item = session.exec(statement).first()
    if not db_item:
        raise HTTPException(status_code=404, detail=f"Cart item with id {item_id} not found")
    
    if db_item.product.quantity_in_stock < item_update.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough stock. Available: {db_item.product.quantity_in_stock}"
        )
    
    db_item.quantity = item_update.quantity
    session.commit()
    session.refresh(db_item)
    return db_item

@router.delete("/items/{item_id}")
def delete_cart_item(item_id: int, session: Session = Depends(get_session)):
    """Remove an item from the cart."""
    db_item = get_cart_item_or_404(session, item_id)
    session.delete(db_item)
    session.commit()
    return {"message": "Cart item deleted successfully"}
