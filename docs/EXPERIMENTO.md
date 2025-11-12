# Documentación Detallada del Experimento de Integridad

## 1. Objetivo del Experimento

Demostrar que el sistema impide que un usuario de bajo privilegio (OPERARIO) manipule datos críticos (eliminar un producto), cumpliendo la definición de **integridad**.

## 2. ASR de Integridad

| Fuente | Ambiente | Estímulo | Respuesta | Medida de Respuesta |
|--------|----------|----------|-----------|---------------------|
| Yo como Operario de Bodega | dado que el sistema está operando correctamente y **solo tengo permisos de lectura** (`GET`) | cuando intento eliminar un producto mediante el endpoint `DELETE /products/{id}` | quiero que el sistema detecte mi **rol no autorizado** y rechace la petición | Esto debe ocurrir el **100% de las veces** y la petición debe ser rechazada con un código **403 Forbidden** en menos de **100 ms**. |

## 3. Tácticas de Arquitectura Implementadas

### 3.1 Control de Acceso (Autorización)

**Descripción**: Mecanismo que verifica el rol del usuario contra los permisos requeridos para un recurso.

**Implementación**: 
- Se implementa como un middleware (`JWTAuthenticationMiddleware`) y una clase de permisos (`IsAdminOrReadOnly`) dentro del Microservicio PRODUCTS (Django)
- Intercepta la petición antes de ejecutar la lógica de eliminación
- Ubicación: `products/middleware.py` y `products/permissions.py`

### 3.2 RBAC (Role-Based Access Control)

**Descripción**: Asignación de permisos basados en roles:
- **OPERARIO**: Solo lectura (GET)
- **ADMIN**: Lectura y escritura/eliminación (GET, POST, PUT, PATCH, DELETE)

**Implementación**:
- La lógica de Django lee el rol desde el token JWT
- El middleware extrae el rol del token y lo adjunta al objeto `request`
- La clase de permisos verifica el rol antes de permitir acciones destructivas
- Ubicación: `products/utils.py`, `products/middleware.py`, `products/permissions.py`

### 3.3 Gateway de Seguridad (Kong)

**Descripción**: Kong actúa como un punto de control inicial para la autenticación, asegurando que solo peticiones con un token válido lleguen a los microservicios.

**Implementación**:
- Kong está configurado para validar la firma del JWT usando el plugin JWT
- El servicio PRODUCTS confía en que el token es válido y solo verifica el claim de roles
- Ubicación: `kong/kong.yml`

## 4. Funcionamiento del Sistema de Integridad

### 4.1 Flujo de Petición

1. **Login (Fuera del experimento)**: 
   - El usuario (Operario o Admin) se autentica en un proveedor de identidad (Auth0/similar) 
   - Recibe un **JSON Web Token (JWT)** que incluye su rol (`OPERARIO` o `ADMIN`)

2. **Petición Crítica**: 
   - El usuario envía la petición `DELETE /products/{id}` a **Kong**
   - Incluye el JWT en el header `Authorization: Bearer <token>`

3. **Filtrado Inicial (Kong)**: 
   - Kong verifica la validez del token (firma) usando el plugin JWT
   - Si el token es válido, Kong reenvía la petición al **Microservicio PRODUCTS**

4. **Verificación de Integridad (PRODUCTS)**:
   - El middleware `JWTAuthenticationMiddleware` extrae el rol del JWT
   - El rol se adjunta al objeto `request` como `request.user_role`
   - La vista `ProductViewSet.destroy()` es llamada
   - La clase de permisos `IsAdminOrReadOnly.has_permission()` verifica el rol
   - Si el rol es `OPERARIO` y la acción es `DELETE`, se rechaza con **403 Forbidden**
   - Si el rol es `ADMIN`, se permite la eliminación

5. **Rechazo/Aceptación**: 
   - Si es OPERARIO: Kong propaga el error 403 al Operario, y el dato crítico nunca fue tocado
   - Si es ADMIN: El producto es eliminado y se devuelve 204 No Content

### 4.2 Diagrama de Flujo

```
[Usuario OPERARIO] 
    |
    | DELETE /products/123
    | Authorization: Bearer <token>
    v
[Kong Gateway]
    |
    | Valida firma JWT
    | Token válido ✓
    v
[Microservicio PRODUCTS]
    |
    | JWTAuthenticationMiddleware
    | Extrae rol: OPERARIO
    v
[IsAdminOrReadOnly.has_permission()]
    |
    | Verifica: OPERARIO != ADMIN
    | Método: DELETE (no es seguro)
    v
[❌ RECHAZO]
    |
    | 403 Forbidden
    | "Acción no autorizada. Requiere rol 'ADMIN'."
    v
[Usuario OPERARIO]
    Producto NO eliminado ✓
```

