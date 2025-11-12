# 🚀 Guía de Despliegue en AWS - Experimento de Integridad

Esta guía te llevará paso a paso para desplegar el experimento de integridad en AWS usando **Terraform para la infraestructura** y luego **configuración manual del software** desde la consola web de AWS.

## 📋 Prerequisitos

1. **Cuenta AWS** con permisos para crear EC2, VPC, Security Groups
2. **Terraform** instalado (`terraform --version`)
3. **AWS CLI** configurado (`aws configure`)
4. **Clave SSH** en AWS (si no la tienes, créala en EC2 → Key Pairs)
5. **Git** instalado en tu máquina local

## 🏗️ Parte 1: Crear Infraestructura con Terraform

Terraform se encargará de crear automáticamente:
- ✅ 3 Security Groups (Kong, PRODUCTS, Database)
- ✅ 4 Instancias EC2 (1 Kong, 2 PRODUCTS, 1 Database)
- ✅ Configuración básica de red y seguridad

### Paso 1.1: Preparar Terraform

```bash
# Desde tu máquina local
cd /Users/majo/Desktop/EXPERIMENTO-INTEGRIDAD/terraform

# Copiar archivo de variables
cp terraform.tfvars.example terraform.tfvars

# Editar terraform.tfvars con tus valores
nano terraform.tfvars  # O usa tu editor favorito
```

**Editar `terraform.tfvars` con estos valores:**

```hcl
aws_region = "us-east-1"  # O tu región preferida
project_name = "experimento-integridad"
instance_type = "t3.micro"  # Free tier eligible

# IMPORTANTE: Nombre de tu clave SSH en AWS (sin la extensión .pem)
key_name = "mi-clave-aws"

# IMPORTANTE: Contraseñas seguras (guárdalas bien, las necesitarás después)
db_password = "MiPasswordSeguro123!"
jwt_secret_key = "MiClaveSecretaJWT123!"

# (Opcional) Restringir SSH solo a tu IP para mayor seguridad
# allowed_cidr_blocks = ["TU.IP.PUBLICA.AQUI/32"]
```

### Paso 1.2: Inicializar y Desplegar con Terraform

```bash
# Inicializar Terraform (descarga providers)
terraform init

# Ver qué se va a crear (revisa que todo esté bien)
terraform plan

# Crear la infraestructura (esto puede tardar 5-10 minutos)
terraform apply
# Escribe "yes" cuando te pregunte

# Guardar las IPs de las instancias
terraform output > ../aws_outputs.txt
cat ../aws_outputs.txt
```

**✅ Listo!** Terraform ha creado:
- 4 instancias EC2 corriendo
- 3 Security Groups configurados
- Todo conectado correctamente

**Anota estas IPs (las necesitarás después):**
- `kong_public_ip`: IP pública de Kong (para acceder al frontend)
- `products_public_ips`: IPs públicas de las 2 instancias PRODUCTS
- `database_private_ip`: IP privada de la base de datos (para PRODUCTS)

### Paso 1.3: Verificar en la Consola AWS

1. Ve a **EC2 → Instances** en la consola de AWS
2. Deberías ver 4 instancias con estos nombres:
   - `experimento-integridad-kong`
   - `experimento-integridad-products-1`
   - `experimento-integridad-products-2`
   - `experimento-integridad-database`
3. Espera a que todas estén en estado **"Running"** (puede tardar 2-3 minutos)

## 🗄️ Parte 2: Configurar Base de Datos

### Paso 2.1: Conectarse a la Instancia Database

**Opción A: Desde la Consola Web de AWS (Session Manager)**

1. En **EC2 → Instances**, selecciona la instancia `experimento-integridad-database`
2. Click en **Connect**
3. Pestaña **Session Manager** → Click **Connect**
4. Se abrirá una terminal en el navegador

**Opción B: Desde tu máquina local (SSH)**

```bash
# Obtener la IP pública de la base de datos
cd terraform
DB_IP=$(terraform output -raw database_private_ip)
# O busca la IP pública en la consola de AWS

# Conectarse (ajusta la ruta de tu clave)
ssh -i ~/.ssh/mi-clave-aws.pem ubuntu@<DB_PUBLIC_IP>
```

