from functools import wraps

from sqlalchemy.orm import Session

from .db import SessionLocal


def transaction():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            db: Session = SessionLocal()
            try:
                result = func(db, *args, **kwargs)
                db.commit()
                return result
            except Exception as e:
                db.rollback()
                raise e
            finally:
                db.close()

        return wrapper

    return decorator
