from django.contrib import admin
from products.models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'sku', 'quantity', 'price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'sku']

