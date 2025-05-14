import shutil
from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Header
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.core.db import get_session
from app.models.models import Product, ProductCategory, Order, CartItem
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.schemas.category import ProductCategoryCreate, ProductCategoryUpdate, ProductCategoryResponse
from app.schemas.order import OrderResponse
from app.common.enums import OrderStatus

router = APIRouter()

def verify_admin(x_api_key: str = Header(...)):
    if x_api_key != "admin-secret":
        raise HTTPException(status_code=401, detail="Unauthorized")

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

@router.post("/product", response_model=ProductResponse, dependencies=[Depends(verify_admin)])
def create_product(product: ProductCreate, session: Session = Depends(get_session)):
    get_category_or_404(session, product.category_id)
    
    db_product = Product(**product.model_dump())
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product

@router.put("/product/{id}", response_model=ProductResponse, dependencies=[Depends(verify_admin)])
def update_product(id: int, data: ProductUpdate, session: Session = Depends(get_session)):
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

@router.delete("/product/{id}", dependencies=[Depends(verify_admin)])
def delete_product(id: int, session: Session = Depends(get_session)):
    db_product = session.get(Product, id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    session.delete(db_product)
    session.commit()
    return {"message": "Product deleted successfully"}

@router.post("/product/{id}/image", dependencies=[Depends(verify_admin)])
def upload_image(id: int, file: UploadFile = File(...), session: Session = Depends(get_session)):
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
@router.post("/category", response_model=ProductCategoryResponse, dependencies=[Depends(verify_admin)])
def create_category(category: ProductCategoryCreate, session: Session = Depends(get_session)):
    db_category = ProductCategory(**category.model_dump())
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category

@router.put("/category/{id}", response_model=ProductCategoryResponse, dependencies=[Depends(verify_admin)])
def update_category(id: int, cat: ProductCategoryUpdate, session: Session = Depends(get_session)):
    db_cat = session.get(ProductCategory, id)
    if not db_cat:
        raise HTTPException(status_code=404, detail="Category not found")
    for field, value in cat.model_dump(exclude_unset=True).items():
        setattr(db_cat, field, value)
    session.commit()
    session.refresh(db_cat)
    return db_cat

@router.delete("/category/{id}", dependencies=[Depends(verify_admin)])
def delete_category(id: int, session: Session = Depends(get_session)):
    db_cat = session.get(ProductCategory, id)
    if not db_cat:
        raise HTTPException(status_code=404, detail="Category not found")
    session.delete(db_cat)
    session.commit()
    return {"message": "Category deleted successfully"}

# Admin endpoints for order management
@router.get("/orders", response_model=List[OrderResponse])
def admin_list_all_orders(session: Session = Depends(get_session)):
    """Admin endpoint to list all orders."""
    orders = session.exec(select(Order)).all()
    return orders

@router.get("/orders/{order_id}/details", response_model=OrderResponse)
def admin_get_order_details(order_id: int, session: Session = Depends(get_session)):
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
def admin_search_orders(
    customer_name: str = None,
    customer_phone: str = None,
    session: Session = Depends(get_session)
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
def admin_get_revenue(session: Session = Depends(get_session)):
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
def admin_update_order_status(
    order_id: int, 
    status: OrderStatus,
    session: Session = Depends(get_session)
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
def admin_delete_order(order_id: int, session: Session = Depends(get_session)):
    """Admin endpoint to delete an order (for testing/cleanup purposes)."""
    order = get_order_or_404(session, order_id)
    session.delete(order)
    session.commit()
    return {"message": "Order deleted successfully"}
