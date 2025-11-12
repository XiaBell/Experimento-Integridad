variable "aws_region" {
  description = "Región de AWS donde se desplegará la infraestructura"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Nombre del proyecto para identificar recursos"
  type        = string
  default     = "experimento-integridad"
}

variable "instance_type" {
  description = "Tipo de instancia EC2"
  type        = string
  default     = "t3.micro"
}

variable "key_name" {
  description = "Nombre de la clave SSH para acceso a las instancias"
  type        = string
}

variable "db_username" {
  description = "Usuario de la base de datos PostgreSQL"
  type        = string
  default     = "postgres"
}

variable "db_password" {
  description = "Contraseña de la base de datos PostgreSQL"
  type        = string
  sensitive   = true
}

variable "jwt_secret_key" {
  description = "Clave secreta para firmar/verificar JWT"
  type        = string
  sensitive   = true
}

variable "allowed_cidr_blocks" {
  description = "CIDR blocks permitidos para acceso SSH"
  type        = list(string)
  default     = ["0.0.0.0/0"]  # En producción, restringir a IPs específicas
}

