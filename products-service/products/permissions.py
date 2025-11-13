from rest_framework import permissions
import logging

logger = logging.getLogger(__name__)


class IsAuthenticatedJWT(permissions.BasePermission):
    
    def has_permission(self, request, view):
        user_info = getattr(request, 'user_info', None)
        
        if not user_info:
            logger.warning(f"Acceso denegado: Usuario no autenticado intentó realizar {request.method}")
            return False
        
        return True


class IsAdminOrReadOnly(permissions.BasePermission):
    
    def has_permission(self, request, view):
        user_role = getattr(request, 'user_role', None)
        user_info = getattr(request, 'user_info', None)
        
        if not user_info:
            logger.warning(f"Acceso denegado: Usuario no autenticado intentó realizar {request.method}")
            return False
        
        if request.method in permissions.SAFE_METHODS:
            logger.info(f"Acceso autorizado: Usuario autenticado con rol '{user_role}' puede realizar {request.method}")
            return True
        
        if user_role == 'ADMIN':
            logger.info(f"Acceso autorizado: Usuario ADMIN puede realizar {request.method}")
            return True
        
        logger.warning(
            f"Acceso denegado: Usuario con rol '{user_role}' intentó realizar {request.method}. "
            f"Se requiere rol 'ADMIN'."
        )
        return False


class IsAdmin(permissions.BasePermission):
    
    def has_permission(self, request, view):
        user_role = getattr(request, 'user_role', None)
        
        if user_role == 'ADMIN':
            logger.info(f"Acceso autorizado: Usuario ADMIN")
            return True
        
        logger.warning(
            f"Acceso denegado: Usuario con rol '{user_role}' intentó acceder. "
            f"Se requiere rol 'ADMIN'."
        )
        return False

