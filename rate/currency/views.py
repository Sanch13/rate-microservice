from django.shortcuts import render
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

import requests

from currency.serializer import DateSerializer
from currency.utils import get_exchange_rates_on_date, get_body_on_date, \
    check_record_exists_by_date, get_crc32_from_body, check_record_exists_by_date_cur_id, \
    get_currency_rate_on_date, get_body_on_date_uid
from currency.models import RatesDay, RateDay
from logs.settings import logger_1


class RateDayAPIView(ListAPIView):
    serializer_class = DateSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        date = request.query_params.get("date")

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


class RateCurrencyDayAPIView(ListAPIView):
    serializer_class = DateSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        date = request.query_params.get("date")
        uid = request.query_params.get("uid")

        if check_record_exists_by_date_cur_id(date=date, uid=uid):
            logger_1.info(f"This instance is in the database. Display from the database")
            response_body = get_body_on_date_uid(date=date, uid=uid)
            headers = get_crc32_from_body(response_body)
            return Response(data=response_body, headers=headers, status=200)

        response = get_currency_rate_on_date(date=date, uid=uid)

        if isinstance(response, requests.exceptions.HTTPError):
            return Response(data={"message": f"Could not get the data, error: {response}"},
                            status=404)

        try:
            RateDay(date=date, cur_id=uid, data=response).save()
            logger_1.success("Saved in the DB")
            response_body = get_body_on_date_uid(date=date, uid=uid)
            headers = get_crc32_from_body(response_body)
            return Response(data=response_body, headers=headers, status=201)

        except Exception as error:
            logger_1.error(f"Could not save in the DataBase: {error}")
            return Response(
                data={"message": f"Error occurred while saving in the database: {error}"},
                status=422
            )


def index(request):
    return render(request, "currency/base.html")
