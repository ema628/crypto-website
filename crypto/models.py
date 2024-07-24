from django.db import models


# Create your models here.
class favouritePages(models.Model):
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    currency = models.CharField(max_length=200)
    time = models.CharField(max_length=200)
    




