from django.db.models import F
from rest_framework.request import Request
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from .models import Basket, BasketProduct
from .serializers import  BasketSerializer, ProductShortSerializer
from products.models import Product


class BasketView(GenericAPIView):
    """
         APIView класс - корзина
         post - получает товар от пользователя и добавляет его в корзину
         Для авторизированных пользователей товар добавляется сразу в корзину.
         Для анонимных пользователей - корзина создается в сессии, а при авторизации
         пользователя переносится в полноценную корзину
         get_basket - Получение корзины пользователя
         get_session_basket - Получение корзины хранящейся в сессии
         delete - удаление товара из корзины
         count - кол-во добавляемого в корзину товара
         product_id - ID товара добавляемого в корзину
    """

    serializer_class = BasketSerializer

    def __init__(self):
        super().__init__()
        self.basket = None

    def post(self, request: Request,  **kwargs) -> Response:
        user = request.user
        request_data = request.data
        count = request_data['count']
        product_id = request_data['id']

        if user.is_authenticated:  # Добавляем товар если пользователь аутентифицирован
            try:
                product = Product.objects.get(id=product_id)
                basket, created = Basket.objects.get_or_create(user=user)
                # Необходимо проверить количество товара на складе перед добавлением в корзину
                if product.count > 0:
                    basket_product, created = BasketProduct.objects.get_or_create(basket=basket, product=product)
                    basket_product.quantity += count
                    basket_product.save()
                    product.count -= count
                    product.save()
                    serialized = ProductShortSerializer(product, context={'post_basket': count})
                    serializer_data = serialized.data
                    return Response(serializer_data, status=status.HTTP_201_CREATED)
                else:
                    return Response({'The product is out of stock'}, status=status.HTTP_404_NOT_FOUND)

            except Basket.DoesNotExist:
                Response({'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        else:  # Создаем корзину в сессии если пользователь анонимный
            if 'basket' not in request.session:
                request.session['basket'] = {}  # Если корзины нет в сессии, то создаем пустой словарь
            self.basket = request.session['basket']
            if product_id not in self.basket:
                self.basket[product_id] = 0  # Если товар еще не добавлен, устанавливаем начальное количество 0
            self.basket[product_id] += count
            request.session.modified = True

            return Response(self.basket, status=status.HTTP_201_CREATED)

    def get_basket(self, request: Request,  **kwargs) -> Response:
        # код для получения данных о корзине
        user = request.user
        response_data = []
        if user.is_authenticated:
            try:
                baskets = Basket.objects.get(user=user)  # Получаем корзину пользователя
            except Basket.DoesNotExist:
                return Response({"message": "Basket not found"}, status=status.HTTP_404_NOT_FOUND)
            basket_data = BasketProduct.objects.filter(basket_id=baskets.id)  # Получаем товары из корзины
            for basket_product in basket_data:
                product = basket_product.product
                serialized = ProductShortSerializer(product, context={'get_basket': basket_product})
                response_data.append(serialized.data)
            return Response(response_data)

        else:
            session_basket = self.get_session_basket(request)
            for product_id in session_basket:
                product = Product.objects.get(pk=product_id)
                serialized = ProductShortSerializer(
                    product,
                    context={'get_basket_anonymous': session_basket[product_id]}
                )
                basket_product_data = serialized.data
                response_data.append(basket_product_data)
            return Response(response_data)

    def get_session_basket(self, request: Request,  **kwargs):
        return request.session.get('basket', {})

    def get(self, request: Request,  **kwargs):
        return self.get_basket(request)

    def delete(self, request: Request,  **kwargs) -> Response:
        user = request.user
        request_data = request.data
        count = request_data['count']
        product_id = request_data['id']
        response_data = []
        delete_data = []

        if user.is_authenticated:  # Удаляем товар если пользователь аутентифицирован
            baskets = Basket.objects.get(user=user)
            basket_data = BasketProduct.objects.filter(product_id=product_id, basket_id=baskets.id)
            basket_data.update(quantity=F('quantity') - count)
            basket_data = basket_data.first()
            if basket_data.quantity <= 0:
                basket_data.delete()

        else:  # Удаляем товар если анонимный пользователь
            session_basket = self.get_session_basket(request)
            for product_id in session_basket:
                if product_id == request_data['id']:
                    session_basket[product_id] -= count
                    if session_basket[product_id] > 0:
                        product = Product.objects.get(pk=product_id)
                        serialized = ProductShortSerializer(product, context={
                            'get_basket_anonymous': session_basket[product_id]})
                        basket_product_data = serialized.data
                        response_data.append(basket_product_data)
                    else:
                        delete_data.append(product_id)
                else:
                    product = Product.objects.get(pk=product_id)
                    serialized = ProductShortSerializer(product, context={
                        'get_basket_anonymous': session_basket[product_id]})
                    basket_product_data = serialized.data
                    response_data.append(basket_product_data)

            for delete_product in delete_data:
                del session_basket[delete_product]

            request.session.modified = True

            return Response(response_data)
