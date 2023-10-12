from django.db import models
from django.contrib.auth.models import User
from django.db import models
from PIL import Image


def product_preview_dir_path(instance: User, filename: str) -> str:
    print('url address', "users/user_{pk}/avatar/{filename}".format(
        pk=instance.pk,
        filename=filename
    ))
    return "users/user_{pk}/avatar/{filename}".format(
        pk=instance.pk,
        filename=filename
    )


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullName = models.TextField(max_length=500, blank=True)
    agreement_accepted = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    avatar = models.ImageField(null=True,
                               blank=True,
                               upload_to=product_preview_dir_path,
                               default='users/default/1681298893.jpg',
                               )

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.avatar.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.avatar.path)





