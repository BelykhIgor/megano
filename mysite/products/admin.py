from django.contrib import admin
from django.shortcuts import render, redirect
from .common import save_csv_product
from .forms import CSVImportForms
from .models import (
    Product,
    Category,
    Subcategory,
    Tag,
    Reviews,
    Specifications,
    ProductImage,
    CategoryImage,
    SubcategoryImage,
)
from django.http import HttpRequest, HttpResponse
from .admin_mixins import ExportAsCSVMixin
from django.urls import path


class CategoryInline(admin.StackedInline):
    model = CategoryImage


# @admin.register(Sale)
# class SaleAdmin(admin.ModelAdmin):
#     list_display = ('product', 'dateFrom', 'dateTo', 'salePrice')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = 'pk', 'title'
    list_display_links = 'pk', 'title'
    inlines = [
        CategoryInline,
    ]
    fieldsets = (
        (None, {
            'fields': (
                'title',
                # 'subcategories',
            )
        }),
    )


class SubcategoryInline(admin.StackedInline):
    model = SubcategoryImage


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = 'pk', 'title'
    list_display_links = 'pk', 'title'

    inlines = [
        SubcategoryInline,
    ]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = 'pk', 'name'
    list_display_links = 'pk', 'name'


@admin.register(Reviews)
class ReviewsAdmin(admin.ModelAdmin):
    list_display = 'pk', 'author', 'email', 'rate',
    list_display_links = 'pk', 'author', 'email'


# class BasketProductInline(admin.TabularInline):
#     model = BasketProduct
#     extra = 1
#
#
# @admin.register(Basket)
# class BasketAdmin(admin.ModelAdmin):
#     list_display = ('user', 'total_quantity', 'total_price')
#     inlines = [BasketProductInline]
#
#     def total_quantity(self, obj):
#         return sum(item.quantity for item in obj.basketproduct_set.all())
#
#     def total_price(self, obj):
#         return sum(item.product.price * item.quantity for item in obj.basketproduct_set.all())
#
#     total_quantity.short_description = 'Total Quantity'
#     total_price.short_description = 'Total Price'


@admin.register(Specifications)
class SpecificationAdmin(admin.ModelAdmin):
    list_display = 'pk', 'name', 'value'
    list_display_links = 'pk', 'name'
    search_fields = 'name', 'value'


class ProductInline(admin.StackedInline):
    model = ProductImage


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, ExportAsCSVMixin):
    change_list_template = "products/products_changelist.html"
    actions = [
        'export_csv'
    ]
    inlines = [
        ProductInline,
    ]

    list_display = 'pk', 'title', 'description', 'price', 'count', 'limited'
    list_display_links = 'pk', 'title'
    search_fields = 'title', 'description', 'price'

    fieldsets = (
        (None, {
            'fields': (
                'title',
                'category',
                'subcategory',
                'price',
                'count',
                'description',
                'specifications',
                'freeDelivery',
                'tags',
                'preview',
            )
        }),
        ('Advanced Options', {
            'classes': ('collapse',),
            'fields': ('fullDescription', 'rating', 'limited')
        }),
    )

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == 'GET':
            form = CSVImportForms()
            context = {
                'form': form,
            }
            return render(request, 'admin/csv_form.html', context)
        form = CSVImportForms(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                'form': form,
            }
            return render(request, 'admin/csv_form.html', context, status=400)
        save_csv_product(
            form.file['csv_file'].file,
            encoding=request.encoding,
        )
        self.message_user(request, 'Data from CSV was imported')
        return redirect("..")

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                "import-products-csv/",
                self.import_csv,
                name="import_products_csv",
            )
        ]
        return new_urls + urls


# class OrderItemInline(admin.TabularInline):
#     model = OrderItem
#     raw_id_fields = ['product']
#
#
# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = [
#         'id',
#         'fullName',
#         'email',
#         'address',
#         'city',
#         'status',
#         'createdAt',
#         'updated'
#     ]
#
#     list_filter = ['status', 'createdAt', 'updated']
#     inlines = [OrderItemInline]
#
#
