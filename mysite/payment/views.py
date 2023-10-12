
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status

from cart.models import Basket


class PaymentView(APIView):
    """
    APIView класс получает из request платежные данные
    - card_number - номер карты
    - month/year- месяц и год срока действия карты
    - cvv_code - секретный код безопасности карты
    - user_name - Имя и фамилия держателя карты
    delete_basket - метод удаления корзины
    """

    def post(self, request: Request, **kwargs) -> Response:
        payment_data = request.data
        card_number = payment_data['number']
        month = payment_data['month']
        cvv_code = payment_data['code']
        year = payment_data['year']
        user_name = payment_data['name']
        print(card_number, 'card_number')

        # Проверка валидности платежных данных
        if card_number.isdigit() \
                and len(card_number) == 16 \
                and int(card_number[15]) != 0 \
                and int(card_number[0]) != 0:
            print('The card number is correct')
            if 1 <= int(month) <= 12:
                print('The month is correct')
                if year.isdigit():
                    print('The year is correct')
                    if len(cvv_code) == 3 and int(cvv_code[0]) != 0 and int(cvv_code[2]) != 0:
                        print('CVV correct')
                        for name in user_name.split():
                            if not name.isalpha():
                                print('Name incorrect')
                            else:
                                self.delete_basket(request)
                                return Response({'Payment was successful'}, status=status.HTTP_200_OK)
        return Response({'Wrong data'}, status=status.HTTP_400_BAD_REQUEST)

    def delete_basket(self, request):  # Удаляем корзину после оплаты заказа
        user = request.user
        basket = Basket.objects.filter(user=user)
        basket.delete()
        if 'basket' in request.session:
            del request.session['basket']


class PaymentSomeoneView(APIView):
    def get(self, request, *args, **kwargs):
        print('request someone', request)

    def post(self, request, *args, **kwargs):
        print('request someone', request)