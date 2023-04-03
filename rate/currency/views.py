from django.shortcuts import render
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.response import Response

import requests

from currency.serializer import DateSerializer, DateUidSerializer, RatesDaySerializer
from currency.utils import get_exchange_rates_on_date, get_body_on_date, \
    check_record_exists_by_date, get_crc32_from_body, get_yesterday_date, is_change, \
    get_official_rate
from currency.models import RatesDay
from logs.settings import logger_1


class RateDayAPIView(ListAPIView):
    serializer_class = DateUidSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        date = serializer.validated_data["date"]
        uid = serializer.validated_data["uid"]

        if check_record_exists_by_date(date=date) and check_record_exists_by_date(
                date=get_yesterday_date(date)):
            today_data = RatesDay.objects.get(date=date)
            today_rate = get_official_rate(data=today_data.data, uid=uid)
            yesterday_data = RatesDay.objects.get(date=get_yesterday_date(date))
            yesterday_rate = get_official_rate(data=yesterday_data.data, uid=uid)

            name_uid = [f"{i.get('Cur_Scale')} {i.get('Cur_Name')}" for i in today_data.data if i.get(
                    'Cur_ID') == uid]
            response_body = {
                "message": f"Currency rates for {date} loaded successfully",
                "is_change": is_change(cur_rate=today_rate, yesterday_rate=yesterday_rate),
                "data": f"{name_uid[0]} = {today_rate} BYN",
            }
            headers = get_crc32_from_body(response_body)
            return Response(data=response_body, headers=headers, status=200)

        return Response(data={"message": f"Could not get the data from the DB, "},
                        status=404)


class RatesDayAPIView(CreateAPIView):
    serializer_class = DateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        date = serializer.validated_data["date"]

        if check_record_exists_by_date(date=date):
            logger_1.info(f"This instance is in the database. Display from the database")
            response_body = get_body_on_date(date=date)
            headers = get_crc32_from_body(response_body)
            return Response(data=response_body, headers=headers, status=200)

        response = get_exchange_rates_on_date(date=date)

        if isinstance(response, requests.exceptions.HTTPError):
            return Response(data={"message": f"Could not get the data, error: {response}"},
                            status=404)

        try:
            RatesDay(date=date, data=response).save()
            logger_1.success("Saved in the DB")
            response_body = get_body_on_date(date=date)
            headers = get_crc32_from_body(response_body)
            return Response(data=response_body, headers=headers, status=201)

        except Exception as error:
            logger_1.error(f"Could not save in the DataBase: {error}")
            return Response(data={"message": "Error occurred while saving in the database"},
                            status=422)


def index(request):
    return render(request, "currency/base.html")
