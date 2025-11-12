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

