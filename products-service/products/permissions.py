"""
Clases de permisos para control de acceso basado en roles (RBAC).
"""
from rest_framework import permissions
import logging

logger = logging.getLogger(__name__)


class IsAuthenticatedJWT(permissions.BasePermission):
    """
    Permiso que verifica autenticación mediante JWT (user_info del middleware).
    Reemplaza IsAuthenticated de DRF para trabajar con JWT personalizado.
    """
    
    def has_permission(self, request, view):
        """
        Verifica si el usuario está autenticado mediante JWT.
        """
        user_info = getattr(request, 'user_info', None)
        
        if not user_info:
            logger.warning(f"Acceso denegado: Usuario no autenticado intentó realizar {request.method}")
            return False
        
        return True


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permiso que permite:
    - Lectura (GET) a todos los usuarios autenticados
    - Escritura/Eliminación (POST, PUT, PATCH, DELETE) solo a ADMIN
    """
    
    def has_permission(self, request, view):
        """
        Verifica si el usuario tiene permiso para realizar la acción.
        """
        user_role = getattr(request, 'user_role', None)
        user_info = getattr(request, 'user_info', None)
        
        # Verificar que el usuario esté autenticado (tenga token válido)
        if not user_info:
            logger.warning(f"Acceso denegado: Usuario no autenticado intentó realizar {request.method}")
            return False
        
        # Permitir métodos de lectura a todos los usuarios autenticados
        if request.method in permissions.SAFE_METHODS:
            logger.info(f"Acceso autorizado: Usuario autenticado con rol '{user_role}' puede realizar {request.method}")
            return True
        
        # Para métodos de escritura, verificar que el usuario sea ADMIN
        if user_role == 'ADMIN':
            logger.info(f"Acceso autorizado: Usuario ADMIN puede realizar {request.method}")
            return True
        
        logger.warning(
            f"Acceso denegado: Usuario con rol '{user_role}' intentó realizar {request.method}. "
            f"Se requiere rol 'ADMIN'."
        )
        return False


class IsAdmin(permissions.BasePermission):
    """
    Permiso que solo permite acceso a usuarios con rol ADMIN.
    """
    
    def has_permission(self, request, view):
        """
        Verifica si el usuario tiene rol ADMIN.
        """
        user_role = getattr(request, 'user_role', None)
        
        if user_role == 'ADMIN':
            logger.info(f"Acceso autorizado: Usuario ADMIN")
            return True
        
        logger.warning(
            f"Acceso denegado: Usuario con rol '{user_role}' intentó acceder. "
            f"Se requiere rol 'ADMIN'."
        )
        return False

