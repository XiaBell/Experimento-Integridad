output "kong_public_ip" {
  description = "IP pública de la instancia Kong"
  value       = aws_instance.kong.public_ip
}

output "kong_public_dns" {
  description = "DNS público de la instancia Kong"
  value       = aws_instance.kong.public_dns
}

output "products_public_ips" {
  description = "IPs públicas de las instancias PRODUCTS"
  value       = aws_instance.products[*].public_ip
}

output "products_private_ips" {
  description = "IPs privadas de las instancias PRODUCTS"
  value       = aws_instance.products[*].private_ip
}

output "database_private_ip" {
  description = "IP privada de la instancia de base de datos"
  value       = aws_instance.database.private_ip
  sensitive   = true
}

output "kong_endpoint" {
  description = "Endpoint del API Gateway Kong"
  value       = "http://${aws_instance.kong.public_ip}:8000"
}

output "kong_admin_endpoint" {
  description = "Endpoint del Admin API de Kong"
  value       = "http://${aws_instance.kong.public_ip}:8001"
}

output "ssh_commands" {
  description = "Comandos SSH para conectarse a las instancias"
  value = {
    kong     = "ssh -i ~/.ssh/${var.key_name}.pem ubuntu@${aws_instance.kong.public_ip}"
    products = [for i, ip in aws_instance.products[*].public_ip : "ssh -i ~/.ssh/${var.key_name}.pem ubuntu@${ip}"]
    database = "ssh -i ~/.ssh/${var.key_name}.pem ubuntu@${aws_instance.database.public_ip}"
  }
}

