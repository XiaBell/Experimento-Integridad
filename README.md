# Experimento de Integridad - Sistema de Gestión de Warehouse

Este proyecto implementa un experimento de **Integridad** basado en control de acceso (RBAC) para demostrar que usuarios con bajo privilegio (OPERARIO) no pueden manipular datos críticos (eliminar productos).

## 📋 Tabla de Contenidos

- [Arquitectura](#arquitectura)
- [ASR de Integridad](#asr-de-integridad)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Inicio Rápido](#inicio-rápido)
- [Instalación y Despliegue](#instalación-y-despliegue)
- [Ejecución del Experimento](#ejecución-del-experimento)
- [Documentación](#documentación)

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
| Operario de Bodega | Sistema operando correctamente, solo permisos de lectura (`GET`) | Intento de eliminar producto mediante `DELETE /products/{id}` | Sistema detecta rol no autorizado y rechaza la petición | **100% de las veces** con código **403 Forbidden** en menos de **100 ms** |

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
├── README.md                  # Este archivo
├── QUICKSTART.md              # Guía rápida de inicio
└── DEPLOY.md                  # Guía completa de despliegue
```

## 🚀 Inicio Rápido

Para ejecutar el experimento localmente en 5 minutos, consulta [QUICKSTART.md](QUICKSTART.md).

### Opción 1: Usar el Frontend Web (Recomendado)

```bash
# 1. Configurar microservicio
cd products-service
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_products
python manage.py runserver

# 2. Abrir navegador en http://localhost:8000
# 3. Usar las credenciales:
#    - Admin: admin / admin123
#    - Operario: operario / operario123
```

### Opción 2: Usar Scripts de Prueba

```bash
# 1. Configurar microservicio (igual que arriba)
# 2. Generar tokens JWT
cd ../tests
python3 generate_tokens.py
export ADMIN_TOKEN=$(cat admin_token.txt)
export OPERARIO_TOKEN=$(cat operario_token.txt)

# 3. Ejecutar pruebas
./test_admin.sh      # Debe retornar 204
./test_operario.sh   # Debe retornar 403
```

## 📦 Instalación y Despliegue

### Opción 1: Despliegue Local (Desarrollo/Pruebas)

Ver [QUICKSTART.md](QUICKSTART.md) para una guía rápida.

### Opción 2: Despliegue en AWS (Producción)

Ver [DEPLOY.md](DEPLOY.md) para instrucciones completas de despliegue con Terraform.

**Resumen rápido:**

```bash
# 1. Configurar Terraform
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Editar terraform.tfvars con tus valores

# 2. Desplegar infraestructura
terraform init
terraform plan
terraform apply

# 3. Configurar servicios (ver DEPLOY.md)
# - Base de datos PostgreSQL
# - Microservicio PRODUCTS (2 instancias)
# - Kong API Gateway

# 4. Ejecutar pruebas
cd ../tests
# Configurar variables de entorno con IPs de AWS
./test_admin.sh
./test_operario.sh
```

## 🧪 Ejecución del Experimento

### Escenario 1: ADMIN (Control - Éxito)

```bash
./tests/test_admin.sh
```

**Resultado Esperado**: 
- Código HTTP: **204 No Content**
- El producto es eliminado exitosamente
- Log: "Acceso autorizado: Usuario ADMIN puede realizar DELETE"

### Escenario 2: OPERARIO (Integridad - Rechazo)

```bash
./tests/test_operario.sh
```

**Resultado Esperado**: 
- Código HTTP: **403 Forbidden**
- El producto **NO** es eliminado
- Mensaje: "Acción no autorizada. Requiere rol 'ADMIN'."
- Log: "Acceso denegado: Usuario con rol 'OPERARIO' intentó realizar DELETE"

## 📊 Evidencias

Las evidencias del experimento deben incluir:

1. **Pantallazo de Postman** con petición `DELETE` como ADMIN (204)
2. **Pantallazo de Postman** con petición `DELETE` como OPERARIO (403)
3. **Logs de Django** mostrando:
   - Para ADMIN: "Acceso autorizado: Usuario ADMIN puede realizar DELETE"
   - Para OPERARIO: "Acceso denegado: Usuario con rol 'OPERARIO' intentó realizar DELETE"

## 📚 Documentación

- **[EXPERIMENTO.md](docs/EXPERIMENTO.md)**: Documentación detallada del experimento, ASR, tácticas de arquitectura, y análisis de resultados
- **[CREDENCIALES.md](CREDENCIALES.md)**: Credenciales de acceso para el experimento (admin/operario)
- **[DEPLOY.md](DEPLOY.md)**: Guía completa de despliegue en AWS
- **[QUICKSTART.md](QUICKSTART.md)**: Guía rápida para ejecutar localmente
- **[kong/README.md](kong/README.md)**: Configuración e instalación de Kong
- **[tests/README.md](tests/README.md)**: Instrucciones para ejecutar pruebas

## 🧹 Limpieza

**IMPORTANTE**: Al finalizar el experimento, destruir la infraestructura para evitar costos:

```bash
cd terraform
terraform destroy
```

## 🔧 Troubleshooting

### Error: Token JWT no se decodifica

- Verificar que `JWT_SECRET_KEY` en Django coincida con la clave usada para firmar el token
- Verificar que el token incluya el claim `role` con valor `ADMIN` o `OPERARIO`

### Error: OPERARIO puede eliminar productos

- Verificar que el middleware `JWTAuthenticationMiddleware` esté en `MIDDLEWARE` en `settings.py`
- Verificar que la clase de permisos `IsAdminOrReadOnly` esté configurada en la vista
- Revisar logs de Django para ver qué rol se está detectando

### Error: Kong rechaza todas las peticiones

- Verificar que el plugin JWT esté habilitado en Kong
- Verificar que el token JWT sea válido y esté firmado con la clave correcta

## 📝 Notas

- Este experimento está diseñado para demostrar el principio de **integridad** mediante control de acceso basado en roles (RBAC)
- El frontend web permite probar visualmente el experimento sin necesidad de Postman o scripts
- Las credenciales de prueba están documentadas en [CREDENCIALES.md](CREDENCIALES.md)
- En producción, los tokens JWT deben venir de un proveedor de identidad (Auth0, Keycloak, etc.)
- El código está preparado para integrarse con proveedores de identidad externos
- Los tokens generados por `generate_tokens.py` son solo para pruebas locales

## 📄 Licencia

Este proyecto es parte de un experimento académico.

