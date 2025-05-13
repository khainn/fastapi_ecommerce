from uuid import uuid4

from app.models import Token


class UserService(object):
    __instance = None

    @staticmethod
    def generate_token(user_id: str):
        access_jti = uuid4().hex
        refresh_jti = uuid4().hex
        payload = {
            'agent_number': user_id,
            'access_jti': access_jti,
            'refresh_jti': refresh_jti
        }
        Token.insert_token(payload)
        access_token = Token.generate_access_token(user_id, access_jti)
        refresh_token = Token.generate_refresh_token(user_id, refresh_jti)
        return access_token, refresh_token
