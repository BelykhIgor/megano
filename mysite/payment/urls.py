from django.urls import path

from .views import PaymentView, PaymentSomeoneView

app_name = 'payment'

urlpatterns = [
    path("payment/<int:id>/", PaymentView.as_view()),
    path("payment-someone/", PaymentSomeoneView.as_view()),
    path("progress-payment/", PaymentSomeoneView.as_view()),
]


