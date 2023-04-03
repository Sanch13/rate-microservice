from datetime import date

from rest_framework import serializers

from currency.models import RatesDay, RateDay


class DateValidationMixin:
    def validate_date(self, value):
        min_date = date(1995, 3, 29)
        max_date = date.today()
        if not (min_date <= value <= max_date):
            raise serializers.ValidationError(f"Date should be between {min_date} and {max_date}")
        return value


class DateSerializer(serializers.Serializer, DateValidationMixin):
    date = serializers.DateField(validators=[DateValidationMixin().validate_date])


class DateUidSerializer(serializers.Serializer, DateValidationMixin):
    date = serializers.DateField(validators=[DateValidationMixin().validate_date])
    uid = serializers.IntegerField(min_value=1)


class RatesDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = RatesDay
        fields = "__all__"


class RateDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = RateDay
        fields = "__all__"
