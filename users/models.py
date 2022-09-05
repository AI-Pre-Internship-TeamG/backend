from datetime import datetime
from django.db import models


class Users(models.Model):
    class Roles(models.TextChoices):
        ADMIN = 'ADMIN'
        USER = 'USER'

    user_name = models.CharField(max_length=20)
    password = models.CharField(max_length=50)
    email = models.EmailField(max_length=50, null=False)
    role = models.CharField(max_length=5, choices=Roles.choices, null=False)
    status = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(auto_now=True)
