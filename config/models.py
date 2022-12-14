from django.db import models
from datetime import datetime
from django.db.models import ForeignKey
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))

        user = self.model(
            email=self.normalize_email(email)
        )
        user.set_password(password)
        # user.set_is_staff(False)
        user.save()
        return user

    def create_superuser(self, email, password):
        """
        Create and save a SuperUser with the given email and password.
        """
        user = self.create_user(
                email=email,
                password=password
            )
        user.is_staff = True
        user.save()
        return user

class User(AbstractBaseUser, PermissionsMixin):
    class Roles(models.TextChoices):
        ADMIN = 'ADMIN'
        USER = 'USER'
        
    email = models.EmailField(unique=True, max_length=255)
    is_staff = models.BooleanField(default=False) #models.CharField(max_length=5, choices=Roles.choices, null=False, default="USER")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.email

class Image(models.Model):
    class Status(models.TextChoices):
        DELETE = 'DEL'
        EXIST = 'EXS'
        MODIFIED = 'MOD'

    user_id = ForeignKey(User, on_delete=models.CASCADE)
    url = models.URLField(max_length=254, null=False)
    status = models.CharField(max_length=3, choices=Status.choices, default="EXS", null=False)
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(auto_now=True)