## 5. Implementación Técnica

### 5.1 Middleware de Autenticación JWT

**Archivo**: `products/middleware.py`

El middleware `JWTAuthenticationMiddleware`:
- Extrae el token del header `Authorization`
- Decodifica el token usando `extract_user_info_from_token()`
- Adjunta `request.user_role` y `request.user_info` al objeto request

### 5.2 Clase de Permisos

**Archivo**: `products/permissions.py`

La clase `IsAdminOrReadOnly`:
- Permite métodos seguros (GET, HEAD, OPTIONS) a todos los usuarios autenticados
- Requiere rol `ADMIN` para métodos destructivos (POST, PUT, PATCH, DELETE)
- Registra intentos de acceso no autorizado en los logs

### 5.3 Vista de Eliminación

**Archivo**: `products/views.py`

El método `ProductViewSet.destroy()`:
- Obtiene la instancia del producto
- La verificación de permisos ya se hizo en `has_permission()`
- Si llegamos aquí, el usuario es ADMIN (o ya se devolvió 403)
- Elimina el producto y devuelve 204 No Content
- Registra la acción en los logs para evidencias

## 6. Plan de Ejecución y Evidencias

### 6.1 Escenarios de Prueba

| Escenario | Objetivo | Rol Utilizado | Acción y Endpoint | Resultado Esperado | Código de Respuesta |
|-----------|----------|---------------|-------------------|-------------------|---------------------|
| **Control (Éxito)** | Validar que el endpoint funciona para el rol correcto | **ADMIN** | `DELETE /products/123` | Éxito, producto eliminado | **204 No Content** |
| **Integridad (Falla)** | Validar que el sistema protege el dato de la manipulación | **OPERARIO** | `DELETE /products/123` | Rechazo, producto no eliminado | **403 Forbidden** |

### 6.2 Métricas a Medir

| Métrica | Valor Objetivo | Cómo Medir |
|---------|----------------|------------|
| Tasa de Rechazo (OPERARIO) | 100% | Verificar que todas las peticiones DELETE de OPERARIO retornen 403 |
| Código de Respuesta | 403 Forbidden | Verificar código HTTP en la respuesta |
| Latencia de Rechazo | < 100 ms | Medir tiempo desde la petición hasta la respuesta 403 |

### 6.3 Evidencias a Capturar

1. **Evidencia del Rol ADMIN (Éxito)**: 
   - Pantallazo de Postman mostrando la petición `DELETE` con el token JWT del rol ADMIN
   - Respuesta **204 No Content** (o 200 OK)
   - Log de Django mostrando eliminación exitosa

2. **Evidencia del Rol OPERARIO (Rechazo)**: 
   - Pantallazo de Postman mostrando la petición `DELETE` con el token JWT del rol OPERARIO
   - Respuesta **403 Forbidden**
   - Mensaje de error: "Acción no autorizada. Requiere rol 'ADMIN'."
   - Log de Django mostrando el rechazo sin intentar consulta a la DB

3. **Log de la Consola de Django**: 
   - Log mostrando que se detectó el rol OPERARIO
   - Log mostrando que se devolvió el 403 sin intentar la eliminación
   - Verificar que NO hay consultas SQL de DELETE en los logs

## 7. Análisis de Resultados

### 7.1 Resultados Esperados

| Métrica | Valor Obtenido (Ejemplo) | Cumplimiento | Conclusión |
|---------|-------------------------|--------------|------------|
| Tasa de Rechazo (OPERARIO) | 100% | Sí | La acción destructiva fue rechazada el 100% de las veces |
| Código de Respuesta | 403 Forbidden | Sí | El sistema devolvió el código de error de autorización correcto, no un error 500 |
| Latencia de Rechazo | 55 ms | Sí | La verificación de permisos es rápida, asegurando que la Integridad no comprometa la latencia |

### 7.2 Conclusión del ASR

El experimento valida de forma concluyente que la táctica de **Control de Acceso (RBAC)** implementada en el Microservicio PRODUCTS satisface el ASR de Integridad, rechazando de forma rápida y categórica cualquier intento de manipulación no autorizada por parte del rol Operario.

## 8. Instrucciones de Despliegue

Ver `README.md` en la raíz del proyecto para instrucciones completas de despliegue.

## 9. Troubleshooting

### Problema: Token JWT no se decodifica correctamente

**Solución**: Verificar que `JWT_SECRET_KEY` en Django coincida con la clave usada para firmar el token.

### Problema: Kong rechaza todas las peticiones

**Solución**: Verificar que el plugin JWT esté habilitado y configurado correctamente en Kong.

### Problema: OPERARIO puede eliminar productos

**Solución**: Verificar que el middleware esté activo y que la clase de permisos esté correctamente configurada en la vista.

