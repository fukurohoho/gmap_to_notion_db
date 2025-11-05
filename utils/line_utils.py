import re

from linebot.models import (CarouselColumn, CarouselTemplate, MessageAction,
                            TemplateSendMessage, URIAction, QuickReply, QuickReplyButton, TextSendMessage)


def show_places_carousel(places: list[dict], name="DBくん"):
    columns_list = []
    for i, place in enumerate(places):
        columns_list.append(
            CarouselColumn(
                title=place["店名"],
                text=place["住所"],
                thumbnail_image_url=place["image_url"],
                actions=[
                    URIAction(label="GoogleMapで表示", uri=place["GoogleMapURL"]),
                    MessageAction(label="この場所を登録", data=f"{name} place {i}"),
                ],
            )
        )
    carousel_template_message = TemplateSendMessage(
        alt_text="場所を選択してください",
        template=CarouselTemplate(columns=columns_list),
    )
    return carousel_template_message

def set_quick_reply_message(reply_token):
    language_list = ["使い方を見る", "DBのURLを表示する"]
    items = [
        QuickReplyButton(
            action=MessageAction(label=f"使い方を見る", text=f"{name} 使い方を見る")
        ),
        QuickReplyButton(
            action=MessageAction(
                label=f"DBのURLを表示する", text=f"{name} DBのURLを表示する"
            )
        ),
    ]
    messages = TextSendMessage(text="", quick_reply=QuickReply(items=items))
    line_bot_api.reply_message(reply_token, messages)

