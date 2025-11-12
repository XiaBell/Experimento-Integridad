# Configuración de Kong API Gateway

Este directorio contiene la configuración de Kong para el experimento de integridad.

## Instalación de Kong

### Opción 1: Usando Docker (Recomendado para desarrollo)

```bash
# Iniciar Kong con PostgreSQL
docker run -d --name kong-database \
  -p 5432:5432 \
  -e "POSTGRES_USER=kong" \
  -e "POSTGRES_PASSWORD=kong" \
  -e "POSTGRES_DB=kong" \
  postgres:13

# Migrar base de datos
docker run --rm \
  --link kong-database:kong-database \
  -e "KONG_DATABASE=postgres" \
  -e "KONG_PG_HOST=kong-database" \
  -e "KONG_PG_USER=kong" \
  -e "KONG_PG_PASSWORD=kong" \
  kong:latest kong migrations bootstrap

# Iniciar Kong
docker run -d --name kong \
  --link kong-database:kong-database \
  -e "KONG_DATABASE=postgres" \
  -e "KONG_PG_HOST=kong-database" \
  -e "KONG_PG_USER=kong" \
  -e "KONG_PG_PASSWORD=kong" \
  -e "KONG_PROXY_ACCESS_LOG=/dev/stdout" \
  -e "KONG_ADMIN_ACCESS_LOG=/dev/stdout" \
  -e "KONG_PROXY_ERROR_LOG=/dev/stderr" \
  -e "KONG_ADMIN_ERROR_LOG=/dev/stderr" \
  -e "KONG_ADMIN_LISTEN=0.0.0.0:8001" \
  -p 8000:8000 \
  -p 8443:8443 \
  -p 8001:8001 \
  -p 8444:8444 \
  kong:latest
```

### Opción 2: Instalación en Ubuntu (Para producción en EC2)

```bash
# Seguir la guía oficial de Kong
# https://docs.konghq.com/gateway/latest/install-and-run/ubuntu/
```

## Configuración del Servicio PRODUCTS

Una vez Kong esté corriendo, configurar el servicio:

```bash
# Crear el servicio
curl -i -X POST http://localhost:8001/services/ \
  --data "name=products-service" \
  --data "url=http://PRODUCTS_SERVICE_IP:8000"

# Crear la ruta
curl -i -X POST http://localhost:8001/services/products-service/routes \
  --data "hosts[]=localhost" \
  --data "paths[]=/products" \
  --data "methods[]=GET" \
  --data "methods[]=POST" \
  --data "methods[]=PUT" \
  --data "methods[]=PATCH" \
  --data "methods[]=DELETE"

# Habilitar plugin JWT
curl -i -X POST http://localhost:8001/services/products-service/plugins \
  --data "name=jwt"
```

## Notas

- En producción, reemplazar `PRODUCTS_SERVICE_IP` con las IPs reales de las instancias EC2
- El plugin JWT de Kong valida la firma del token, pero no verifica roles
- La verificación de roles se hace en el microservicio PRODUCTS (Django)

