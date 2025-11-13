"""
Comando de Django para poblar la base de datos con productos de prueba.
"""
from django.core.management.base import BaseCommand
from products.models import Product


class Command(BaseCommand):
    help = 'Pobla la base de datos con productos de prueba'

    def handle(self, *args, **options):
        products_data = [
            {
                'name': 'Laptop Dell XPS 15',
                'description': 'Laptop de alta gama con procesador Intel i7',
                'sku': 'LAP-DELL-XPS15-001',
                'quantity': 25,
                'price': 1299.99,
            },
            {
                'name': 'Mouse Logitech MX Master 3',
                'description': 'Mouse inalámbrico ergonómico',
                'sku': 'MOU-LOG-MX3-001',
                'quantity': 150,
                'price': 99.99,
            },
            {
                'name': 'Teclado Mecánico Keychron K2',
                'description': 'Teclado mecánico inalámbrico 75%',
                'sku': 'TEC-KEY-K2-001',
                'quantity': 80,
                'price': 89.99,
            },
            {
                'name': 'Monitor LG UltraWide 34"',
                'description': 'Monitor curvo 3440x1440 144Hz',
                'sku': 'MON-LG-UW34-001',
                'quantity': 40,
                'price': 599.99,
            },
            {
                'name': 'Auriculares Sony WH-1000XM4',
                'description': 'Auriculares inalámbricos con cancelación de ruido',
                'sku': 'AUD-SON-WH1000-001',
                'quantity': 60,
                'price': 349.99,
            },
            {
                'name': 'Webcam Logitech C920',
                'description': 'Cámara web Full HD 1080p',
                'sku': 'CAM-LOG-C920-001',
                'quantity': 120,
                'price': 79.99,
            },
            {
                'name': 'SSD Samsung 1TB',
                'description': 'Disco sólido interno NVMe M.2',
                'sku': 'SSD-SAM-1TB-001',
                'quantity': 200,
                'price': 129.99,
            },
            {
                'name': 'Memoria RAM Corsair 16GB',
                'description': 'Memoria DDR4 3200MHz',
                'sku': 'RAM-COR-16GB-001',
                'quantity': 180,
                'price': 89.99,
            },
            {
                'name': 'Placa Base ASUS B550',
                'description': 'Motherboard AM4 para AMD Ryzen',
                'sku': 'MB-ASU-B550-001',
                'quantity': 45,
                'price': 179.99,
            },
            {
                'name': 'Fuente de Poder Corsair 750W',
                'description': 'Fuente modular 80 Plus Gold',
                'sku': 'PSU-COR-750W-001',
                'quantity': 70,
                'price': 119.99,
            },
            {
                'name': 'Tarjeta Gráfica NVIDIA RTX 3060',
                'description': 'GPU 12GB GDDR6',
                'sku': 'GPU-NVI-RTX3060-001',
                'quantity': 15,
                'price': 399.99,
            },
            {
                'name': 'Disco Duro Externo Seagate 2TB',
                'description': 'HDD portátil USB 3.0',
                'sku': 'HDD-SEA-2TB-001',
                'quantity': 90,
                'price': 69.99,
            },
            {
                'name': 'Router TP-Link Archer AX50',
                'description': 'Router WiFi 6 AX3000',
                'sku': 'ROU-TPL-AX50-001',
                'quantity': 55,
                'price': 149.99,
            },
            {
                'name': 'Hub USB-C Anker 7 puertos',
                'description': 'Hub multipuerto con HDMI y USB',
                'sku': 'HUB-ANK-7P-001',
                'quantity': 130,
                'price': 49.99,
            },
            {
                'name': 'Cable HDMI 2.1 3 metros',
                'description': 'Cable de alta velocidad 4K 120Hz',
                'sku': 'CAB-HDM-3M-001',
                'quantity': 250,
                'price': 24.99,
            },
            {
                'name': 'Alfombrilla Gaming Razer',
                'description': 'Alfombrilla de ratón XL',
                'sku': 'MAT-RAZ-XL-001',
                'quantity': 100,
                'price': 29.99,
            },
            {
                'name': 'Micrófono Blue Yeti',
                'description': 'Micrófono USB condensador',
                'sku': 'MIC-BLU-YETI-001',
                'quantity': 35,
                'price': 129.99,
            },
            {
                'name': 'Soporte Monitor Ergonómico',
                'description': 'Brazos articulados para monitor',
                'sku': 'STA-ERG-ARM-001',
                'quantity': 60,
                'price': 89.99,
            },
            {
                'name': 'Ventilador CPU Noctua NH-D15',
                'description': 'Cooler de aire para CPU',
                'sku': 'FAN-NOC-NH15-001',
                'quantity': 25,
                'price': 99.99,
            },
        ]

        created_count = 0
        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                sku=product_data['sku'],
                defaults=product_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Producto creado: {product.name} (SKU: {product.sku})')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'→ Producto ya existe: {product.name} (SKU: {product.sku})')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Proceso completado. {created_count} productos nuevos creados.')
        )

