import re

from linebot.models import (
    CarouselColumn,
    CarouselTemplate,
    MessageAction,
    TemplateSendMessage,
    URIAction,
)


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
