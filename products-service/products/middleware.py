import logging
from django.utils.deprecation import MiddlewareMixin
from products.utils import extract_user_info_from_token

logger = logging.getLogger(__name__)


class JWTAuthenticationMiddleware(MiddlewareMixin):
    
    def process_request(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Bearer '):
            request.user_info = None
            request.user_role = None
            return None
        
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

