from django.contrib.auth.models import AbstractUser
from django.db import models


class ViolencePredictionUser(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    gender = models.CharField(
        max_length=10,
        choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]
    )
    dob = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.username
