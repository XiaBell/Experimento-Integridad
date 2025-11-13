import jwt
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def decode_jwt_token(token):
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token JWT expirado")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Token JWT inválido: {e}")
        return None
    except Exception as e:
        logger.error(f"Error al decodificar token JWT: {e}")
        return None


def extract_role_from_token(token):
    payload = decode_jwt_token(token)
    if payload:
        role = payload.get('role') or payload.get('roles') or payload.get('http://schemas.microsoft.com/ws/2008/06/identity/claims/role')
        if isinstance(role, list) and len(role) > 0:
            role = role[0]
        return role
    return None


def extract_user_info_from_token(token):
    payload = decode_jwt_token(token)
    if payload:
        return {
            'username': payload.get('sub') or payload.get('username') or payload.get('email'),
            'role': extract_role_from_token(token),
            'email': payload.get('email'),
            'user_id': payload.get('sub') or payload.get('user_id'),
        }
    return None

