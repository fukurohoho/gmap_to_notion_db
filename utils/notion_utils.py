import json
import logging
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "."))

import requests
from dotenv import load_dotenv
from map_utils import map_fields_dict

load_dotenv()
NOTION_API_KEY = os.getenv("NOTION_API_KEY")

notion_fields_dict = {
    "店名": "text",
    "住所": "text",
    "概要": "text",
    "料理ジャンル": "select",
    "定休日": "multi_select",
    "GoogleMapURL": "url",
    "参考URL": "url",
    "訪問有無": "status",
    "訪問(予定)日": "date",
}


def write_data_to_notion(place: dict) -> str:
    """場所情報からNotionDBにデータを追加し、そのURLを返します。

    Args:
        place (dict): 追加したいデータの場所情

    Returns:
        str: 追加したデータのURL
    """
    place["料理ジャンル"] = []
    headers_notion = {
        "Authorization": f"Bearer {os.getenv('NOTION_API_KEY')}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    properties_notion = {
        "店名": {
            "title": [
                {
                    "text": {
                        "content": place["店名"],
                    }
                }
            ]
        }
    }
    for key, value in notion_fields_dict.items():
        if key in map_fields_dict.keys():
            if key == "店名":
                continue
            if place[key] == "" or place[key] == []:
                continue

            if value == "text":
                properties_notion[key] = {
                    "rich_text": [{"text": {"content": place[key]}}]
                }
            elif value == "multi_select":
                properties_notion[key] = {
                    "multi_select": [
                        {
                            "name": elem,
                        }
                        for elem in place[key]
                    ]
                }
            elif value == "status":
                properties_notion[key] = {
                    "status": {
                        "name": place[key],
                    }
                }
            elif value == "date":
                properties_notion[key] = {"date": {"start": place[key], "end": null}}
            elif value == "url":
                properties_notion[key] = {
                    "url": place[key],
                }
            elif value == "select":
                properties_notion[key] = {
                    "select": {
                        "name": place[key],
                    }
                }

    body_notion = {
        "parent": {
            "database_id": os.getenv("DATABASE_ID"),
        },
        "properties": properties_notion,
    }

    import pprint

    pprint.pprint(body_notion)

    req = requests.post(
        "https://api.notion.com/v1/pages",
        headers=headers_notion,
        data=json.dumps(body_notion),
        timeout=15,
    )
    try:
        req.raise_for_status()
        notion_page = req.json()
        return notion_page["url"]
    except requests.exceptions.RequestException as e:
        logging.error(f"Error writing data to Notion: {e}")
        from traceback import format_exc

        print(format_exc())
        return ""


if __name__ == "__main__":
    place = {
        "GoogleMapURL": "https://maps.google.com/?cid=2351152992680583293",
        "image_url": "https://lh3.googleusercontent.com/place-photos/AEkURDxic-5X1F--iRf9WnXpkeq90zQXij5AHOMOZOgkHHluWXK7KdhNjEIMUBQnKL0-9pP8imfbJeYnL9W3SVtxLVFJnazKZVzzR38uS4MX8w8UoRaoCQcqJ4ZshbhTmGbyXF84vkzL_4oEGY42K3s=s1600-w4032",
        "place_id": "ChIJBQ7HhlkIAWARfaBSnTD5oCA",
        "住所": "京都府京都市左京区吉田泉殿町１−1−９１",
        "参考URL": "https://map.mcdonalds.co.jp/map/26537",
        "定休日": [],
        "店名": "マクドナルド 百万遍店",
        "料理ジャンル": [
            "cafe",
            "establishment",
            "food",
            "point_of_interest",
            "restaurant",
            "store",
        ],
        "概要": "ハンバーガー、フライドポテトで知られる老舗ファストフードのチェーン店。",
    }
    print(write_data_to_notion(place))
