from django.db import models


class TestModel(models.Model):
    class Meta:
        app_label = 'tests'

    a = models.CharField(max_length=255)
    b = models.IntegerField(unique=True)
