"""
Middleware personalizado para autenticación JWT.
Este middleware extrae el token JWT del header Authorization y adjunta
la información del usuario al objeto request.
"""
import logging
from django.utils.deprecation import MiddlewareMixin
from products.utils import extract_user_info_from_token

logger = logging.getLogger(__name__)


class JWTAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware que procesa el token JWT del header Authorization
    y adjunta la información del usuario al request.
    
    Asume que Kong ya validó la firma del token, por lo que solo
    extraemos la información del usuario (especialmente el rol).
    """
    
    def process_request(self, request):
        """
        Procesa la petición para extraer información del JWT.
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Bearer '):
            # Si no hay token, el request.user.role será None
            # y las vistas con permisos lo manejarán
            request.user_info = None
            request.user_role = None
            return None
        
        # Extraer el token (remover 'Bearer ')
        token = auth_header.split(' ')[1] if len(auth_header.split(' ')) > 1 else None
        
        if token:
            user_info = extract_user_info_from_token(token)
            if user_info:
                request.user_info = user_info
                request.user_role = user_info.get('role')
                logger.info(f"Usuario autenticado: {user_info.get('username')} con rol: {request.user_role}")
            else:
                request.user_info = None
                request.user_role = None
        else:
            request.user_info = None
            request.user_role = None
        
        return None

