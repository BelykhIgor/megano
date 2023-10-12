from csv import DictReader
from io import TextIOWrapper
from .models import Product

from django.contrib.auth.models import User


def save_csv_product(file, encoding):
    csv_file = TextIOWrapper(
        file,
        encoding=encoding,
    )
    reader = DictReader(csv_file)

    products = [
        Product(**row)
        for row in reader
    ]
    Product.objects.bulk_create(products)
    return products