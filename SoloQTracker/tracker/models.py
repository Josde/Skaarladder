from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class User(AbstractUser): # Override user model for future use, just in case. See: https://docs.djangoproject.com/en/4.0/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project
    pass 