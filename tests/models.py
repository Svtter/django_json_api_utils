from django.db import models


class ModelForTesting(models.Model):
    a = models.CharField(max_length=255)
    b = models.IntegerField(unique=True)
