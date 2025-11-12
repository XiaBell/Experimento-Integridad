"""
Utilidades para manejo de JWT y extracción de información del usuario.
"""
import jwt
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def decode_jwt_token(token):
    """
    Decodifica un token JWT y retorna el payload.
    
    Args:
        token: String del token JWT (sin el prefijo 'Bearer ')
    
    Returns:
        dict: Payload del token decodificado, o None si hay error
    """
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
    """
    Extrae el rol del usuario desde el token JWT.
    
    Args:
        token: String del token JWT (sin el prefijo 'Bearer ')
    
    Returns:
        str: Rol del usuario ('ADMIN' o 'OPERARIO'), o None si no se encuentra
    """
    payload = decode_jwt_token(token)
    if payload:
        # El rol puede estar en diferentes claims según el proveedor de identidad
        role = payload.get('role') or payload.get('roles') or payload.get('http://schemas.microsoft.com/ws/2008/06/identity/claims/role')
        if isinstance(role, list) and len(role) > 0:
            role = role[0]
        return role
    return None


def extract_user_info_from_token(token):
    """
    Extrae información completa del usuario desde el token JWT.
    
    Args:
        token: String del token JWT (sin el prefijo 'Bearer ')
    
    Returns:
        dict: Información del usuario (username, role, etc.)
    """
    payload = decode_jwt_token(token)
    if payload:
        return {
            'username': payload.get('sub') or payload.get('username') or payload.get('email'),
            'role': extract_role_from_token(token),
            'email': payload.get('email'),
            'user_id': payload.get('sub') or payload.get('user_id'),
        }
    return None

