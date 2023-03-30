from rest_framework import serializers

from currency.models import RatesDay, RateDay


class RatesDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = RatesDay
        fields = "__all__"


class RateDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = RateDay
        fields = "__all__"
