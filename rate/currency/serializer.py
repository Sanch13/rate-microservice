from rest_framework import serializers

from currency.models import RatesDay


class RatesDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = RatesDay
        fields = "__all__"
