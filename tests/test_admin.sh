#!/bin/bash

# Script de prueba para el escenario de control (ADMIN)
# Este script prueba que un usuario ADMIN puede eliminar productos

set -e

# Configuración
KONG_ENDPOINT="${KONG_ENDPOINT:-http://localhost:8000}"
PRODUCT_ID="${PRODUCT_ID:-1}"

# Token JWT para usuario ADMIN
# NOTA: En producción, este token vendría del proveedor de identidad (Auth0/Keycloak)
# Para pruebas, puedes generar un token usando jwt.io o un script Python
ADMIN_TOKEN="${ADMIN_TOKEN:-your-admin-jwt-token-here}"

echo "=========================================="
echo "Prueba de Control: ADMIN eliminando producto"
echo "=========================================="
echo ""
echo "Endpoint: ${KONG_ENDPOINT}/products/${PRODUCT_ID}"
echo "Método: DELETE"
echo "Rol: ADMIN"
echo ""

# Realizar petición DELETE
response=$(curl -s -w "\n%{http_code}" -X DELETE \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -H "Content-Type: application/json" \
  "${KONG_ENDPOINT}/products/${PRODUCT_ID}")

# Separar cuerpo de respuesta y código HTTP
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

echo "Código de Respuesta HTTP: ${http_code}"
echo "Cuerpo de Respuesta: ${body}"
echo ""

# Verificar resultado esperado
if [ "$http_code" -eq 204 ] || [ "$http_code" -eq 200 ]; then
    echo "✅ ÉXITO: Producto eliminado correctamente"
    echo "✅ El sistema permitió la acción destructiva al usuario ADMIN"
    exit 0
else
    echo "❌ FALLO: Se esperaba código 204 o 200, se obtuvo ${http_code}"
    exit 1
fi

