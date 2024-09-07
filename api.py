import argparse
import json
from datetime import datetime

from dateutil.relativedelta import relativedelta

from meteostat import Point, Daily

import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry


team_name = "tobytes()"


def dict_to_serializable(data: dict) -> dict:
    result = {"date": data["date"].strftime("%Y-%m-%d %H:%M:%S").tolist()}
    del data["date"]
    for key, value in data.items():
        if hasattr(value, "tolist"):
            result[key] = value.tolist()
        else:
            result[key] = value

    return result


def append_meteostat_to_openmeteo(openmeteo_data: dict, meteostat_data: dict):
    for key, value in meteostat_data.items():
        if key not in openmeteo_data:
            openmeteo_data[key] = []
        for v in value.values():
            openmeteo_data[key].append(v)


def get_weather_by_meteostat(lat: float, lng: float, date: datetime) -> dict:
    place = Point(lat, lng)
    start = date - relativedelta(months=1)
    end = date
    daily_data = Daily(place, start, end)
    fetched = daily_data.fetch()
    return fetched.to_dict()


def get_weather_by_openmeteo(lat: float, lng: float, date: datetime) -> dict:
    start = date - relativedelta(months=1)
    end = date

    cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lng,
        "start_date": start.strftime("%Y-%m-%d"),
        "end_date": end.strftime("%Y-%m-%d"),
        "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "temperature_2m_mean",
                  "apparent_temperature_max", "apparent_temperature_min", "apparent_temperature_mean", "sunrise",
                  "sunset", "daylight_duration", "sunshine_duration", "precipitation_sum", "rain_sum", "snowfall_sum",
                  "precipitation_hours", "wind_speed_10m_max", "wind_gusts_10m_max", "wind_direction_10m_dominant",
                  "shortwave_radiation_sum", "et0_fao_evapotranspiration"],
        "wind_speed_unit": "ms",
        "timezone": "auto"
    }
    responses = openmeteo.weather_api(url, params=params)

    daily = responses[0].Daily()
    daily_weather_code = daily.Variables(0).ValuesAsNumpy()
    daily_temperature_2m_max = daily.Variables(1).ValuesAsNumpy()
    daily_temperature_2m_min = daily.Variables(2).ValuesAsNumpy()
    daily_temperature_2m_mean = daily.Variables(3).ValuesAsNumpy()
    daily_apparent_temperature_max = daily.Variables(4).ValuesAsNumpy()
    daily_apparent_temperature_min = daily.Variables(5).ValuesAsNumpy()
    daily_apparent_temperature_mean = daily.Variables(6).ValuesAsNumpy()
    daily_sunrise = daily.Variables(7).ValuesAsNumpy()
    daily_sunset = daily.Variables(8).ValuesAsNumpy()
    daily_daylight_duration = daily.Variables(9).ValuesAsNumpy()
    daily_sunshine_duration = daily.Variables(10).ValuesAsNumpy()
    daily_precipitation_sum = daily.Variables(11).ValuesAsNumpy()
    daily_rain_sum = daily.Variables(12).ValuesAsNumpy()
    daily_snowfall_sum = daily.Variables(13).ValuesAsNumpy()
    daily_precipitation_hours = daily.Variables(14).ValuesAsNumpy()
    daily_wind_speed_10m_max = daily.Variables(15).ValuesAsNumpy()
    daily_wind_gusts_10m_max = daily.Variables(16).ValuesAsNumpy()
    daily_wind_direction_10m_dominant = daily.Variables(17).ValuesAsNumpy()
    daily_shortwave_radiation_sum = daily.Variables(18).ValuesAsNumpy()
    daily_et0_fao_evapotranspiration = daily.Variables(19).ValuesAsNumpy()

    daily_data = {
        "date": pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s", utc=True),
            end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left"
        ),
        "weather_code": daily_weather_code,
        "temperature_2m_max": daily_temperature_2m_max,
        "temperature_2m_min": daily_temperature_2m_min,
        "temperature_2m_mean": daily_temperature_2m_mean,
        "apparent_temperature_max": daily_apparent_temperature_max,
        "apparent_temperature_min": daily_apparent_temperature_min,
        "apparent_temperature_mean": daily_apparent_temperature_mean,
        # "sunrise": daily_sunrise,
        # "sunset": daily_sunset,
        "daylight_duration": daily_daylight_duration,
        "sunshine_duration": daily_sunshine_duration,
        "precipitation_sum": daily_precipitation_sum,
        "rain_sum": daily_rain_sum,
        "snowfall_sum": daily_snowfall_sum,
        "precipitation_hours": daily_precipitation_hours,
        "wind_speed_10m_max": daily_wind_speed_10m_max,
        "wind_gusts_10m_max": daily_wind_gusts_10m_max,
        "wind_direction_10m_dominant": daily_wind_direction_10m_dominant,
        "shortwave_radiation_sum": daily_shortwave_radiation_sum,
        "et0_fao_evapotranspiration": daily_et0_fao_evapotranspiration
    }

    return daily_data


def call_api(lat: float, lng: float, date: str) -> dict:
    date = datetime.strptime(date, "%Y-%m-%d")
    print(f"lat = {lat}, lng = {lng}, date = {date}")
    results_dict = {}

    weather_meteostat = get_weather_by_meteostat(lat, lng, date)
    weather_openmeteo = get_weather_by_openmeteo(lat, lng, date)
    append_meteostat_to_openmeteo(weather_openmeteo, weather_meteostat)
    results_dict.update(weather_openmeteo)
    result = dict_to_serializable(results_dict)

    return result


def save_json(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--lat", type=float, help="Широта")
    parser.add_argument("--lng", type=float, help="Долгота")
    parser.add_argument("--date", type=str, help="Дата в формате YYYY-MM-DD")
    args = parser.parse_args()

    if not all([args.lat, args.lng, args.date]):
        print("Не все обязательные аргументы предоставлены.")
        parser.print_help()
        exit(1)

    results = call_api(args.lat, args.lng, args.date)
    print(results)
    save_json(results, f'{team_name}.json')
