from django.db import models


class RatesDay(models.Model):
    date = models.DateField()
    data = models.JSONField()
