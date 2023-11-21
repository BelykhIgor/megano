from django.urls import path

from .views import  BasketView

app_name = 'cart'

urlpatterns = [
       path("basket", BasketView.as_view()),
]


