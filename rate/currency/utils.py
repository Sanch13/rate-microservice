import json
import zlib
from datetime import date, timedelta

import requests

from currency.models import RatesDay

from currency.serializer import RatesDaySerializer
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
        return error


def get_exchange_rates_on_date(date: str) -> dict:
    """Return the list of rate for date"""
    url = URL_API_BANK
    params = {
        "ondate": date,
        "periodicity": 0
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
    """Return CRC from response_body"""
    crc = str(zlib.crc32(json.dumps(response_body).encode("utf-8")))
    headers = {"CRC32": crc}
    return headers


def check_record_exists_by_date(date: str) -> bool:
    """Return true if the record exists"""
    return RatesDay.objects.filter(date=date).exists()


def get_yesterday_date(day: date) -> str:
    """Return yesterday date by string"""
    yesterday = day - timedelta(days=1)
    yesterday = yesterday.strftime("%Y-%m-%d")
    return yesterday


def is_change(cur_rate, yesterday_rate):
    if yesterday_rate > cur_rate:
        return f"Курс снизился был {yesterday_rate}, а стал {cur_rate}"
    elif yesterday_rate < cur_rate:
        return f"Курс увеличился был {yesterday_rate}, а стал {cur_rate}"
    return f"Курс остался прежним"


def get_official_rate(data, uid: int):
    for obj in data:
        if obj.get('Cur_ID') == uid:
            return obj.get("Cur_OfficialRate")
