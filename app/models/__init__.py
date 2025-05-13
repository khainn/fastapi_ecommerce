# Import all the models, so that Base has them before being
# imported by Alembic
from app.models.models import Product, ProductCategory, Cart, CartItem, Order  # noqa
