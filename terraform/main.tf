terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Data source para obtener la VPC por defecto
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Security Group para Kong Gateway
resource "aws_security_group" "kong" {
  name        = "${var.project_name}-kong-sg"
  description = "Security group para Kong API Gateway"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "HTTP"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 8443
    to_port     = 8443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Admin API"
    from_port   = 8001
    to_port     = 8001
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-kong-sg"
  }
}

# Security Group para el microservicio PRODUCTS
resource "aws_security_group" "products" {
  name        = "${var.project_name}-products-sg"
  description = "Security group para microservicio PRODUCTS"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description     = "HTTP desde Kong"
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.kong.id]
  }

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-products-sg"
  }
}

# Security Group para la base de datos PostgreSQL
resource "aws_security_group" "database" {
  name        = "${var.project_name}-db-sg"
  description = "Security group para base de datos PostgreSQL"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description     = "PostgreSQL desde PRODUCTS"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.products.id]
  }

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-db-sg"
  }
}

# Instancia EC2 para Kong Gateway
resource "aws_instance" "kong" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
  key_name      = var.key_name

  vpc_security_group_ids = [aws_security_group.kong.id]

  user_data = <<-EOF
              #!/bin/bash
              apt-get update
              apt-get install -y docker.io docker-compose
              systemctl start docker
              systemctl enable docker
              usermod -aG docker ubuntu
              
              # Instalar Kong (simplificado - en producción usar instalación oficial)
              docker pull kong:latest
              
              # Crear directorio para configuración
              mkdir -p /opt/kong
              EOF

  tags = {
    Name = "${var.project_name}-kong"
    Role = "api-gateway"
  }
}

# Instancias EC2 para el microservicio PRODUCTS (2 instancias para redundancia)
resource "aws_instance" "products" {
  count         = 2
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
  key_name      = var.key_name

  vpc_security_group_ids = [aws_security_group.products.id]

  user_data = <<-EOF
              #!/bin/bash
              apt-get update
              apt-get install -y python3-pip python3-venv postgresql-client
              
              # Variables de entorno para el servicio
              cat >> /etc/environment << EOL
              DB_HOST=${aws_instance.database.private_ip}
              DB_NAME=warehouse_db
              DB_USER=${var.db_username}
              DB_PASSWORD=${var.db_password}
              JWT_SECRET_KEY=${var.jwt_secret_key}
              JWT_ALGORITHM=HS256
              DEBUG=False
              EOL
              EOF

  tags = {
    Name = "${var.project_name}-products-${count.index + 1}"
    Role = "products-service"
  }
}

# Instancia EC2 para la base de datos PostgreSQL
resource "aws_instance" "database" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
  key_name      = var.key_name

  vpc_security_group_ids = [aws_security_group.database.id]

  user_data = <<-EOF
              #!/bin/bash
              apt-get update
              apt-get install -y postgresql postgresql-contrib
              
              # Configurar PostgreSQL
              sudo -u postgres psql -c "CREATE DATABASE warehouse_db;"
              sudo -u postgres psql -c "CREATE USER ${var.db_username} WITH PASSWORD '${var.db_password}';"
              sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE warehouse_db TO ${var.db_username};"
              
              # Configurar para aceptar conexiones
              echo "host    all             all             10.0.0.0/16               md5" >> /etc/postgresql/*/main/pg_hba.conf
              echo "listen_addresses = '*'" >> /etc/postgresql/*/main/postgresql.conf
              
              systemctl restart postgresql
              EOF

  tags = {
    Name = "${var.project_name}-database"
    Role = "database"
  }
}

# Data source para obtener la AMI de Ubuntu más reciente
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

