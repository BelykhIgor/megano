from rest_framework import serializers
from .models import Sale
from products.serializers import CustomDateSerializer
from products.serializers import ProductImageSerializer

from products.models import Tag


class SalesSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='product.id')
    price = serializers.DecimalField(max_digits=10, decimal_places=2, source='product.price')
    salePrice = serializers.DecimalField(max_digits=10, decimal_places=2)
    dateFrom = CustomDateSerializer()
    dateTo = CustomDateSerializer()
    title = serializers.CharField(source='product.title')
    images = serializers.SerializerMethodField()

    class Meta:
        model = Sale
        fields = [
            'id', 'price', 'salePrice',  'dateFrom', 'dateTo', 'title', 'images'
        ]

    def get_images(self, obj):
        image_data = ProductImageSerializer(obj.product.product_images.all(), many=True).data
        return [image_data[0] if image_data else {}]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']