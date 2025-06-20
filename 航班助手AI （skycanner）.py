# -*- coding: utf-8 -*-
"""Test.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Sgreo2usaN__Rv5N3A8qZOroMUBtH8Y4
"""

import json
import time
import requests
import gradio as gr
from openai import OpenAI

# 配置
OPENAI_API_KEY = ""
SKYSCANNER_API_KEY = ""
MODEL = "gpt-4o-mini"

# 城市到IATA代码映射
iata_lookup = {
    "london": "LON",
    "shanghai": "SHA",
    "berlin": "BER",
    "paris": "CDG",
    "tokyo": "TYO",
    "guangzhou": "CAN",
    "peking": "PEK"
}

city_images = {
    "london": "https://upload.wikimedia.org/wikipedia/commons/c/cd/London_Montage_L.jpg",
    "shanghai": "https://upload.wikimedia.org/wikipedia/commons/4/4c/Shanghai_Bund_Panorama.jpg",
    "tokyo": "https://upload.wikimedia.org/wikipedia/commons/6/6f/Tokyo_Skyline.jpg",
    "berlin": "https://upload.wikimedia.org/wikipedia/commons/f/fb/Berlin_Skyline_Fernsehturm.jpg"
}

client = OpenAI(api_key=OPENAI_API_KEY)

system_message = (
    "您是一家名为 FlightAI 的航空公司的助理。"
    "回答简短、礼貌，回答不超过 1 句话。"
    "回答一定要准确。如果不知道答案，请直说。"
    "如果用户问票价，请调用工具函数获取‘从哪儿出发到哪儿’、哪天、什么舱位的价格。"
)

#Skyscanner 查询函数
def get_ticket_price(from_iata, to_iata, date, seat_class, api_key=SKYSCANNER_API_KEY):
    create_url = "https://partners.api.skyscanner.net/apiservices/v3.0/flights/live/search/create"
    poll_url_base = "https://partners.api.skyscanner.net/apiservices/v3.0/flights/live/search/poll/"
    headers = {
        "Content-Type": "application/json",
        "apikey": api_key
    }
    payload = {
        "query": {
            "market": "US",
            "locale": "en-US",
            "currency": "USD",
            "cabinClass": seat_class.upper(),
            "queryLegs": [
                {
                    "originPlace": {"queryPlace": {"iata": from_iata}},
                    "destinationPlace": {"queryPlace": {"iata": to_iata}},
                    "date": {
                        "year": int(date[:4]),
                        "month": int(date[5:7]),
                        "day": int(date[8:10])
                    }
                }
            ],
            "adults": 1
        }
    }
    try:
        res = requests.post(create_url, headers=headers, json=payload)
        res.raise_for_status()
        session_token = res.json()["sessionToken"]
    except Exception as e:
        print("Create session failed:", e)
        return "Unknown"

    poll_url = poll_url_base + session_token
    for attempt in range(6):
        try:
            poll_res = requests.get(poll_url, headers=headers)
            poll_res.raise_for_status()
            data = poll_res.json()
            if data.get("status") == "RESULT_STATUS_COMPLETE":
                itineraries = data.get("content", {}).get("results", {}).get("itineraries", {})
                prices = []
                for itinerary in itineraries.values():
                    pricing_options = itinerary.get("pricingOptions", [])
                    for option in pricing_options:
                        price = option.get("price", {}).get("amount")
                        if price:
                            prices.append(price)
                if prices:
                    return f"${min(prices)}"
                else:
                    return "Unknown"
            else:
                time.sleep(2)
        except Exception as e:
            print("Polling error:", e)
            time.sleep(1)
    return "Unknown"


price_function = {
    "name": "get_ticket_price",
    "description": "获取航班票价，包括出发地、目的地、时间和舱位。",
    "parameters": {
        "type": "object",
        "properties": {
            "from_city": {"type": "string"},
            "to_city": {"type": "string"},
            "departure_date": {"type": "string"},
            "seat_class": {
                "type": "string",
                "enum": ["economy", "business"]
            }
        },
        "required": ["from_city", "to_city", "departure_date", "seat_class"]
    }
}


def handle_tool_call(message):
    tool_call = message.tool_calls[0]
    args = json.loads(tool_call.function.arguments)
    from_city = args["from_city"]
    to_city = args["to_city"]
    date = args["departure_date"]
    seat_class = args["seat_class"]

    iata_from = iata_lookup.get(from_city.lower(), from_city.upper())
    iata_to = iata_lookup.get(to_city.lower(), to_city.upper())

    price = get_ticket_price(iata_from, iata_to, date, seat_class)
    image_url = city_images.get(to_city.lower(), "")

    return {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": json.dumps({
            "from_city": from_city,
            "to_city": to_city,
            "departure_date": date,
            "seat_class": seat_class,
            "price": price,
            "image": image_url
        })
    }, (from_city, to_city)


def chat(message, history):
    formatted_history = []
    for user_msg, assistant_msg in history:
        formatted_history.append({"role": "user", "content": user_msg})
        formatted_history.append({"role": "assistant", "content": assistant_msg})

    messages = [{"role": "system", "content": system_message}] + formatted_history + [{"role": "user", "content": message}]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=[{"type": "function", "function": price_function}],
        tool_choice="auto"
    )

    msg = response.choices[0].message

    if response.choices[0].finish_reason == "tool_calls":
        tool_response, _ = handle_tool_call(msg)
        messages.append(msg)
        messages.append(tool_response)

        second_response = client.chat.completions.create(model=MODEL, messages=messages)
        final_msg = second_response.choices[0].message

        data = json.loads(tool_response["content"])
        reply = f'{data["from_city"]} 到 {data["to_city"]}（{data["departure_date"]}, {data["seat_class"]} 舱）票价是 {data["price"]}。'
        if data.get("image"):
            reply += f"\n\n![目的地图片]({data['image']})"
        return reply

    return msg.content


gr.ChatInterface(
    fn=chat,
    title="FlightAI 实时机票助手（Skyscanner）",
    chatbot=gr.Chatbot()
).launch()