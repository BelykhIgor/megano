from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from myauth.models import Profile
from .models import Order, OrderItem
from .serializers import (
    OrderSerializer,
    ProductShortSerializer,
)
from products.models import Product
from cart.models import Basket, BasketProduct


class OrderView(GenericAPIView):
    """
    APIView класс создания заказа
    Из request получает список ID товаров из корзины и их количество.
    Создаёт заказ, добавляет к нему список товаров и возвращает ID заказа.
    Для анонимных пользователей - получает корзину из сессии, добавляет к нему список товар, возвращает ID заказа.
    """
    serializer_class = OrderSerializer

    def post(self, request: Request,  **kwargs) -> Response:
        user = request.user

        if user.is_authenticated:
            product_list = request.data  # Получение списка товаров из данных запроса
            # Создание заказа
            order = Order.objects.create(user=user)

            # Создание товаров для заказа

            for product_data in product_list:
                price = product_data.get('price')
                quantity = product_data.get('count')
                product = Product.objects.get(id=product_data['id'])  # Получить товар
                order_item = OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=price,
                    quantity=quantity
                )  # Создать запись о товаре в заказе
            data_res = {"orderId": order.id}

            return Response(data_res, status=status.HTTP_200_OK)
        else:  # Для анонимного пользователя
            session_basket = request.session.get('basket')  # Получаем корзину из сессии
            order = Order.objects.create()  # Создаем пустой заказ
            #  Добавляем товары к заказу из корзины сессии
            for product_id, quantity in session_basket.items():
                product = Product.objects.get(pk=product_id)

                order_item = OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=product.price,
                    quantity=quantity
                )  # Создать запись о товаре в заказе
            order_id = {"orderId": order.pk}

            return Response(order_id, status=status.HTTP_200_OK)

    def get(self, request: Request,  **kwargs) -> Response:
        user = request.user
        if user.is_authenticated:
            orders = Order.objects.filter(user=user)
            order_data = OrderSerializer(orders, many=True).data
            return Response(order_data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_200_OK)


class OrderConfirmView(GenericAPIView):
    """
    APIView класс получает от пользователя недостающую информацию для оформления и подтверждения заказа.
    deliveryType:  - ordinary - обычная доставка.
                   - express - ускоренная доставка.
    - fullName - полное имя пользователя
    - createdAt - время создания заказа
    - email  - электронная почта клиента
    - phone - контактный телефон клиента
    - products_data - список товаров в заказе
    - total_cost - общая стоимость заказа
    - order_id - ID заказа
    - user - заказчик
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get(self, request: Request, **kwargs) -> Response:
        products_data = []
        total_cost = 0
        order_id = kwargs.get('order_id')
        user = request.user

        if user.is_authenticated:
            session_basket = request.session.get('basket', {})
            #  После авторизации анонимного пользователя, проверяем есть ли корзина с товарами, и если есть то,
            #  объединяем с данными из корзины анонимной сессии, если нет, то создаем корзину.
            try:
                user_basket = Basket.objects.get(user=user)
            except Basket.DoesNotExist:
                user_basket = Basket.objects.create(user=user)

            for product_item, values in session_basket.items():  # Добавляем в корзину товары
                product = Product.objects.get(pk=product_item)
                basket_product, _ = BasketProduct.objects.get_or_create(basket=user_basket, product=product)
                basket_product.quantity += values
                basket_product.save()

            # request.session['basket'] = {}  # очищаем корзину анонимной сессии

            order = Order.objects.get(pk=order_id)  # Получаем заказ
            if not order.user_id:
                order.user_id = user.id
                order.save()
            order_items = order.items.all()  # Получаем список товаров в заказе

            for order_product in order_items:  # Собираем список товаров из корзины
                total_quantity_cost = order_product.quantity * order_product.price
                total_cost += total_quantity_cost

                serialized = ProductShortSerializer(
                    order_product.product,
                    context={'order_count_product': order_product.quantity}
                )
                products_data.append(serialized.data)
            try:
                user_data = Profile.objects.get(user=user)

                data_res = {
                  "id": order_id,
                  "createdAt": order.createdAt,
                  "fullName": user_data.fullName,
                  "email": user_data.email,
                  "phone": user_data.phone,
                  "deliveryType": '',
                  "paymentType": '',
                  "totalCost": total_cost,
                  "status": '',
                  "city": '',
                  "address": '',
                  "products": products_data,
                }
                return Response(data_res)
            except Profile.DoesNotExits:
                data_res = {
                    "id": order_id,
                    "createdAt": order.createdAt,
                    "fullName": '',
                    "email": '',
                    "phone": '',
                    "deliveryType": '',
                    "paymentType": '',
                    "totalCost": total_cost,
                    "status": '',
                    "city": '',
                    "address": '',
                    "products": products_data,
                }
                return Response(data_res)

        else:
            order_id = kwargs.get('order_id')
            return Response({"id": order_id})

    def post(self, request: Request, **kwargs) -> Response:
        order_id = kwargs.get('order_id')
        try:
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            return Response({'message': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        request_data = request.data
        order.fullName = request_data.get('fullName', order.fullName)
        order.email = request_data.get('email', order.email)
        order.phone = request_data.get('phone', order.phone)

        order.deliveryType = request_data.get('deliveryType', order.deliveryType)
        if order.deliveryType == "express":
            order.totalCost = request_data.get('totalCost', order.totalCost)
            order.totalCost += 500
        if order.deliveryType == "ordinary" and request_data.get('totalCost', order.totalCost) < 2000:
            order.totalCost = request_data.get('totalCost', order.totalCost)
            order.totalCost += 200
        elif order.deliveryType == "ordinary" and request_data.get('totalCost', order.totalCost) > 2000:
            order.totalCost = request_data.get('totalCost', order.totalCost)
        order.paymentType = request_data.get('paymentType', order.paymentType)
        order.city = request_data.get('city', order.city)
        order.address = request_data.get('address', order.address)
        if order.city and order.city.isalpha() and order.address:
            order.status = 'accepted'
            order.save()
            return Response(request_data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Address not is valid'}, status=status.HTTP_400_BAD_REQUEST)


