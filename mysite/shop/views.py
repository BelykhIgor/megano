from django.db.models import Count
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.paginator import Paginator
from rest_framework import status
from .models import Sale
from .serializers import SalesSerializer
from products.models import Product
from products.serializers import ProductShortSerializer


class SalesListView(APIView):  # Список товаров для распродажи
    """
    Данный APIView формирует список товаров из категории SALE
    """
    def get(self, request: Request,  **kwargs) -> Response:
        try:
            sales_data = Sale.objects.all()
        except Sale.DoesNotExist:
            return Response({"message": "Product sales  not found"}, status=status.HTTP_404_NOT_FOUND)
        products_list = []
        for sale in sales_data:
            if sale.product.count > 0:
                serialized = SalesSerializer(sale)
                products_list.append(serialized.data)

        items_per_page = 6  # Количество продуктов на странице
        paginator = Paginator(sales_data, items_per_page)
        current_page = request.query_params.get('currentPage')
        page = paginator.get_page(current_page)
        total_pages = paginator.num_pages
        response_data = self.get_sale_catalog(page, total_pages)
        return Response(response_data)

    def get_sale_catalog(self, page, total_pages):
        products = page.object_list
        serialized = SalesSerializer(products, many=True)
        product_data = {
            "items": serialized.data,
            "currentPage": page.number,
            "lastPage": total_pages
        }
        return product_data


class BannersListView(APIView):
    """
    APIView класс формирует список недавно добавленных товаров для баннера
    product_list - список товаров
    """
    product_list = []

    def get(self, request: Request) -> Response:
        newest_products = Product.objects.order_by('-date')[:3]
        serialized = ProductShortSerializer(newest_products, many=True)
        serialized_data = serialized.data
        return Response(serialized_data, status=status.HTTP_200_OK)


