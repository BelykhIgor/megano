from rest_framework import serializers
from django.contrib.auth.models import User
from myauth.serializers import ProfileOrderSerializers
from .models import (
    Product,
    Category,
    Subcategory,
    Tag,
    Reviews,
    Specifications,
    ProductImage,
    CategoryImage,
    SubcategoryImage,
)
from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size = 5
    page_query_param = 'currentPage'
    max_page_size = 10


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class SubcategoryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubcategoryImage
        fields = [
            'src', 'alt'
        ]


class CategoryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryImage
        fields = [
            'src', 'alt'
        ]


class SubcategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Subcategory
        fields = ('id', 'title', 'image')

    def get_image(self, instance):
        image_data = SubcategoryImageSerializer(instance.subcategory_images.all(), many=True).data
        return image_data[0] if image_data else {}


class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubcategorySerializer(many=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'title', 'image', 'subcategories')

    def get_image(self, instance):
        image_data = CategoryImageSerializer(instance.category_images.all(), many=True).data
        return image_data[0] if image_data else {}


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reviews
        fields = ['author', 'email', 'text', 'rate', 'date']


class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specifications
        fields = ['name', 'value']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = [
            'src', 'alt'
        ]


class ProductLimitedSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    subcategoryProduct = SubcategorySerializer()

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'subcategory', 'price', 'count', 'date',
            'title', 'description', 'fullDescription', 'freeDelivery',
            'limited'
        ]


class ProductFullSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(source='product_images', many=True)
    tags = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    specifications = SpecificationSerializer(many=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'category',
            'subcategory',
            'price',
            'count',
            'date',
            'title',
            'description',
            'fullDescription',
            'images',
            'freeDelivery',
            'tags',
            'reviews',
            'specifications',
            'rating'
        ]

    def get_reviews(self, instance):
        reviews_data = ReviewSerializer(instance.reviews_product.all(), many=True).data
        return reviews_data

    def get_tags(self, instance):
        tags_data = TagSerializer(instance.tags.all(), many=True).data
        return tags_data

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if not data.get('images'):
            # Если 'images' пустое, подставляем путь к дефолтному изображению
            default_image_path = '/media/products/default/default-image-product.jpeg'
            data['images'] = [{'src': default_image_path, 'alt': 'Image alt string'}]

        return data


# class ProductShortSerializer(serializers.ModelSerializer):
#     images = ProductImageSerializer(source='product_images', many=True)
#     tags = serializers.SerializerMethodField()
#     reviews = serializers.SerializerMethodField()
#     category = serializers.CharField(source='category.id')
#     count = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Product
#         fields = [
#             'id',
#             'category',
#             'price',
#             'count',
#             'date',
#             'title',
#             'description',
#             'freeDelivery',
#             'images',
#             'tags',
#             'reviews',
#             'rating'
#         ]
#
#     def get_reviews(self, instance):
#         reviews_data = ReviewSerializer(instance.reviews_product.all(), many=True).data
#         return reviews_data
#
#     def get_tags(self, instance):
#         tags_data = TagSerializer(instance.tags.all(), many=True).data
#         return tags_data
#
#     def get_count(self, instance):
#         # Получаем context, переданный при сериализации
#         if self.context.get('get_basket'):
#             basket_product = self.context.get('get_basket')
#             if basket_product:
#                 return basket_product.quantity  # Используем quantity из BasketProduct
#             return instance.count  # Или берем count из Product
#         elif self.context.get('order_count_product'):
#             count_order = self.context.get('order_count_product')
#             return count_order
#         elif self.context.get('post_basket'):
#             product_count = self.context.get('post_basket')
#             return product_count
#
#         elif self.context.get('get_basket_anonymous'):
#             basket_product = self.context.get('get_basket_anonymous')
#             return basket_product
#

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


# class ProductPopularSerializer(serializers.ModelSerializer):
#     tags = TagSerializer(many=True)
#     reviews = ReviewSerializer(many=True)
#
#     class Meta:
#         model = Product
#         fields = [
#             'id',
#             'price',
#             'count',
#             'date',
#             'title',
#             'description',
#             'freeDelivery',
#             'tags',
#             'reviews',
#             'rating'
#         ]


class CustomDateSerializer(serializers.Serializer):
    def to_representation(self, value):
        return value.strftime('%m-%d')


# class SalesSerializer(serializers.ModelSerializer):
#     id = serializers.IntegerField(source='product.id')
#     price = serializers.DecimalField(max_digits=10, decimal_places=2, source='product.price')
#     salePrice = serializers.DecimalField(max_digits=10, decimal_places=2)
#     dateFrom = CustomDateSerializer()
#     dateTo = CustomDateSerializer()
#     title = serializers.CharField(source='product.title')
#     images = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Sale
#         fields = [
#             'id', 'price', 'salePrice',  'dateFrom', 'dateTo', 'title', 'images'
#         ]
#
#     def get_images(self, obj):
#         image_data = ProductImageSerializer(obj.product.product_images.all(), many=True).data
#         return [image_data[0] if image_data else {}]


# class CatalogSerializer(serializers.ModelSerializer):
#     images = ProductImageSerializer(many=True, required=False)
#
#     class Meta:
#         model = Product
#         fields = ['category', 'price', 'count', 'date', 'title', 'description', 'freeDelivery',
#                   'images', 'tags', 'reviews', 'rating'
#                   ]


# class OrderItemSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = OrderItem
#         fields = ['product', 'price', 'quantity']


# class OrderSerializer(serializers.ModelSerializer):
#     fullName = ProfileOrderSerializers()
#     email = ProfileOrderSerializers()
#     phone = ProfileOrderSerializers()
#
#     class Meta:
#         model = Order
#         fields = [
#             'id',
#             'createdAt',
#             'fullName',
#             'email',
#             'phone',
#             'deliveryType',
#             'paymentType',
#             'totalCost',
#             'status',
#             'city',
#             'address',
#         ]


# class BasketSerializer(serializers.ModelSerializer):
#     user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
#     session = serializers.CharField(required=False)
#
#     class Meta:
#         model = Basket
#         fields = ['user', 'session']
