# Experimento de Integridad - Sistema de Gestión de Warehouse

Este proyecto implementa un experimento de **Integridad** basado en control de acceso (RBAC) para demostrar que usuarios con bajo privilegio (OPERARIO) no pueden manipular datos críticos (eliminar productos).

## 📋 Tabla de Contenidos

- [Arquitectura](#arquitectura)
- [ASR de Integridad](#asr-de-integridad)
- [Estructura del Proyecto](#estructura-del-proyecto)

## 🏗️ Arquitectura

- **Frontend**: Interfaz web HTML/JavaScript para probar el experimento
- **API Gateway**: Kong (valida firma JWT)
- **Microservicio PRODUCTS**: Django REST Framework (verifica roles RBAC)
- **Base de Datos**: PostgreSQL
- **Infraestructura**: AWS (EC2, VPC) gestionada con Terraform
- **Autenticación**: JWT (JSON Web Tokens)

## 🎯 ASR de Integridad

| Fuente | Ambiente | Estímulo | Respuesta | Medida de Respuesta |
|--------|----------|----------|-----------|---------------------|
| Operario de Bodega | Sistema operando correctamente, solo permisos de lectura (`GET`) | Intento de eliminar producto mediante `DELETE /products/{id}` | Sistema detecta rol no autorizado y rechaza la petición | **100% de las veces** con código **403 Forbidden** en menos de **1s** |

## 📁 Estructura del Proyecto

```
EXPERIMENTO-INTEGRIDAD/
├── products-service/          # Microservicio Django
│   ├── products/
│   │   ├── models.py          # Modelo Product
│   │   ├── views.py           # Vistas con RBAC
│   │   ├── permissions.py     # Clases de permisos (IsAdminOrReadOnly)
│   │   ├── middleware.py      # Middleware JWT
│   │   └── utils.py           # Utilidades JWT
│   └── requirements.txt
├── terraform/                 # Infraestructura como código
│   ├── main.tf                # Recursos AWS
│   ├── variables.tf           # Variables de configuración
│   └── outputs.tf             # Outputs (IPs, endpoints)
├── kong/                      # Configuración de Kong
│   ├── kong.yml               # Configuración declarativa
│   └── README.md              # Guía de instalación
├── tests/                     # Scripts de prueba
│   ├── test_admin.sh          # Prueba con rol ADMIN (204)
│   ├── test_operario.sh       # Prueba con rol OPERARIO (403)
│   └── generate_tokens.py     # Generador de tokens JWT
├── docs/                      # Documentación
│   └── EXPERIMENTO.md         # Documentación detallada del experimento
└── README.md                  # Este archivo
```

## 📝 Notas

- Este experimento está diseñado para demostrar el principio de **integridad** mediante control de acceso basado en roles (RBAC)
- El frontend web permite probar visualmente el experimento sin necesidad de Postman o scripts
- Las credenciales de prueba se pueden ver en la sección de pver credenciales desde el front cuando se deseen probar.


