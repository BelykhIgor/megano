from django.db import models

from products.models import Product


class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    dateFrom = models.DateField()
    dateTo = models.DateField()
    salePrice = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Sale (from {self.dateFrom} to {self.dateTo})"