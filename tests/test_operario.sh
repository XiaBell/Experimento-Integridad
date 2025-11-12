#!/bin/bash

# Script de prueba para el escenario de integridad (OPERARIO)
# Este script prueba que un usuario OPERARIO NO puede eliminar productos

set -e

# Configuración
KONG_ENDPOINT="${KONG_ENDPOINT:-http://localhost:8000}"
PRODUCT_ID="${PRODUCT_ID:-1}"

# Token JWT para usuario OPERARIO
# NOTA: En producción, este token vendría del proveedor de identidad (Auth0/Keycloak)
# Para pruebas, puedes generar un token usando jwt.io o un script Python
OPERARIO_TOKEN="${OPERARIO_TOKEN:-your-operario-jwt-token-here}"

echo "=========================================="
echo "Prueba de Integridad: OPERARIO intentando eliminar producto"
echo "=========================================="
echo ""
echo "Endpoint: ${KONG_ENDPOINT}/products/${PRODUCT_ID}"
echo "Método: DELETE"
echo "Rol: OPERARIO"
echo ""

# Realizar petición DELETE
response=$(curl -s -w "\n%{http_code}" -X DELETE \
  -H "Authorization: Bearer ${OPERARIO_TOKEN}" \
  -H "Content-Type: application/json" \
  "${KONG_ENDPOINT}/products/${PRODUCT_ID}")

# Separar cuerpo de respuesta y código HTTP
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

echo "Código de Respuesta HTTP: ${http_code}"
echo "Cuerpo de Respuesta: ${body}"
echo ""

# Verificar resultado esperado
if [ "$http_code" -eq 403 ]; then
    echo "✅ ÉXITO: Acción rechazada correctamente"
    echo "✅ El sistema protegió la integridad rechazando la acción destructiva"
    echo "✅ El producto NO fue eliminado"
    exit 0
else
    echo "❌ FALLO: Se esperaba código 403 Forbidden, se obtuvo ${http_code}"
    if [ "$http_code" -eq 204 ] || [ "$http_code" -eq 200 ]; then
        echo "⚠️  ADVERTENCIA CRÍTICA: El producto fue eliminado, violando la integridad"
    fi
    exit 1
fi

