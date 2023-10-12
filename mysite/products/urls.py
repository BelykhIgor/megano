from django.urls import path

from .views import (
    CategoryView,
    CatalogListView,
    ProductDetailView,
    ProductsLimitedView,
    PopularProductListView,
    ProductReviewListView,
    TagListView,
)

app_name = 'products'

urlpatterns = [
    path("categories/", CategoryView.as_view()),
    path("catalog/", CatalogListView.as_view()),
    path("product/<int:product_id>/", ProductDetailView.as_view()),
    path("product/<int:product_id>/reviews/", ProductReviewListView.as_view()),
    path("products/limited/", ProductsLimitedView.as_view()),
    path("products/popular/", PopularProductListView.as_view()),
    path("tags/", TagListView.as_view()),

]


