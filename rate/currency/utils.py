import json
import zlib
from datetime import date, timedelta

import requests

from currency.models import RatesDay, RateDay

from currency.serializer import RatesDaySerializer, RateDaySerializer
from logs.settings import logger_1

URL_API_BANK = "https://www.nbrb.by/api/exrates/rates/"


def try_get_data_from_bank(url: str, params: dict):
    try:
        logger_1.info("API request to bank")
        response = requests.get(url=url, params=params)
        response.raise_for_status()
        logger_1.success("API request to bank completed successfully")
        return response.json()
    except requests.exceptions.HTTPError as error:
        logger_1.error(f"Could not get the data, error: {error}")
        return {"message": f"API request to bank with status {error}"}


def get_exchange_rates_on_date(date: str) -> dict:
    """Return the list of rate for date"""
    url = URL_API_BANK
    params = {
        "ondate": date,
        "periodicity": 0
    }
    return try_get_data_from_bank(url=url, params=params)


def get_currency_rate_on_date(date: str, uid: str) -> dict:
    """Return currency rate on date"""
    url = URL_API_BANK + uid
    params = {
        "ondate": date,
    }
    return try_get_data_from_bank(url=url, params=params)


def get_body_on_date(date: str) -> dict:
    """Return response_body"""
    cur_data = RatesDay.objects.get(date=date)
    response_body = {
        "message": f"Currency rates for {date} loaded successfully",
        "data": RatesDaySerializer(cur_data).data
    }
    return response_body


def get_crc32_from_body(response_body: dict) -> dict:
    """Return CRC from response_body in headers"""
    crc = str(zlib.crc32(json.dumps(response_body).encode("utf-8")))
    headers = {"CRC32": crc}
    return headers


def check_record_exists_by_date(date: str) -> bool:
    """Return true if the record exists"""
    return RatesDay.objects.filter(date=date).exists()


def check_record_exists_by_date_cur_id(date: str, uid: str) -> bool:
    """Return true if the record exists"""
    return RateDay.objects.filter(date=date, cur_id=uid).exists()


def get_body_on_date_uid(date: str, uid: str):
    """Return response_body, headers objects"""
    cur_data = RateDay.objects.get(date=date, cur_id=uid)
    response_body = {
        "message": f"Currency rate for {date} loaded successfully",
        "Has rate change?": compare_currency_rate(cur_date=cur_data.date,
                                                  cur_id=cur_data.data.get("Cur_ID"),
                                                  cur_rate=cur_data.data.get("Cur_OfficialRate")),
        "data": RateDaySerializer(cur_data).data,
    }
    return response_body


def compare_currency_rate(cur_date: date, cur_id: int, cur_rate: float):
    """Return str. Comparing courses yesterday and today """
    url = URL_API_BANK + str(cur_id)
    params = {
        "ondate": get_yesterday_date(cur_date),
    }
    try:
        logger_1.info("API request to bank")
        yesterday_response = requests.get(url=url, params=params)
        yesterday_response.raise_for_status()
        logger_1.success("API request to bank completed successfully")
        yesterday_rate = yesterday_response.json().get('Cur_OfficialRate')
        if yesterday_rate > cur_rate:
            return f"Курс снизился был {yesterday_rate}, а стал {cur_rate}"
        elif yesterday_rate < cur_rate:
            return f"Курс увеличился был {yesterday_rate}, а стал {cur_rate}"
        return f"Курс остался прежним"

    except requests.exceptions.HTTPError as error:
        logger_1.error(f"Could not get the data, error: {error}")
        return {"message": f"API request to bank with status {error}"}


def get_yesterday_date(day: date) -> str:
    """Return yesterday date by string"""
    yesterday = day - timedelta(days=1)
    yesterday = yesterday.strftime("%Y-%m-%d")
    return yesterday
