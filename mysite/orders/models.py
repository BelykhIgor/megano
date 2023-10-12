from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _, ngettext

from products.models import Product


class Order(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True, verbose_name=_('created_at'))
    updated = models.DateTimeField(auto_now=True)
    fullName = models.CharField(max_length=50)
    email = models.EmailField()
    deliveryType = models.CharField(max_length=20, null=False, blank=True,  verbose_name=_('deliveryType'))
    paymentType = models.CharField(max_length=20, null=False, blank=True,  verbose_name=_('paymentType'))
    status = models.CharField(max_length=10)
    city = models.CharField(max_length=20, null=True, blank=True, verbose_name=_('city'))
    address = models.TextField(null=True, blank=True, verbose_name=_('delivery_address'))
    phone = models.CharField(max_length=20, blank=True)
    totalCost = models.DecimalField(null=True, max_digits=10, decimal_places=2, verbose_name=_('totalCost'))

    class Meta:
        ordering = ('-createdAt',)
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return 'Order {}'.format(self.id)

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return '{}'.format(self.id)