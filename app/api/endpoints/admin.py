import shutil

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Header
from sqlmodel import Session
from app.core.db import get_session
from app.models.models import Product, ProductCategory
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.schemas.category import ProductCategoryCreate, ProductCategoryUpdate, ProductCategoryResponse

router = APIRouter()

def verify_admin(x_api_key: str = Header(...)):
    if x_api_key != "admin-secret":
        raise HTTPException(status_code=401, detail="Unauthorized")

def get_category_or_404(session: Session, category_id: int) -> ProductCategory:
    category = session.get(ProductCategory, category_id)
    if not category:
        raise HTTPException(status_code=404, detail=f"Category with id {category_id} not found")
    return category

@router.post("/product", response_model=ProductResponse, dependencies=[Depends(verify_admin)])
def create_product(product: ProductCreate, session: Session = Depends(get_session)):
    # Check if category exists
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
    
    # Check if new category exists if category_id is being updated
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
