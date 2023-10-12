from django.urls import path

from .views import OrderView, OrderConfirmView

app_name = 'orders'

urlpatterns = [
    path("orders/", OrderView.as_view()),
    path("order/<int:order_id>/", OrderConfirmView.as_view()),
]


