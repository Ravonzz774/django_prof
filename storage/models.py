import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class User(AbstractUser):
    username = models.EmailField(unique=True, max_length=256)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    password = models.CharField(max_length=256)

    files = models.ManyToManyField('File', related_name='users', blank=True, through='Access')

    REQUIRED_FIELDS = []

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'


class File(models.Model):
    file = models.FileField(upload_to='uploads/')
    filename = models.CharField(max_length=256)
    file_id = models.CharField(max_length=256)


class Access(models.Model):
    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)
    file = models.ForeignKey('File', on_delete=models.CASCADE)
    isOwner = models.BooleanField(default=False)
