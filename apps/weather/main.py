"""
weather.py

Authorize as:

    https://discordapp.com/oauth2/authorize?client_id=698589904808050708&permission=32&scope=bot

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
import os
from pathlib import Path
import argparse
from pprint import pprint

import requests
import discord
import asyncio


HERE = Path(__file__).resolve().parent
METAWEATHER = "https://www.metaweather.com/api/"
CLIENT_ID = r"698589904808050708"
BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]

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


class DiscordClient(discord.Client):
    def __init__(self, new_banner, guild_id, dry_run=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.banner = new_banner
        self.dry_run = dry_run
        self.guild_id = guild_id

    async def on_ready(self):
        try:
            print("Logged on as", self.user)
            guild = self.get_guild(self.guild_id)
            if guild is None:
                raise ValueError(f"We don't have access to guild {self.guild_id}")
            if "BANNER" not in guild.features:
                print("If only we had permissions...")
                return
            print("Uploading", self.banner, "to guild", guild.name)
            if self.dry_run:
                print("   [dry-run]")
                return
            with open(self.banner, "rb") as f:
                await guild.edit(banner=f.read())
        finally:
            await self.logout()


def find_location(query):
    r = requests.get(f"{METAWEATHER}/location/search/?query={query}")
    r.raise_for_status()
    data = r.json()
    return data[0]["woeid"]


def current_weather(location):
    # this is a query, find the WhereOnEarth ID
    if isinstance(location, str) and not location.isnumeric():
        location = find_location(location)
    r = requests.get(f"{METAWEATHER}/location/{location}/")
    r.raise_for_status()
    data = r.json()
    print("MetaWeather replied with:")
    pprint(data)
    return data["consolidated_weather"][0]["weather_state_abbr"]


def update_banner(server, image_path, dry_run=False):
    if not BOT_TOKEN:
        raise ValueError("Please provide your DISCORD_BOT_TOKEN env var!")

    client = DiscordClient(new_banner=image_path, guild_id=server, dry_run=dry_run)
    client.run(BOT_TOKEN)


def parse_cli():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--location",
        required=True,
        type=str,
        help="Place to obtain weather information for. It can be a text query or a WhereOnEarth ID.",
    )
    p.add_argument(
        "--server",
        required=True,
        type=int,
        help="Discord server ID (Server Settings> Widget) where you want to update the banner.",
    )
    p.add_argument("--dry-run", action="store_true", help="If set, do not upload the banner.")
    return p.parse_args()


def main(server, location, default_banner=None, dry_run=False):
    weather = current_weather(location)
    imgpath = HERE / "data" / WEATHER_TO_IMAGE.get(weather.lower(), default_banner)
    update_banner(server, imgpath, dry_run=dry_run)
    return imgpath


if __name__ == "__main__":
    args = parse_cli()
    print(main(args.server, args.location))
