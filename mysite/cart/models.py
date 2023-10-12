from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _, ngettext
from products.models import Product


class Basket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='basket_user', verbose_name=_('user'),
                             blank=True, null=True)
    products = models.ManyToManyField(
        Product,
        through='BasketProduct',
        related_name='baskets',
        verbose_name=_('products')
    )

    class Meta:
        ordering = ('pk',)

    def __str__(self) -> str:
        return f"(pk={self.pk}, )"


class BasketProduct(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.product!r} in {self.basket!r}"
