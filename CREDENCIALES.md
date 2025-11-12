# 🔐 Credenciales de Acceso - Experimento de Integridad

Este documento contiene las credenciales de prueba para el experimento de integridad.

## 👤 Usuarios de Prueba

### 🔴 ADMIN (Administrador)
- **Usuario:** `admin`
- **Contraseña:** `admin123`
- **Rol:** `ADMIN`
- **Permisos:** 
  - ✅ Ver productos
  - ✅ Crear productos
  - ✅ Modificar productos
  - ✅ **Eliminar productos** (acción crítica del experimento)

### 🟡 OPERARIO (Operario de Bodega)
- **Usuario:** `operario`
- **Contraseña:** `operario123`
- **Rol:** `OPERARIO`
- **Permisos:**
  - ✅ Ver productos
  - ❌ Crear productos
  - ❌ Modificar productos
  - ❌ **Eliminar productos** (debe ser rechazado con 403)

## 📝 Notas

- Estas credenciales son solo para pruebas del experimento
- En producción, los usuarios vendrían de un proveedor de identidad (Auth0, Keycloak, etc.)
- Los tokens JWT generados son válidos por 24 horas
- Las credenciales están hardcodeadas en `products/auth_views.py` para facilitar las pruebas


