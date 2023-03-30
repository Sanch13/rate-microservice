from django.db import models


class RatesDay(models.Model):
    date = models.DateField()
    data = models.JSONField()


class RateDay(models.Model):
    date = models.DateField()
    cur_id = models.PositiveIntegerField()
    data = models.JSONField()
