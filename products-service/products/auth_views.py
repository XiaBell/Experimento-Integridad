from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import jwt
import logging
from datetime import datetime, timedelta
from django.conf import settings

logger = logging.getLogger(__name__)

TEST_USERS = {
    'admin': {
        'password': 'admin123',
        'role': 'ADMIN',
        'username': 'admin',
        'email': 'admin@warehouse.com'
    },
    'operario': {
        'password': 'operario123',
        'role': 'OPERARIO',
        'username': 'operario',
        'email': 'operario@warehouse.com'
    }
}


def generate_jwt_token(user_data):
    payload = {
        'sub': user_data['username'],
        'username': user_data['username'],
        'role': user_data['role'],
        'email': user_data['email'],
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(hours=24),
    }
    
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username', '').lower()
    password = request.data.get('password', '')
    
    if not username or not password:
        return Response(
            {"detail": "Usuario y contraseña son requeridos"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user_data = TEST_USERS.get(username)
    
    if not user_data or user_data['password'] != password:
        logger.warning(f"Intento de login fallido para usuario: {username}")
        return Response(
            {"detail": "Credenciales inválidas"},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    token = generate_jwt_token(user_data)
    
    logger.info(f"Login exitoso para usuario: {username} con rol: {user_data['role']}")
    
    return Response({
        "token": token,
        "user": {
            "username": user_data['username'],
            "role": user_data['role'],
            "email": user_data['email']
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def test_users(request):
    return Response({
        "message": "Credenciales de prueba para el experimento",
        "users": {
            "admin": {
                "username": "admin",
                "password": "admin123",
                "role": "ADMIN"
            },
            "operario": {
                "username": "operario",
                "password": "operario123",
                "role": "OPERARIO"
            }
        }
    }, status=status.HTTP_200_OK)

