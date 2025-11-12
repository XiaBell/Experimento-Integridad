from rest_framework import serializers
from products.models import Product


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Product.
    """
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'sku', 'quantity', 'price', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