### Paso 2.2: Configurar PostgreSQL

Una vez conectado, ejecuta estos comandos:

```bash
# Verificar que PostgreSQL esté instalado y corriendo
sudo systemctl status postgresql

# Si no está corriendo:
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verificar que la base de datos se creó (Terraform lo hizo en user_data)
sudo -u postgres psql -l | grep warehouse_db

# Si no existe, crearla manualmente:
sudo -u postgres psql << EOF
CREATE DATABASE warehouse_db;
CREATE USER postgres WITH PASSWORD 'MiPasswordSeguro123!';
GRANT ALL PRIVILEGES ON DATABASE warehouse_db TO postgres;
ALTER USER postgres CREATEDB;
\q
EOF

# Verificar configuración de conexiones remotas
sudo cat /etc/postgresql/*/main/pg_hba.conf | grep "10.0.0.0/16"
sudo cat /etc/postgresql/*/main/postgresql.conf | grep listen_addresses

# Si no están configuradas (aunque Terraform las configuró), hacerlo:
echo "host    all             all             10.0.0.0/16               md5" | sudo tee -a /etc/postgresql/*/main/pg_hba.conf
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" /etc/postgresql/*/main/postgresql.conf

# Reiniciar PostgreSQL
sudo systemctl restart postgresql

# Probar conexión
sudo -u postgres psql -d warehouse_db -c "SELECT version();"
```

**✅ Listo:** La base de datos está configurada. Anota la **IP privada** de esta instancia (la encontrarás en la consola de AWS o con `terraform output database_private_ip`).

## 🐍 Parte 3: Desplegar Microservicio PRODUCTS

Repite estos pasos en **AMBAS** instancias PRODUCTS (`products-1` y `products-2`).

### Paso 3.1: Conectarse a la Instancia PRODUCTS

**Desde la Consola Web:**
1. Selecciona la instancia `experimento-integridad-products-1` (o `products-2`)
2. Click **Connect** → **Session Manager** → **Connect**

**O desde tu máquina:**
```bash
cd terraform
PRODUCTS_IP=$(terraform output -json products_public_ips | jq -r '.[0]')  # Para products-1
# O usa [1] para products-2

ssh -i ~/.ssh/mi-clave-aws.pem ubuntu@$PRODUCTS_IP
```

### Paso 3.2: Clonar el Repositorio

```bash
# Instalar git si no está instalado
sudo apt-get update
sudo apt-get install -y git

# Clonar tu repositorio (reemplaza con tu URL de GitHub)
cd /opt
sudo git clone https://github.com/tu-usuario/experimento-integridad.git
sudo mv experimento-integridad products-service
sudo chown -R ubuntu:ubuntu products-service
cd products-service/products-service
```

**Nota:** Si tu repositorio es privado, necesitarás configurar credenciales de Git o usar SSH keys.

### Paso 3.3: Configurar Entorno Python

```bash
# Instalar dependencias del sistema
sudo apt-get install -y python3-pip python3-venv postgresql-client nginx

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias Python
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

### Paso 3.4: Configurar Variables de Entorno

```bash
# IMPORTANTE: Obtener la IP privada de la base de datos
# Opción 1: Desde terraform (en tu máquina local)
# terraform output database_private_ip

# Opción 2: Desde la consola AWS, ver la IP privada de la instancia database

# Reemplazar estos valores:
DB_PRIVATE_IP="<IP_PRIVADA_DE_LA_DB>"  # Ejemplo: 10.0.1.123
DB_PASSWORD="MiPasswordSeguro123!"  # Debe coincidir con terraform.tfvars
JWT_SECRET="MiClaveSecretaJWT123!"  # Debe ser la MISMA en ambas instancias PRODUCTS

# Generar SECRET_KEY de Django
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')

# Crear archivo .env
cat > .env << EOF
SECRET_KEY=$SECRET_KEY
DEBUG=False
DB_HOST=$DB_PRIVATE_IP
DB_NAME=warehouse_db
DB_USER=postgres
DB_PASSWORD=$DB_PASSWORD
JWT_SECRET_KEY=$JWT_SECRET
JWT_ALGORITHM=HS256
ALLOWED_HOSTS=*
EOF

