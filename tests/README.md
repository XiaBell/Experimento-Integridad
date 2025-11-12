# Scripts de Prueba para el Experimento de Integridad

Este directorio contiene los scripts para ejecutar las pruebas del experimento de integridad.

## Prerequisitos

1. Instalar `curl` (generalmente ya está instalado)
2. Python 3 con PyJWT instalado:
   ```bash
   pip install PyJWT
   ```

## Generar Tokens JWT de Prueba

Antes de ejecutar las pruebas, necesitas generar tokens JWT:

```bash
cd tests
python3 generate_tokens.py
```

Esto generará:
- `admin_token.txt`: Token para usuario ADMIN
- `operario_token.txt`: Token para usuario OPERARIO

Luego exporta las variables de entorno:

```bash
export ADMIN_TOKEN=$(cat admin_token.txt)
export OPERARIO_TOKEN=$(cat operario_token.txt)
export KONG_ENDPOINT=http://localhost:8000  # Ajustar según tu despliegue
export PRODUCT_ID=1  # ID del producto a eliminar
```

## Ejecutar Pruebas

### Escenario 1: Control (ADMIN - Éxito)

```bash
chmod +x test_admin.sh
./test_admin.sh
```

**Resultado Esperado:**
- Código HTTP: 204 No Content (o 200 OK)
- El producto es eliminado exitosamente

### Escenario 2: Integridad (OPERARIO - Rechazo)

```bash
chmod +x test_operario.sh
./test_operario.sh
```

**Resultado Esperado:**
- Código HTTP: 403 Forbidden
- El producto NO es eliminado
- Mensaje de error indicando falta de autorización

## Usar con Postman

1. Importar la colección de Postman (si está disponible)
2. Configurar las variables de entorno en Postman:
   - `kong_endpoint`: URL del API Gateway
   - `admin_token`: Token JWT del usuario ADMIN
   - `operario_token`: Token JWT del usuario OPERARIO
3. Ejecutar las peticiones y capturar pantallazos como evidencia

## Notas

- Los tokens generados por `generate_tokens.py` son solo para pruebas locales
- En producción, los tokens deben venir del proveedor de identidad (Auth0/Keycloak)
- Asegúrate de que el `JWT_SECRET_KEY` en `generate_tokens.py` coincida con el configurado en Django

