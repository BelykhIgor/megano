from django.urls import path

from .views import (
    SalesListView,
    BannersListView,
)

app_name = 'shop'

urlpatterns = [
    path("sales", SalesListView.as_view()),
    path("banners", BannersListView.as_view()),
]


