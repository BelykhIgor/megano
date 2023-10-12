# Generated by Django 4.2.6 on 2023-10-09 19:10

from django.db import migrations, models
import django.db.models.deletion
import products.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ('pk',),
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='price')),
                ('count', models.PositiveIntegerField(default=0)),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='created_date')),
                ('title', models.CharField(blank=True, max_length=25)),
                ('description', models.TextField(blank=True, db_index=True, verbose_name='description')),
                ('fullDescription', models.TextField(blank=True, null=True, verbose_name='full description')),
                ('freeDelivery', models.BooleanField(default=False, verbose_name='free Delivery')),
                ('rating', models.DecimalField(decimal_places=1, default=0, max_digits=8)),
                ('limited', models.BooleanField(default=False, verbose_name='limited_product')),
                ('preview', models.ImageField(blank=True, default='products/default/default-image-product.jpeg', upload_to=products.models.product_preview_dir_path, verbose_name='preview_product')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_category', to='products.category', verbose_name='category')),
            ],
            options={
                'ordering': ('pk',),
            },
        ),
        migrations.CreateModel(
            name='Specifications',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=25, verbose_name='Наименование спецификации')),
                ('value', models.CharField(blank=True, max_length=25, verbose_name='Значение спецификации')),
            ],
            options={
                'ordering': ('pk',),
            },
        ),
        migrations.CreateModel(
            name='Subcategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ('pk',),
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=250, verbose_name='Наименование тега')),
            ],
            options={
                'ordering': ('pk',),
            },
        ),
        migrations.CreateModel(
            name='SubcategoryImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, upload_to=products.models.subcategory_preview_dir_path, verbose_name='subcategory_images')),
                ('src', models.CharField(blank=True, max_length=250, verbose_name='путь к изображению')),
                ('alt', models.CharField(blank=True, max_length=200, verbose_name='description')),
                ('subcategory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subcategory_images', to='products.subcategory', verbose_name='subcategory image')),
            ],
        ),
        migrations.CreateModel(
            name='Reviews',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.CharField(blank=True, max_length=25, verbose_name='Автор отзыва')),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('text', models.TextField(blank=True, verbose_name='Текст отзыва')),
                ('rate', models.PositiveIntegerField()),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Дата отзыва')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews_product', to='products.product', verbose_name='Связанный продукт')),
            ],
            options={
                'ordering': ('pk',),
            },
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('images', models.ImageField(blank=True, default='products/product_12/images/8cbc24cf8212671c0309b37c8.jpg', upload_to=products.models.product_image_directory_path, verbose_name='images')),
                ('src', models.CharField(blank=True, max_length=250)),
                ('alt', models.CharField(blank=True, max_length=200, verbose_name='description')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_images', to='products.product', verbose_name='product image')),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='reviews',
            field=models.ManyToManyField(blank=True, related_name='product_reviews', to='products.reviews'),
        ),
        migrations.AddField(
            model_name='product',
            name='specifications',
            field=models.ManyToManyField(blank=True, related_name='product_specifications', to='products.specifications'),
        ),
        migrations.AddField(
            model_name='product',
            name='subcategory',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='products_subcategory', to='products.subcategory', verbose_name='subcategory'),
        ),
        migrations.AddField(
            model_name='product',
            name='tags',
            field=models.ManyToManyField(related_name='product_tags', to='products.tag'),
        ),
        migrations.CreateModel(
            name='CategoryImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, upload_to=products.models.category_preview_dir_path, verbose_name='category_images')),
                ('src', models.CharField(blank=True, max_length=250)),
                ('alt', models.CharField(blank=True, max_length=200, verbose_name='description')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='category_images', to='products.category', verbose_name='category image')),
            ],
        ),
        migrations.AddField(
            model_name='category',
            name='subcategories',
            field=models.ManyToManyField(to='products.subcategory'),
        ),
    ]
