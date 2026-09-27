import os

import requests
from dotenv import load_dotenv


load_dotenv()


def send_tracker_report(results):
    token = os.getenv("TRACKER_BOT_TOKEN")
    chat_id = os.getenv("TRACKER_CHAT_ID")

    if not token:
        raise RuntimeError(
            "TRACKER_BOT_TOKEN is missing from .env"
        )

    if not chat_id:
        raise RuntimeError(
            "TRACKER_CHAT_ID is missing from .env"
        )

    messages = []

    for result in results:
        store = result["store"]
        summary = result["summary"]

        lines = [
            f"📦 <b>{store}</b>",
            "",
        ]

        new_products = summary["new_products"]
        price_changes = summary["price_changes"]
        restocked = summary["restocked"]
        sold_out = summary["sold_out"]
        new_sizes = summary["new_sizes"]
        removed_sizes = summary["removed_sizes"]

        lines.append(
            f"🆕 New products: {len(new_products)}"
        )
        lines.append(
            f"💰 Price changes: {len(price_changes)}"
        )
        lines.append(
            f"🔄 Restocked: {len(restocked)}"
        )
        lines.append(
            f"❌ Sold out: {len(sold_out)}"
        )
        lines.append(
            f"📏 New sizes: {len(new_sizes)}"
        )
        lines.append(
            f"📉 Removed sizes: {len(removed_sizes)}"
        )

        if new_products:
            lines.append("")
            lines.append("<b>New products</b>")

            for product in new_products:
                lines.append(f"• {product}")

        if price_changes:
            lines.append("")
            lines.append("<b>Price changes</b>")

            for change in price_changes:
                lines.append(f"• {change}")

        if restocked:
            lines.append("")
            lines.append("<b>Restocked</b>")

            for product in restocked:
                lines.append(f"• {product}")

        if sold_out:
            lines.append("")
            lines.append("<b>Sold out</b>")

            for product in sold_out:
                lines.append(f"• {product}")

        messages.append("\n".join(lines))

    message = "\n\n".join(messages)

    url = (
        f"https://api.telegram.org/bot{token}/sendMessage"
    )

    response = requests.post(
        url,
        json={
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
        },
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    if not data.get("ok"):
        raise RuntimeError(
            f"Telegram API error: {data}"
        )

    return data
