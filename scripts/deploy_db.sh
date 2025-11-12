#!/bin/bash
# Script para configurar la base de datos en AWS EC2

set -e

echo "🗄️  Configurando PostgreSQL..."

# Variables (ajustar según necesidad)
DB_PASSWORD="${DB_PASSWORD:-TuPasswordSeguro123!}"

# Verificar que PostgreSQL esté instalado
if ! command -v psql &> /dev/null; then
    echo "Instalando PostgreSQL..."
    sudo apt-get update
    sudo apt-get install -y postgresql postgresql-contrib
fi

# Iniciar PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Crear base de datos y usuario
sudo -u postgres psql << EOF
-- Crear base de datos
CREATE DATABASE warehouse_db;

-- Crear usuario
CREATE USER postgres WITH PASSWORD '$DB_PASSWORD';

-- Dar permisos
GRANT ALL PRIVILEGES ON DATABASE warehouse_db TO postgres;
ALTER USER postgres CREATEDB;
\q
EOF

# Configurar PostgreSQL para conexiones remotas
PG_VERSION=$(psql --version | grep -oP '\d+' | head -1)
PG_CONF="/etc/postgresql/$PG_VERSION/main/postgresql.conf"
PG_HBA="/etc/postgresql/$PG_VERSION/main/pg_hba.conf"

# Configurar listen_addresses
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" $PG_CONF

# Agregar regla de autenticación
if ! grep -q "10.0.0.0/16" $PG_HBA; then
    echo "host    all             all             10.0.0.0/16               md5" | sudo tee -a $PG_HBA
fi

# Reiniciar PostgreSQL
sudo systemctl restart postgresql

# Verificar
echo "✅ Verificando conexión..."
sudo -u postgres psql -d warehouse_db -c "SELECT version();" > /dev/null

echo "✅ PostgreSQL configurado correctamente!"
echo "   Base de datos: warehouse_db"
echo "   Usuario: postgres"
echo "   Contraseña: $DB_PASSWORD"