# Verificar que se creó correctamente
cat .env
```

### Paso 3.5: Ejecutar Migraciones y Poblar Datos

```bash
# Asegúrate de estar en el directorio correcto y con venv activado
cd /opt/products-service/products-service
source venv/bin/activate
export $(cat .env | xargs)

# Ejecutar migraciones
python manage.py migrate

# Poblar con datos de prueba
python manage.py seed_products

# Verificar que funciona (prueba rápida)
python manage.py runserver 0.0.0.0:8000 &
sleep 3
curl http://localhost:8000/api/products/
# Deberías ver JSON con productos
pkill -f "manage.py runserver"
```

### Paso 3.6: Configurar Gunicorn como Servicio

```bash
# Crear archivo de servicio systemd
sudo nano /etc/systemd/system/products-service.service
```

**Pegar este contenido:**
```ini
[Unit]
Description=Products Service Gunicorn
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/products-service/products-service
Environment="PATH=/opt/products-service/products-service/venv/bin"
EnvironmentFile=/opt/products-service/products-service/.env
ExecStart=/opt/products-service/products-service/venv/bin/gunicorn \
    --workers 2 \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    products_service.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
# Guardar y salir (Ctrl+X, Y, Enter)

# Habilitar y iniciar el servicio
sudo systemctl daemon-reload
sudo systemctl enable products-service
sudo systemctl start products-service

# Verificar que está corriendo
sudo systemctl status products-service

# Ver logs (opcional)
sudo journalctl -u products-service -f
# Presiona Ctrl+C para salir
```

### Paso 3.7: Repetir en la Segunda Instancia PRODUCTS

**IMPORTANTE:** Repite los pasos 3.1 a 3.6 en la **segunda instancia PRODUCTS** (`products-2`), asegurándote de:
- ✅ Usar la **misma IP privada de la base de datos**
- ✅ Usar el **mismo JWT_SECRET_KEY** (debe ser idéntico en ambas)
- ✅ Clonar el mismo repositorio

## 🚪 Parte 4: Configurar Kong API Gateway

### Paso 4.1: Conectarse a la Instancia Kong

**Desde la Consola Web:**
1. Selecciona la instancia `experimento-integridad-kong`
2. Click **Connect** → **Session Manager** → **Connect**

**O desde tu máquina:**
```bash
cd terraform
KONG_IP=$(terraform output -raw kong_public_ip)
ssh -i ~/.ssh/mi-clave-aws.pem ubuntu@$KONG_IP
```

### Paso 4.2: Verificar Docker

```bash
# Verificar que Docker esté instalado (Terraform lo instaló en user_data)
docker --version

# Si no está instalado:
sudo apt-get update
sudo apt-get install -y docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu
newgrp docker  # O cerrar y volver a abrir la sesión
```

### Paso 4.3: Configurar Kong con Docker Compose

```bash
# Crear directorio de trabajo
mkdir -p /opt/kong
cd /opt/kong

# Crear archivo docker-compose.yml
nano docker-compose.yml
```

**Pegar este contenido:**
```yaml
version: '3.8'

services:
  kong-database:
    image: postgres:13
    environment:
      POSTGRES_USER: kong
      POSTGRES_PASSWORD: kong
      POSTGRES_DB: kong
    volumes:
      - kong_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U kong"]
      interval: 10s
      timeout: 5s
      retries: 5

  kong-migration:
    image: kong:latest
    command: kong migrations bootstrap
    environment:
      KONG_DATABASE: postgres
      KONG_PG_HOST: kong-database
      KONG_PG_USER: kong
      KONG_PG_PASSWORD: kong
    depends_on:
      kong-database:
        condition: service_healthy

  kong:
    image: kong:latest
    environment:
      KONG_DATABASE: postgres
      KONG_PG_HOST: kong-database
      KONG_PG_USER: kong
      KONG_PG_PASSWORD: kong
      KONG_PROXY_ACCESS_LOG: /dev/stdout
      KONG_ADMIN_ACCESS_LOG: /dev/stdout
      KONG_PROXY_ERROR_LOG: /dev/stderr
      KONG_ADMIN_ERROR_LOG: /dev/stderr
      KONG_ADMIN_LISTEN: 0.0.0.0:8001
    ports:
      - "8000:8000"
      - "8443:8443"
      - "8001:8001"
      - "8444:8444"
    depends_on:
      kong-migration:
        condition: service_completed_successfully
    healthcheck:
      test: ["CMD", "kong", "health"]
      interval: 10s
      timeout: 10s
      retries: 10

