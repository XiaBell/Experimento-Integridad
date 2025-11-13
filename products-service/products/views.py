"""
Vistas del API para gestión de productos.
Implementa control de acceso basado en roles (RBAC) para garantizar integridad.
"""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
import logging

from products.models import Product
from products.serializers import ProductSerializer
from products.permissions import IsAdminOrReadOnly

logger = logging.getLogger(__name__)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar productos.
    
    Implementa la táctica de Control de Acceso (RBAC):
    - OPERARIO: Solo lectura (GET)
    - ADMIN: Lectura y escritura/eliminación (GET, POST, PUT, PATCH, DELETE)
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    def get_queryset(self):
        """
        Retorna el queryset de productos.
        """
        return Product.objects.all()
    
    def destroy(self, request, *args, **kwargs):
        """
        Elimina un producto.
        
        Esta es la acción crítica que el experimento de integridad protege.
        Solo usuarios con rol ADMIN pueden eliminar productos.
        
        La verificación de permisos se realiza en IsAdminOrReadOnly,
        que rechazará la petición con 403 si el usuario no es ADMIN.
        """
        instance = self.get_object()
        user_role = getattr(request, 'user_role', None)
        user_info = getattr(request, 'user_info', {})
        username = user_info.get('username', 'unknown') if user_info else 'unknown'
        
        # Log para evidencias del experimento
        logger.info(
            f"Intento de eliminación de producto ID={instance.id} "
            f"por usuario '{username}' con rol '{user_role}'"
        )
        
        # La verificación de permisos ya se hizo en IsAdminOrReadOnly.has_permission()
        # Si llegamos aquí, el usuario es ADMIN (o el permiso falló y se devolvió 403)
        
        try:
            product_id = instance.id
            product_name = instance.name
            self.perform_destroy(instance)
            
            logger.info(
                f"Producto eliminado exitosamente: ID={product_id}, Name={product_name} "
                f"por usuario ADMIN '{username}'"
            )
            
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            logger.error(f"Error al eliminar producto: {e}")
            return Response(
                {"detail": f"Error al eliminar producto: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def list(self, request, *args, **kwargs):
        """
        Lista todos los productos (máximo 20 para el frontend).
        Disponible para todos los usuarios autenticados (OPERARIO y ADMIN).
        """
        response = super().list(request, *args, **kwargs)
        # Limitar a 20 productos como se solicitó
        if isinstance(response.data, list):
            response.data = response.data[:20]
        return response
    
    def retrieve(self, request, *args, **kwargs):
        """
        Obtiene un producto específico.
        Disponible para todos los usuarios autenticados (OPERARIO y ADMIN).
        """
        return super().retrieve(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        """
        Crea un nuevo producto.
        Solo disponible para usuarios con rol ADMIN.
        """
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """
        Actualiza un producto.
        Solo disponible para usuarios con rol ADMIN.
        """
        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        """
        Actualiza parcialmente un producto.
        Solo disponible para usuarios con rol ADMIN.
        """
        return super().partial_update(request, *args, **kwargs)

