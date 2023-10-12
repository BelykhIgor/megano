from rest_framework import serializers
from django.contrib.auth.models import User
from products.models import Product, Tag, Reviews
from .models import Basket


class BasketSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    session = serializers.CharField(required=False)

    class Meta:
        model = Basket
        fields = ['user', 'session']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reviews
        fields = ['author', 'email', 'text', 'rate', 'date']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class ProductShortSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    category = serializers.CharField(source='category.id')
    count = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'category',
            'price',
            'count',
            'date',
            'title',
            'description',
            'freeDelivery',
            'images',
            'tags',
            'reviews',
            'rating'
        ]

    def get_reviews(self, instance):
        reviews_data = ReviewSerializer(instance.reviews_product.all(), many=True).data
        return reviews_data

    def get_tags(self, instance):
        tags_data = TagSerializer(instance.tags.all(), many=True).data
        return tags_data

    def get_images(self, instance):
        # Здесь формируем структуру данных для images
        return [
            {
                "src": instance.preview.url,  # URL изображения
                "alt": instance.title  # Описание изображения
            }
        ]

    def get_count(self, instance):
        # Получаем context, переданный при сериализации
        if self.context.get('get_basket'):
            basket_product = self.context.get('get_basket')
            if basket_product:
                return basket_product.quantity  # Используем quantity из BasketProduct
            return instance.count  # Или берем count из Product
        elif self.context.get('order_count_product'):
            count_order = self.context.get('order_count_product')
            return count_order
        elif self.context.get('post_basket'):
            product_count = self.context.get('post_basket')
            return product_count

        elif self.context.get('get_basket_anonymous'):
            basket_product = self.context.get('get_basket_anonymous')
            return basket_product
        else:
            return instance.count
