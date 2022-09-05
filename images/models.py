from django.db import models
from datetime import datetime
from django.db.models import ForeignKey

# from ..users import User


# class Image(models.Model):
#     class Status(models.TextChoices):
#         DELETE = 'DEL'
#         EXIST = 'EXS'
#         MODIFIED = 'MOD'

#     user_id = ForeignKey(User, on_delete=models.CASCADE)
#     url = models.URLField(max_length=254, null=False)
#     status = models.CharField(max_length=3, choices=Status.choices, null=False)
#     created_at = models.DateTimeField(default=datetime.now)
#     updated_at = models.DateTimeField(auto_now=True)