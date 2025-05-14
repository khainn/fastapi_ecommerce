from enum import Enum


class UserRole(Enum):
    ADMIN = 'admin'
    GUEST = 'guest'

class OrderStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