volumes:
  kong_data:
```

```bash
# Guardar y salir (Ctrl+X, Y, Enter)

# Iniciar Kong
sudo docker-compose up -d

# Verificar que está corriendo
sudo docker-compose ps

# Ver logs
sudo docker-compose logs -f kong
# Presiona Ctrl+C para salir

# Verificar que Kong responde
curl http://localhost:8001/
# Deberías ver un JSON con información de Kong
```

### Paso 4.4: Configurar Servicios en Kong

```bash
# IMPORTANTE: Obtener la IP privada de una instancia PRODUCTS
# Opción 1: Desde terraform (en tu máquina local)
# terraform output products_private_ips

# Opción 2: Desde la consola AWS, ver la IP privada de products-1

# Reemplazar con la IP privada de PRODUCTS-1
PRODUCTS_IP="<IP_PRIVADA_PRODUCTS_1>"  # Ejemplo: 10.0.1.124

# Crear servicio en Kong
curl -i -X POST http://localhost:8001/services/ \
  --data "name=products-service" \
  --data "url=http://$PRODUCTS_IP:8000"

# Crear ruta
curl -i -X POST http://localhost:8001/services/products-service/routes \
  --data "hosts[]=*" \
  --data "paths[]=/api" \
  --data "methods[]=GET" \
  --data "methods[]=POST" \
  --data "methods[]=PUT" \
  --data "methods[]=PATCH" \
  --data "methods[]=DELETE"

# Verificar que el servicio está configurado
curl http://localhost:8001/services/products-service
curl http://localhost:8001/services/products-service/routes
```

**Nota:** Kong está configurado para pasar las peticiones directamente al servicio PRODUCTS. El plugin JWT es opcional para este experimento, ya que la verificación de roles se hace en Django.

## ✅ Parte 5: Verificar que Todo Funciona

### Paso 5.1: Obtener IP Pública de Kong

```bash
# Desde tu máquina local
cd terraform
terraform output kong_public_ip

# O desde la consola AWS, ver la IP pública de la instancia kong
```

### Paso 5.2: Probar desde tu Navegador

1. Abre tu navegador
2. Ve a: `http://<KONG_PUBLIC_IP>:8000`
3. Deberías ver la interfaz web del experimento
4. Prueba con las credenciales:
   - **Admin:** `admin` / `admin123` → Puede eliminar productos ✅
   - **Operario:** `operario` / `operario123` → No puede eliminar (403) ❌

### Paso 5.3: Probar desde Terminal (Opcional)

```bash
# Reemplazar <KONG_PUBLIC_IP> con la IP pública de Kong
KONG_IP="<KONG_PUBLIC_IP>"

# Probar login como ADMIN
curl -X POST http://$KONG_IP:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Guardar el token de la respuesta y probar eliminar
TOKEN="<token_del_response>"
curl -X DELETE http://$KONG_IP:8000/api/products/1/ \
  -H "Authorization: Bearer $TOKEN"
# Debería retornar 204 No Content

# Probar como OPERARIO (debe fallar con 403)
TOKEN_OPERARIO=$(curl -s -X POST http://$KONG_IP:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"operario","password":"operario123"}' | grep -o '"token":"[^"]*' | cut -d'"' -f4)

curl -X DELETE http://$KONG_IP:8000/api/products/2/ \
  -H "Authorization: Bearer $TOKEN_OPERARIO"
# Debería retornar 403 Forbidden
```

## 🧹 Parte 6: Limpieza (IMPORTANTE)

Cuando termines el experimento, **destruir toda la infraestructura** para evitar costos:

```bash
# Desde tu máquina local
cd terraform
terraform destroy
# Escribe "yes" cuando te pregunte
```

Esto eliminará:
- ✅ Todas las instancias EC2
- ✅ Todos los Security Groups creados
- ✅ Todo lo relacionado con el experimento

**IMPORTANTE:** Verifica que no queden recursos huérfanos en la consola de AWS.

