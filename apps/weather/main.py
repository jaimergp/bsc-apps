"""
weather.py

Weather      | Abbreviation
-------------+--------------
Snow         | sn
Sleet        | sl
Hail         | h
Thunderstorm | t
Heavy Rain   | hr
Light Rain   | lr
Showers      | s
Heavy Cloud  | hc
Light Cloud  | lc
Clear        | c
"""

import sys
from pathlib import Path
import argparse

import requests

HERE = Path(__file__).resolve().parent
METAWEATHER = "https://www.metaweather.com/api/"

WEATHER_TO_IMAGE = {
    "sn": "snow.png",
    "h": "snow.png",
    "t": "storm.png",
    "hr": "rain.png",
    "lr": "rain.png",
    "s": "rain.png",
    "hc": "cloudy.png",
    "lc": "sunny.png",
    "c": "sunny.png",
}


def find_location(query):
    r = requests.get(f"{METAWEATHER}/location/search/?query={query}")
    r.raise_for_status()
    data = r.json()
    return data["woeid"]


def current_weather(whereonearth):
    if isinstance(whereonearth, str):  # this is a query, find the WhereOnEarth ID
        whereonearth = find_location(whereonearth)
    assert isinstance(whereonearth, int), "Location must be a WhereonEarth ID"
    r = requests.get(f"{METAWEATHER}/location/{whereonearth}/")
    r.raise_for_status()
    data = r.json()
    print(data)
    return data["consolidated_weather"][0]["weather_state_abbr"]


def update_banner(server, image_path):
    pass


def parse_cli():
    p = argparse.ArgumentParser()
    p.add_argument("location", type=str, help="Place to obtain weather information for")
    p.add_argument("--server", help="Discord server where you want to update the banner.")


def main(server, location, default_banner=None):
    weather = current_weather(location)
    imgpath = HERE / "data" / WEATHER_TO_IMAGE.get(weather.lower(), default_banner)
    if server:
        update_banner(server, imgpath)
    return imgpath


if __name__ == "__main__":
    args = parse_cli()
    print(main(args.server, args.location))
