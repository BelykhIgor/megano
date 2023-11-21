from django.core.management import BaseCommand
from products.models import Category, Subcategory, Product


class Command(BaseCommand):
    help = 'Создает тестовые продукты с категориями и подкатегориями'

    def create_product_with_category_and_subcategory(self, category_title, subcategory_title, product_data):
        category, created = Category.objects.get_or_create(title=category_title)
        subcategory = Subcategory.objects.get_or_create(title=subcategory_title, category=category)
        product = Product.objects.create(category=category, subcategory=subcategory, **product_data)

        return product

    def handle(self, *args, **options):
        products_data = [
            {
                'category_title': 'Комплектующие для ПК',
                'subcategory_title': 'Процессоры',
                'product_data': {
                    'price': 300.0,
                    'count': 10,
                    'title': 'Процессор AMD',
                    'description': 'This is an example product.',
                }
            },
            {
                'category_title': 'Жёсткие диски',
                'subcategory_title': 'SSD',
                'product_data': {
                    'price': 150.0,
                    'count': 10,
                    'title': 'SSD Disk',
                    'description': 'This is an example product.',
                }
            },
            {
                'category_title': 'Оргтехника',
                'subcategory_title': 'Принтеры',
                'product_data': {
                    'price': 80.0,
                    'count': 10,
                    'title': 'Принтер Canon',
                    'description': 'This is an example product.',
                }
            }
        ]

        for product_info in products_data:
            category_title = product_info['category_title']
            subcategory_title = product_info['subcategory_title']
            product_data = product_info['product_data']
            self.create_product_with_category_and_subcategory(category_title, subcategory_title, product_data)

        self.stdout.write(self.style.SUCCESS('Successfully created products'))
