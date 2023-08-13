from datetime import datetime

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

#from users.models import User


class Recipe(models.Model):
    # author = models.ForeignKey(
    #     'users.User',
    # )
    title = models.CharField(
        max_length=200,
    )
    image = models.ImageField(
        upload_to='recipes/',
    )