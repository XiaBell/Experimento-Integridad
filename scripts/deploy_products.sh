#!/bin/bash
# Script para desplegar el microservicio PRODUCTS en AWS EC2

set -e

echo "🐍 Desplegando microservicio PRODUCTS..."

# Variables (ajustar según necesidad)
REPO_URL="${REPO_URL:-https://github.com/tu-usuario/experimento-integridad.git}"
DB_HOST="${DB_HOST:-localhost}"
DB_NAME="${DB_NAME:-warehouse_db}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD:-TuPasswordSeguro123!}"
JWT_SECRET="${JWT_SECRET:-TuClaveSecretaJWT123!}"
INSTALL_DIR="/opt/products-service"

# Instalar dependencias del sistema
echo "📦 Instalando dependencias del sistema..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv postgresql-client git nginx

# Clonar repositorio
echo "📥 Clonando repositorio..."
if [ -d "$INSTALL_DIR" ]; then
    echo "   Directorio ya existe, actualizando..."
    cd $INSTALL_DIR
    sudo git pull
else
    sudo git clone $REPO_URL $INSTALL_DIR
fi

cd $INSTALL_DIR/products-service

# Crear entorno virtual
echo "🔧 Configurando entorno virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# Instalar dependencias Python
echo "📦 Instalando dependencias Python..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Generar SECRET_KEY
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')

# Crear archivo .env
echo "⚙️  Configurando variables de entorno..."
cat > .env << EOF
SECRET_KEY=$SECRET_KEY
DEBUG=False
DB_HOST=$DB_HOST
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
JWT_SECRET_KEY=$JWT_SECRET
JWT_ALGORITHM=HS256
ALLOWED_HOSTS=*
EOF

# Cargar variables de entorno
export $(cat .env | xargs)

# Ejecutar migraciones
echo "🗄️  Ejecutando migraciones..."
python manage.py migrate

# Poblar datos de prueba
echo "📊 Poblando datos de prueba..."
python manage.py seed_products

# Crear archivo de servicio systemd
echo "🔧 Configurando servicio systemd..."
sudo tee /etc/systemd/system/products-service.service > /dev/null << EOF
[Unit]
Description=Products Service Gunicorn
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=$INSTALL_DIR/products-service
Environment="PATH=$INSTALL_DIR/products-service/venv/bin"
EnvironmentFile=$INSTALL_DIR/products-service/.env
ExecStart=$INSTALL_DIR/products-service/venv/bin/gunicorn \\
    --workers 2 \\
    --bind 0.0.0.0:8000 \\
    --timeout 120 \\
    products_service.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

# Habilitar y iniciar servicio
echo "🚀 Iniciando servicio..."
sudo systemctl daemon-reload
sudo systemctl enable products-service
sudo systemctl restart products-service

# Esperar a que el servicio inicie
sleep 3

# Verificar que está corriendo
if sudo systemctl is-active --quiet products-service; then
    echo "✅ Servicio PRODUCTS iniciado correctamente!"
    echo "   Ver logs con: sudo journalctl -u products-service -f"
    echo "   Estado: sudo systemctl status products-service"
else
    echo "❌ Error al iniciar el servicio"
    sudo journalctl -u products-service -n 50
    exit 1
fi

# Verificar que responde
echo "🔍 Verificando que el servicio responde..."
sleep 2
if curl -s http://localhost:8000/api/products/ > /dev/null; then
    echo "✅ El servicio responde correctamente!"
else
    echo "⚠️  El servicio no responde, revisa los logs"
fi

