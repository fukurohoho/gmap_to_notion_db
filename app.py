import os
import logging
import requests
from flask import Flask, request, jsonify
from reply_generator import generate_reply 

from utils.map_utils import search_and_suggest_places
from utils.line_utils import show_places_carousel

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

logging.basicConfig(level=logging.INFO)

@app.route('/webhook', methods=['POST'])
def webhook():
    name = "DBくん"

    data = request.json
    places = []
    logging.info(f"Received data: {data}")

    if "events" in data and len(data["events"]) > 0:
        event = data["events"][0]
        if event["type"] == "message" and event["message"]["type"] == "text":
            text = event["message"]["text"].replace(name, '').strip()

            if text.startswith(f"{name} place"):
                try:
                    place_index = int(text.replace(f"{name} place", "").strip())
                    place = places[place_index]
                    logging.info(f"Selected place: {place}")

                    # ここにNotion処理が入る

                    reply_message(event.reply_token, f"「{place['店名']}」を登録したよ")
                    return jsonify({"message": f"「{place['店名']}」を登録したよ"}), 200
                except ValueError:
                    logging.error(f"Invalid place index: {text}")
                    places = []
                    reply_message(event.reply_token, "エラー！もう1回検索から行ってな")
                    return jsonify({"message": "エラー！もう1回検索から行ってな"}), 400

            elif text.startswith(name):
                places = search_and_suggest_places(text)
                logging.info(f"Found places: {places}")
                carousel_message = show_places_carousel(places, name)
                logging.info(f"Sending carousel message: {carousel_message}")
                line_bot_api.reply_message(event.reply_token, messages=carousel_message)
                return jsonify({"message": f"「{text}」の検索結果やで"}), 200

    return jsonify({"message": ""}), 200


def reply_message(reply_token, text):
    """LINE にメッセージを返信する"""
    if not LINE_CHANNEL_ACCESS_TOKEN:
        logging.error("LINE_CHANNEL_ACCESS_TOKEN is not set!")
        return

    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    payload = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": text}]
    }
    
    response = requests.post(url, headers=headers, json=payload)
    logging.info(f"LINE API response: {response.status_code} {response.text}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)