## 📝 Checklist de Verificación

Antes de probar, verifica:

- [ ] Terraform aplicó correctamente (`terraform apply` exitoso)
- [ ] Todas las 4 instancias están en estado "Running" en la consola AWS
- [ ] Security Groups están creados y configurados correctamente
- [ ] Base de datos tiene la base `warehouse_db` creada
- [ ] Ambas instancias PRODUCTS tienen el mismo `JWT_SECRET_KEY`
- [ ] PRODUCTS usan la IP **privada** de la base de datos (no la pública)
- [ ] Kong está corriendo (`sudo docker-compose ps`)
- [ ] Kong responde en el puerto 8001 (`curl http://localhost:8001/`)
- [ ] Kong tiene configurado el servicio `products-service`
- [ ] Puedes acceder a `http://<KONG_IP>:8000` desde tu navegador

## 🐛 Troubleshooting

### Error: No se puede conectar a la base de datos desde PRODUCTS

- Verifica que el Security Group de la DB permita conexiones desde el Security Group de PRODUCTS en el puerto 5432
- Verifica que PostgreSQL esté escuchando en todas las interfaces (`listen_addresses = '*'`)
- Verifica que estás usando la IP **privada** de la DB, no la pública
- Verifica las credenciales en el archivo `.env`

### Error: Kong no responde

- Verifica que el Security Group de Kong permita tráfico en los puertos 8000, 8001 desde `0.0.0.0/0`
- Verifica logs: `sudo docker-compose logs kong`
- Verifica que Kong esté corriendo: `sudo docker-compose ps`
- Verifica que los puertos no estén ocupados: `sudo netstat -tulpn | grep 8000`

### Error: PRODUCTS service no responde

- Verifica logs: `sudo journalctl -u products-service -f`
- Verifica que el servicio esté corriendo: `sudo systemctl status products-service`
- Verifica que el puerto 8000 esté abierto: `curl http://localhost:8000/api/products/`
- Verifica el archivo `.env` tiene las variables correctas

### Error: Frontend no carga

- Verifica que estés accediendo a `http://<KONG_IP>:8000` (no `https://`)
- Verifica que Kong esté configurado correctamente
- Verifica los logs de Kong: `sudo docker-compose logs kong`
- Verifica que el Security Group de Kong permita tráfico HTTP (puerto 8000) desde `0.0.0.0/0`

### Error: Terraform no puede crear recursos

- Verifica que tengas permisos suficientes en AWS
- Verifica que la región sea correcta
- Verifica que el nombre de la clave SSH sea correcto
- Verifica los límites de tu cuenta AWS (número de instancias, etc.)

## 💡 Tips Importantes

1. **IPs Privadas vs Públicas:**
   - Base de datos: PRODUCTS deben usar la IP **privada** (no la pública)
   - Kong: Usa la IP **pública** para acceder desde fuera de AWS

2. **JWT Secret:**
   - Debe ser **exactamente igual** en ambas instancias PRODUCTS
   - Si cambias el secret, los tokens antiguos dejarán de funcionar
   - Guárdalo bien, lo necesitarás si reinicias las instancias

3. **Security Groups:**
   - Terraform los crea automáticamente con las reglas correctas
   - No necesitas modificarlos manualmente
   - Si necesitas cambiar algo, edita `main.tf` y ejecuta `terraform apply`

4. **Costos:**
   - Las instancias t3.micro son elegibles para free tier
   - Verifica tus límites de free tier en AWS
   - **Siempre ejecuta `terraform destroy` cuando termines**

5. **Session Manager vs SSH:**
   - Session Manager es más fácil (no necesitas clave SSH)
   - SSH es más rápido si ya tienes la clave configurada
   - Ambos funcionan igual para configurar el software

## 📚 Recursos Adicionales

- **Ver IPs de las instancias:** `terraform output`
- **Ver estado de Terraform:** `terraform show`
- **Ver logs de PRODUCTS:** `sudo journalctl -u products-service -f`
- **Ver logs de Kong:** `sudo docker-compose logs -f kong`
- **Reiniciar servicio PRODUCTS:** `sudo systemctl restart products-service`
- **Reiniciar Kong:** `sudo docker-compose restart kong`
