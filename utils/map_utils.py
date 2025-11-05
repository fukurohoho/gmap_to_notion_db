import os
import pprint
import re
import time

import googlemaps
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

map_fields_dict = {
    "店名": "name",
    "住所": "formatted_address",
    "概要": "editorial_summary",
    "料理ジャンル": "types",
    "定休日": "holiday_guess",
    "GoogleMapURL": "url",
    "参考URL": "website",
    "place_id": "place_id",
    "image_url": "images",
}


def get_image_url(photo_reference: str, maxwidth: int = 400) -> str:
    endpoint = "https://maps.googleapis.com/maps/api/place/photo"
    params = {
        "maxwidth": maxwidth,
        "photo_reference": photo_reference,
        "key": GOOGLE_API_KEY,
    }
    try:
        req = requests.get(endpoint, params=params, allow_redirects=False, timeout=10)
        return req.headers.get("Location")
    except requests.exceptions.RequestException as e:
        print(f"Error getting image URL: {e}")
        return ""


def format_place_info(place: dict) -> dict:
    info_dict = {}
    for key, item in map_fields_dict.items():
        if place.get(item, "") != "":
            info_dict[key] = place.get(item, "")

    photo_ref = place.get("photos", [])[0].get("photo_reference", "")
    maxwidth = place.get("photos", [])[0].get("width", 400)
    info_dict["image_url"] = get_image_url(photo_ref, maxwidth)

    info_dict["住所"] = re.sub(
        r"日本、〒\d+-\d+", " ", place["formatted_address"]
    ).strip()

    info_dict["概要"] = place.get("editorial_summary", "").get("overview", "")

    # 定休日をとってくる
    buisiness_days = place.get("current_opening_hours", {}).get("weekday_text", [])
    info_dict["定休日"] = [
        item[0]
        for item in re.findall(
            r"([日月火水木金土])曜日: 定休日", " ".join(buisiness_days)
        )
    ]

    return info_dict


def search_and_suggest_places(query: str, max_results: int = 10) -> list[dict]:
    """
    指定されたクエリで店舗を検索し、各店舗の詳細情報を取得する関数
    """
    places_details = []
    places_result = gmaps.places(query=query, language="ja")

    for place in places_result.get("results", [])[:max_results]:
        place_id = place["place_id"]
        details = gmaps.place(place_id=place_id, language="ja").get("result")
        places_details.append(format_place_info(details))

    return places_details


if __name__ == "__main__":
    pprint.pprint(search_and_suggest_places("マクド　百万遍"))
