from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _, ngettext
from django.conf import settings


def category_preview_dir_path(instance: "CategoryImage", filename: str) -> str:
    #  Формирует путь для сохранения изображения категории
    return "category/category_{pk}/preview_{filename}".format(
        pk=instance.category.pk,
        filename=filename
    )


def subcategory_preview_dir_path(instance: "SubcategoryImage", filename: str) -> str:
    #  Формирует путь для сохранения изображения подкатегории
    return "subcategory/subcategory_{pk}/preview_{filename}".format(
        pk=instance.subcategory.pk,
        filename=filename
    )


class SubcategoryImage(models.Model):
    subcategory = models.ForeignKey(
        'Subcategory',
        on_delete=models.CASCADE,
        related_name='subcategory_images',
        verbose_name=_('subcategory image')
    )
    image = models.ImageField(
        upload_to=subcategory_preview_dir_path,
        blank=True,
        verbose_name=_('subcategory_images')
    )
    src = models.CharField(max_length=250, null=False, blank=True, verbose_name='путь к изображению')
    alt = models.CharField(max_length=200, null=False, blank=True, verbose_name=_('description'))

    def save(self, *args, **kwargs):
        self.src = settings.MEDIA_URL + f'subcategory/subcategory_{self.subcategory.pk}/preview_{self.image.name}'
        self.alt = self.image.name
        super().save(*args, **kwargs)


class Subcategory(models.Model):
    title = models.CharField(max_length=255)

    class Meta:
        ordering = ('pk',)

    def __str__(self) -> str:
        return f"{self.title!r}  pk={self.pk} "


class CategoryImage(models.Model):
    category = models.ForeignKey(
        'Category',
        on_delete=models.CASCADE,
        related_name='category_images',
        verbose_name=_('category image')
    )
    image = models.ImageField(upload_to=category_preview_dir_path, blank=True, verbose_name=_('category_images'))
    src = models.CharField(max_length=250, null=False, blank=True)
    alt = models.CharField(max_length=200, null=False, blank=True, verbose_name=_('description'))

    def save(self, *args, **kwargs):
        self.src = settings.MEDIA_URL + f'category/category_{self.category.pk}/preview_{self.image.name}'
        self.alt = self.image.name
        super().save(*args, **kwargs)


class Category(models.Model):
    title = models.CharField(max_length=255)
    subcategories = models.ManyToManyField(Subcategory)

    class Meta:
        ordering = ('pk',)

    def __str__(self) -> str:
        return f"{self.title!r}  pk={self.pk} "


def product_image_directory_path(instance: 'ProductImage', filename: str) -> str:
    #  формирует путь для изображения товара
    return "products/product_{pk}/images/{filename}".format(
        pk=instance.product.pk,
        filename=filename,
    )


class ProductImage(models.Model):
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='product_images',
        verbose_name=_('product image')
    )
    images = models.ImageField(
        upload_to=product_image_directory_path,
        blank=True,
        verbose_name=_('images'),
        default='products/product_12/images/8cbc24cf8212671c0309b37c8.jpg'
                )
    src = models.CharField(max_length=250, null=False, blank=True)
    alt = models.CharField(max_length=200, null=False, blank=True, verbose_name=_('description'))

    def save(self, *args, **kwargs):
        self.src = settings.MEDIA_URL + f'products/product_{self.product.pk}/images/{self.images.name}'
        self.alt = self.product.title
        super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField(max_length=250, null=False, blank=True, verbose_name='Наименование тега')

    class Meta:
        ordering = ('pk',)

    def __str__(self) -> str:
        return f"{self.name!r}  pk={self.pk} "


class Specifications(models.Model):
    name = models.CharField(max_length=25, null=False, blank=True, verbose_name='Наименование спецификации')
    value = models.CharField(max_length=25, null=False, blank=True, verbose_name='Значение спецификации')

    class Meta:
        ordering = ('pk',)

    def __str__(self) -> str:
        return f"({self.pk}, {self.name!r}, {self.value})"


class Reviews(models.Model):
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='reviews_product',
        verbose_name='Связанный продукт'
    )
    author = models.CharField(max_length=25, null=False, blank=True, verbose_name='Автор отзыва')
    email = models.EmailField(blank=True)
    text = models.TextField(null=False, blank=True, verbose_name='Текст отзыва')
    rate = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата отзыва')

    class Meta:
        ordering = ('pk',)

    def __str__(self) -> str:
        return f"Reviews(pk={self.pk}, name={self.author!r})"


def product_preview_dir_path(instance: "Category", filename: str) -> str:
    return "products/{category}/preview_{filename}".format(
        category=instance.category.pk,
        filename=filename
    )


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='product_category',
        verbose_name=_('category')
    )
    subcategory = models.ForeignKey(
        Subcategory,
        default=1,
        on_delete=models.CASCADE,
        related_name='products_subcategory',
        verbose_name=_('subcategory')
    )
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2, verbose_name=_('price'))
    count = models.PositiveIntegerField(default=0)  # Кол-во товара на складе
    date = models.DateTimeField(auto_now_add=True, verbose_name=_('created_date'))
    title = models.CharField(max_length=25, null=False, blank=True)
    description = models.TextField(null=False, blank=True, verbose_name=_('description'), db_index=True)
    fullDescription = models.TextField(null=True, blank=True, verbose_name=_('full description'))
    freeDelivery = models.BooleanField(default=False, verbose_name=_('free Delivery'))
    tags = models.ManyToManyField(Tag, related_name='product_tags')
    reviews = models.ManyToManyField(Reviews, blank=True, related_name='product_reviews')
    specifications = models.ManyToManyField(Specifications, blank=True, related_name='product_specifications')
    rating = models.DecimalField(default=0, max_digits=8, decimal_places=1)
    limited = models.BooleanField(default=False, verbose_name=_('limited_product'))
    preview = models.ImageField(
        upload_to=product_preview_dir_path,
        blank=True,
        verbose_name=_('preview_product'),
        default='products/default/default-image-product.jpeg'
    )

    class Meta:
        ordering = ('pk',)

    def __str__(self) -> str:
        return f"(pk={self.pk}, {self.title!r})"

    @receiver(post_save, sender=Reviews)
    def update_product_rating(sender, instance, **kwargs):
        # Получаем средний рейтинг для продукта на основе всех отзывов
        average_rating = sender.objects.filter(product=instance.product).aggregate(Avg('rate'))['rate__avg']

        # Обновляем поле `rating` в связанной модели `Product`
        product = instance.product
        product.rating = round(average_rating, 1) if average_rating is not None else 0.0
        product.save()
