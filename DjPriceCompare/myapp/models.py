from re import T
from django.db import models
from  django.contrib.auth.models import User

# Create your models here.
class Register(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    mobile = models.CharField(max_length=10, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    image = models.FileField(null=True, blank=True)

    def __str__(self) -> str:
        return self.user.username


class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.TextField(null=True, default={'object':[]}, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.user.username