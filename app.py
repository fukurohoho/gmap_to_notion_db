import logging
import os
import sys
from textwrap import dedent
from linebot.models import TextSendMessage
from linebot.api import LineBotApi

import requests
from flask import Flask, jsonify, request

sys.path.append(os.path.join(os.path.dirname(__file__), "."))
from dotenv import load_dotenv

from utils.line_utils import show_places_carousel, set_quick_reply_message
from utils.map_utils import search_and_suggest_places
from utils.notion_utils import write_data_to_notion

load_dotenv()

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
logging.basicConfig(level=logging.INFO)
places = []
name = "DBくん"


@app.route("/webhook", methods=["POST"])
def webhook():
    global places
    data = request.json
    logging.info(f"Received data: {data}")

    if "events" in data and len(data["events"]) > 0:
        event = data["events"][0]
        if event["type"] == "message" and event["message"]["type"] == "text":
            text = event["message"]["text"]
            logging.info(f"Received text: {text}")
            print(f"{text} を受信したで")

            if text.startswith(f"{name} place"):
                try:
                    place_index = int(text.replace(f"{name} place", "").strip())
                    place = places[place_index]
                    logging.info(f"Selected place: {place}")

                    notion_url = write_data_to_notion(place)
                    line_bot_api.reply_message(
                        event["replyToken"],
                        [
                        TextSendMessage(text=f"「{place['店名']}」を登録したで\n{notion_url}"),
                        set_quick_reply_message(name)
                        ]
                    )

                    return (
                        jsonify(
                            {
                                "message": f"「{place['店名']}」を登録したで\n{notion_url}"
                            }
                        ),
                        200,
                    )
                except ValueError:
                    logging.error(f"Invalid place index: {text}")
                    places = []
                    line_bot_api.reply_message(
                        event["replyToken"], 
                        [
                        TextSendMessage(text="エラー😭もう1回検索から行ってな"),
                        set_quick_reply_message(name)
                        ]
                    )

                    return jsonify({"message": "エラー😭もう1回検索から行ってな"}), 400

            elif text.startswith(name):
                query = text.replace(name, "").strip()
                if query == "使い方を見る":  # 使い方の説明
                    how_to_use = dedent(
                        """
                    まず、「{name} (知りたい場所)」で話しかけるねん。
                    そうしたら、{name}がその場所をGoogleMap上で検索して候補を見せるから、その中から登録したいものを選んでな😉
                    """
                    )
                    line_bot_api.reply_message(
                        event["replyToken"], 
                        [
                        TextSendMessage(text=how_to_use),
                        set_quick_reply_message(name)
                        ]
                    )


                    return jsonify({"message": "使い方を見る"}), 200

                elif query == "DBのURLを表示する":  # DB URLの表示
                    line_bot_api.reply_message(
                        event["replyToken"],
                        [
                        TextSendMessage(text=f"DBのURLはこれやで\n{os.getenv('NOTION_DB_URL')}"),
                        set_quick_reply_message(name)
                        ]
                    )

                    return (
                        jsonify(
                            {
                                "message": f"DBのURLはこれやで\n{os.getenv('NOTION_DB_URL')}"
                            }
                        ),
                        200,
                    )

                else:  # 場所検索
                    places = search_and_suggest_places(query)
                    logging.info(f"Found places: {places}")
                    carousel_message = show_places_carousel(places, name)
                    logging.info(f"Sending carousel message: {carousel_message}")
                    line_bot_api.reply_message(
                        event["replyToken"], 
                        [
                        carousel_message,
                        set_quick_reply_message(name)
                        ]
                    )

                    return jsonify({"message": f"「{text}」の検索結果やで"}), 200

    return jsonify({"message": ""}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
