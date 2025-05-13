from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from app.core.db import get_session
from app.models.models import Product, ProductCategory
from typing import List, Optional

router = APIRouter()

@router.get("/")
def list_products(
    category_id: Optional[int] = None,
    sort_by: Optional[str] = Query("name", enum=["name", "price", "quantity_in_stock"]),
    session: Session = Depends(get_session)
):
    query = select(Product)
    if category_id:
        query = query.where(Product.category_id == category_id)
    query = query.order_by(getattr(Product, sort_by))
    return session.exec(query).all()

@router.get("/top")
def top_products(session: Session = Depends(get_session)):
    query = select(Product).order_by(Product.total_sold.desc()).limit(10)
    return session.exec(query).all()
