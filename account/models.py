from django.db import models
from django.contrib.auth.models import User
from shared.models import TimestampMixin

# Create your models here.
class CustomerProfile(TimestampMixin):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='customer_profile',
    )
    phone = models.CharField(max_length=20, blank=True)
    profile_image = models.ImageField(
        upload_to='profile_images/',
        blank=True,
        null=True,
    )
    address = models.CharField(max_length=20, blank=True,null=True)

    def __str__(self):
        return self.user.get_username()

