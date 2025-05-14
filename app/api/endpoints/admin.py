import shutil
from typing import List
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Header, Security
from fastapi.security import APIKeyHeader
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.core.db import get_session
from app.core.config import settings
from app.models.models import Product, ProductCategory, Order, CartItem
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.schemas.category import ProductCategoryCreate, ProductCategoryUpdate, ProductCategoryResponse
from app.schemas.order import OrderResponse
from app.schemas.admin import AdminLogin, AdminToken
from app.common.enums import OrderStatus
from app.common.jwt_manager import JWTManager

router = APIRouter()

# Define API key header
api_key_header = APIKeyHeader(name="Authorization", auto_error=True)

async def verify_admin(authorization: str = Security(api_key_header)):
    try:
        # Remove 'Bearer ' prefix if present
        token = authorization.replace('Bearer ', '') if authorization.startswith('Bearer ') else authorization
        payload = JWTManager.decode_token(token, settings.SECRET_KEY)
        if payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

@router.post("/login", response_model=AdminToken)
async def admin_login(login_data: AdminLogin):
    if login_data.username != settings.ADMIN_USERNAME or login_data.password != settings.ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    payload = {
        "sub": login_data.username,
        "role": "admin",
        "exp": datetime.utcnow() + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    }
    
    access_token = JWTManager.create_token(payload, settings.SECRET_KEY)
    return {"access_token": access_token, "token_type": "bearer"}

def get_category_or_404(session: Session, category_id: int) -> ProductCategory:
    category = session.get(ProductCategory, category_id)
    if not category:
        raise HTTPException(status_code=404, detail=f"Category with id {category_id} not found")
    return category

def get_order_or_404(session: Session, order_id: int) -> Order:
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order with id {order_id} not found")
    return order

@router.post("/product", response_model=ProductResponse)
async def create_product(
    product: ProductCreate, 
    session: Session = Depends(get_session),
    _: dict = Depends(verify_admin)
):
    get_category_or_404(session, product.category_id)
    
    db_product = Product(**product.model_dump())
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product

@router.put("/product/{id}", response_model=ProductResponse)
async def update_product(
    id: int, 
    data: ProductUpdate, 
    session: Session = Depends(get_session),
    _: dict = Depends(verify_admin)
):
    db_product = session.get(Product, id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if data.category_id is not None:
        get_category_or_404(session, data.category_id)
    
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(db_product, field, value)
    session.commit()
    session.refresh(db_product)
    return db_product

@router.delete("/product/{id}")
async def delete_product(
    id: int, 
    session: Session = Depends(get_session),
    _: dict = Depends(verify_admin)
):
    db_product = session.get(Product, id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    session.delete(db_product)
    session.commit()
    return {"message": "Product deleted successfully"}

@router.post("/product/{id}/image")
async def upload_image(
    id: int, 
    file: UploadFile = File(...), 
    session: Session = Depends(get_session),
    _: dict = Depends(verify_admin)
):
    db_product = session.get(Product, id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    path = f"static/{file.filename}"
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    db_product.image_url = path
    session.commit()
    return {"image_url": path}

# Category
@router.post("/category", response_model=ProductCategoryResponse)
async def create_category(
    category: ProductCategoryCreate, 
    session: Session = Depends(get_session),
    _: dict = Depends(verify_admin)
):
    db_category = ProductCategory(**category.model_dump())
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category

@router.put("/category/{id}", response_model=ProductCategoryResponse)
async def update_category(
    id: int, 
    cat: ProductCategoryUpdate, 
    session: Session = Depends(get_session),
    _: dict = Depends(verify_admin)
):
    db_cat = session.get(ProductCategory, id)
    if not db_cat:
        raise HTTPException(status_code=404, detail="Category not found")
    for field, value in cat.model_dump(exclude_unset=True).items():
        setattr(db_cat, field, value)
    session.commit()
    session.refresh(db_cat)
    return db_cat

@router.delete("/category/{id}")
async def delete_category(
    id: int, 
    session: Session = Depends(get_session),
    _: dict = Depends(verify_admin)
):
    db_cat = session.get(ProductCategory, id)
    if not db_cat:
        raise HTTPException(status_code=404, detail="Category not found")
    session.delete(db_cat)
    session.commit()
    return {"message": "Category deleted successfully"}

# Admin endpoints for order management
@router.get("/orders", response_model=List[OrderResponse])
async def admin_list_all_orders(
    session: Session = Depends(get_session),
    _: dict = Depends(verify_admin)
):
    """Admin endpoint to list all orders."""
    orders = session.exec(select(Order)).all()
    return orders

@router.get("/orders/{order_id}/details", response_model=OrderResponse)
async def admin_get_order_details(
    order_id: int, 
    session: Session = Depends(get_session),
    _: dict = Depends(verify_admin)
):
    """Admin endpoint to get order details including cart items."""
    order = get_order_or_404(session, order_id)
    
    # Get cart items for this order
    cart_items = session.exec(
        select(CartItem)
        .options(selectinload(CartItem.product))
        .where(CartItem.cart_id == order.cart_id)
    ).all()
    
    # Create response with cart items
    order_dict = order.model_dump()
    order_dict['cart_items'] = cart_items
    
    return order_dict

@router.get("/orders/search", response_model=List[OrderResponse])
async def admin_search_orders(
    customer_name: str = None,
    customer_phone: str = None,
    session: Session = Depends(get_session),
    _: dict = Depends(verify_admin)
):
    """Admin endpoint to search orders by customer details."""
    statement = select(Order)
    
    if customer_name:
        statement = statement.where(Order.customer_name.ilike(f"%{customer_name}%"))
    
    if customer_phone:
        statement = statement.where(Order.customer_phone.ilike(f"%{customer_phone}%"))
    
    orders = session.exec(statement).all()
    return orders

@router.get("/orders/revenue", response_model=dict)
async def admin_get_revenue(
    session: Session = Depends(get_session),
    _: dict = Depends(verify_admin)
):
    """Admin endpoint to get total revenue and order statistics."""
    orders = session.exec(select(Order)).all()
    
    total_revenue = sum(order.total_price for order in orders)
    total_orders = len(orders)
    average_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    return {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "average_order_value": average_order_value
    }

@router.put("/orders/{order_id}/status", response_model=OrderResponse)
async def admin_update_order_status(
    order_id: int, 
    status: OrderStatus,
    session: Session = Depends(get_session),
    _: dict = Depends(verify_admin)
):
    """Admin endpoint to update the status of an order."""
    order = get_order_or_404(session, order_id)
    
    # Update the order status
    order.status = status.value
    session.add(order)
    session.commit()
    session.refresh(order)
    
    return order

@router.delete("/orders/{order_id}")
async def admin_delete_order(
    order_id: int, 
    session: Session = Depends(get_session),
    _: dict = Depends(verify_admin)
):
    """Admin endpoint to delete an order (for testing/cleanup purposes)."""
    order = get_order_or_404(session, order_id)
    session.delete(order)
    session.commit()
    return {"message": "Order deleted successfully"}
