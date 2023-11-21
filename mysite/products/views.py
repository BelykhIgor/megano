import json
from django.db.models import F
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from .models import Category, Tag
from django.core.paginator import Paginator
from django.db.models import Count
from rest_framework import status

from myauth.models import Profile
from .models import (
    Product
)
from .serializers import (
    CategorySerializer,
    ReviewSerializer,
    ProductLimitedSerializer,
    ProductFullSerializer,
    ProductShortSerializer,
    TagSerializer,
)


class TagListView(APIView):
    """
    Данный APIView возвращает список тегов
    tags_data - словарь с тегами для серилизации
    tags_response - серилизованный ответ с тегами
    """
    def get(self, request: Request,  **kwargs) -> Response:
        popular_tags = Tag.objects.annotate(tag_count=Count('product_tags')).order_by('-tag_count')[:10]
        tags_data = [{'id': tag.id, 'name': tag.name} for tag in list(popular_tags)]
        serialized = TagSerializer(data=tags_data, many=True)
        if serialized.is_valid():
            tags_response = serialized.data
            return Response(tags_response)
        else:
            errors = serialized.errors  # Получение информации о всех ошибках валидации
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)


class PopularProductListView(APIView):
    """
    Данный APIView формирует список популярных товаров на основе их среднего рейтинга
    """
    def get(self, request: Request,  **kwargs) -> Response:
        try:
            products = Product.objects.order_by('-rating')[:8]
        except Product.DoesNotExist:
            return Response({"message": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        serialized = ProductShortSerializer(products, many=True)
        popular_products_data = serialized.data
        return Response(popular_products_data, status=status.HTTP_200_OK)


class CatalogListView(GenericAPIView):  # Список товаров общего каталога
    """
    APIView класс формирует каталог общий каталог товаров, а также с применением фильтра
    min_price - минимальная цена
    max_price - максимальная цена
    free_delivery - бесплатная доставка
    available - товары в наличии
    sort_by - фильтрация по цене (с начала дешевые или наоборот)
    sort_type - маркер фильтрации по цене
    limit - товары из лимитированной серии
    catalog_num - номер каталога
    """
    serializer_class = ProductShortSerializer

    def get(self, request: Request,  **kwargs) -> Response:
        print('CATALOG', request.GET, kwargs)
        name_filter = request.query_params.get('filter[name]')
        min_price = request.query_params.get('filter[minPrice]')
        max_price = request.query_params.get('filter[maxPrice]')
        available = request.query_params.get('filter[available]')
        sort_by = request.query_params.get('sort')
        sort_type = request.query_params.get('sortType')
        catalog_num = request.query_params.get('category')
        try:
            products_queryset = Product.objects.all()
        except Product.DoesNotExist:
            return Response({"message": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        if catalog_num:
            products_queryset = products_queryset.filter(category_id=catalog_num)

        if name_filter:
            products_queryset = products_queryset.filter(title__icontains=name_filter)

        if min_price:
            products_queryset = products_queryset.filter(price__gte=min_price)

        if max_price:
            products_queryset = products_queryset.filter(price__lte=max_price)

        free_delivery = request.query_params.get('filter[freeDelivery]')
        if free_delivery == 'true':
            products_queryset = products_queryset.filter(freeDelivery=True)

        if available == 'true':
            products_queryset = products_queryset.filter(count__gt=0)

        if sort_by:
            if sort_type == 'inc':
                products_queryset = products_queryset.order_by(sort_by)
            else:
                products_queryset = products_queryset.order_by(f'-{sort_by}')

        items_per_page = 6  # Количество продуктов на странице
        paginator = Paginator(products_queryset, items_per_page)
        current_page = request.query_params.get('currentPage')
        page = paginator.get_page(current_page)
        total_pages = paginator.num_pages
        response_data = self.get_catalog_response(page, total_pages)
        return Response(response_data)

    def get_catalog_response(self, page, total_pages):
        products = page.object_list
        serialized = ProductShortSerializer(products, many=True)
        product_data = {
            "items": serialized.data,
            "currentPage": page.number,
            "lastPage": total_pages
        }
        return product_data


class CategoryView(APIView):
    """
    APIView класс, получает список категорий товаров
    """
    def get(self, request: Request,  **kwargs) -> Response:
        categories = Category.objects.all()
        serialized = CategorySerializer(categories, many=True)
        categories_data = serialized.data
        return Response(categories_data)


class ProductDetailView(GenericAPIView):
    """
    APIView класс формирует детальную информацию о товаре
    """
    serializer_class = ProductFullSerializer

    def get(self, request: Request, **kwargs) -> Response:
        try:
            product_queryset = Product.objects.get(pk=kwargs.get('product_id'))
        except Product.DoesNotExist:
            return Response({"message": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        serialized = ProductFullSerializer(product_queryset)
        return Response(serialized.data)


class ProductsLimitedView(GenericAPIView):
    """
      APIView класс формирует список товаров лимитированной серии
      """
    serializer_class = ProductLimitedSerializer

    def get(self, request):
        try:
            product_queryset = Product.objects.filter(limited=True)
        except Product.DoesNotExist:
            return Response({"message": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        serialized = ProductShortSerializer(product_queryset, many=True)
        product_limited = serialized.data
        return Response(product_limited, status=status.HTTP_200_OK)


class ProductReviewListView(GenericAPIView):
    """
      APIView класс получает отзыв о товаре и связывает их вместе, формируя список отзывов о конкретном товаре
      product - товар полученный по ID из request
      review - серилизованный отзыв
      """

    def post(self, request: Request, **kwargs) -> Response:
        try:
            product = Product.objects.get(pk=kwargs['product_id'])
        except Product.DoesNotExist:
            return Response({"message": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        serialized = ReviewSerializer(data=request.data)
        if serialized.is_valid():
            serialized.validated_data["product"] = product  # Устанавливаем продукт в отзыве
            review = serialized.save()  # Сохраняем отзыв с установленным продуктом
            return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)
        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)
