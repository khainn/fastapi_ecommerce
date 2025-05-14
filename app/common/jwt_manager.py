import jwt as PyJWT
from datetime import datetime, timedelta


class JWTManager:

    @staticmethod
    def create_token(payload: dict, secret_key: str, algorithm: str = 'HS256') -> str:
        token = PyJWT.encode(payload, secret_key, algorithm=algorithm)
        return token

    @staticmethod
    def decode_token(token: str, secret_key: str, algorithms: list = ['HS256']) -> dict:
        try:
            payload = PyJWT.decode(token, secret_key, algorithms=algorithms)
            return payload
        except PyJWT.ExpiredSignatureError:
            raise Exception("Token has expired")
        except PyJWT.InvalidTokenError:
            raise Exception("Invalid token")
