from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    # Create and return a 'User' with an email and password.
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Hash the password
        user.save(using=self._db)
        return user

    # Create and return a superuser with an email and password.
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    email = models.EmailField(max_length=250, unique=True, verbose_name='email address')
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    objects = CustomUserManager()  # Link the custom user manager
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # Override groups and user_permissions to add unique related_name
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',  # Change to a unique name
        blank=True,
        help_text='The groups this user belongs to.'
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',  # Change to a unique name
        blank=True,
        help_text='Specific permissions for this user.'
    )
    
    USERNAME_FIELD = 'email'  # Use email as the username field
    REQUIRED_FIELDS = []  # Required fields when creating a user

    def __str__(self):
        return self.email