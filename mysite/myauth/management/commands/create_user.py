from django.contrib.auth.models import User, Group
from django.core.management import BaseCommand
from faker import Faker


class Command(BaseCommand):
    """
    Функция для создания тестовых пользователей с простым паролем и случайными именами.
    """
    def handle(self, *args, **kwargs):
        password = '123456'
        names = []
        for name in range(1, 5):
            fake = Faker()
            random_name = fake.first_name()
            names.append(User(username=random_name, password=password))
        User.objects.bulk_create(names)