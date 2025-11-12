#!/usr/bin/env python3
"""
Script para generar tokens JWT de prueba para los roles ADMIN y OPERARIO.
Esto es solo para pruebas locales. En producción, los tokens vendrían del proveedor de identidad.
"""

import jwt
import json
from datetime import datetime, timedelta

# Configuración
JWT_SECRET_KEY = "your-secret-key-change-in-production"  # Debe coincidir con JWT_SECRET_KEY en Django
JWT_ALGORITHM = "HS256"

def generate_token(role, username, expiration_hours=24):
    """
    Genera un token JWT con el rol especificado.
    
    Args:
        role: Rol del usuario ('ADMIN' o 'OPERARIO')
        username: Nombre de usuario
        expiration_hours: Horas hasta la expiración del token
    
    Returns:
        str: Token JWT codificado
    """
    payload = {
        'sub': username,
        'username': username,
        'role': role,
        'email': f'{username}@warehouse.com',
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(hours=expiration_hours),
    }
    
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

if __name__ == "__main__":
    # Generar token para ADMIN
    admin_token = generate_token('ADMIN', 'admin-user')
    print("=" * 60)
    print("TOKEN JWT PARA ADMIN")
    print("=" * 60)
    print(admin_token)
    print()
    
    # Generar token para OPERARIO
    operario_token = generate_token('OPERARIO', 'operario-user')
    print("=" * 60)
    print("TOKEN JWT PARA OPERARIO")
    print("=" * 60)
    print(operario_token)
    print()
    
    # Guardar tokens en archivos para uso en scripts de prueba
    with open('admin_token.txt', 'w') as f:
        f.write(admin_token)
    
    with open('operario_token.txt', 'w') as f:
        f.write(operario_token)
    
    print("✅ Tokens guardados en admin_token.txt y operario_token.txt")
    print()
    print("Para usar en los scripts de prueba:")
    print("  export ADMIN_TOKEN=$(cat admin_token.txt)")
    print("  export OPERARIO_TOKEN=$(cat operario_token.txt)")

