import os
from io import BytesIO
from datetime import datetime

from dotenv import load_dotenv
from telegram import Bot
from telegram.constants import ParseMode


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

MAX_LENGTH = 4000


def money(value):
    if value is None:
        return "N/A"

    return f"₹{float(value):,.0f}"


def build_message(store, summary):
    """
    Build the Telegram notification from the sync summary.
    """

    lines = []

    lines.append(
        f"📦 <b>Shopify Inventory Report</b>"
    )

    lines.append(
        f"<b>Store:</b> {store['name']}"
    )

    lines.append(
        f"<b>Date:</b> "
        f"{datetime.now().strftime('%d %b %Y, %I:%M %p')}"
    )

    # --------------------------------
    # New Products
    # --------------------------------

    new_products = summary["new_products"]

    if new_products:

        lines.append("")
        lines.append(
            f"🆕 <b>NEW PRODUCTS ({len(new_products)})</b>"
        )

        for item in new_products:

            lines.append(
                f"• {item['title']} "
                f"— {money(item['price'])}"
            )

    # --------------------------------
    # Price Changes
    # --------------------------------

    price_changes = summary["price_changes"]

    if price_changes:

        lines.append("")
        lines.append(
            f"💰 <b>PRICE CHANGES ({len(price_changes)})</b>"
        )

        for item in price_changes:

            lines.append(
                f"• {item['title']}\n"
                f"  {money(item['old'])} → "
                f"{money(item['new'])}"
            )

    # --------------------------------
    # Restocked
    # --------------------------------

    restocked = summary["restocked"]

    if restocked:

        lines.append("")
        lines.append(
            f"🔄 <b>RESTOCKED ({len(restocked)})</b>"
        )

        for title in restocked:
            lines.append(f"• {title}")

    # --------------------------------
    # Sold Out
    # --------------------------------

    sold_out = summary["sold_out"]

    if sold_out:

        lines.append("")
        lines.append(
            f"📉 <b>SOLD OUT ({len(sold_out)})</b>"
        )

        for title in sold_out:
            lines.append(f"• {title}")

    # --------------------------------
    # New Sizes
    # --------------------------------

    new_sizes = summary["new_sizes"]

    if new_sizes:

        lines.append("")
        lines.append(
            f"📏 <b>NEW SIZES ({len(new_sizes)})</b>"
        )

        for item in new_sizes:

            sizes = ", ".join(item["sizes"])

            lines.append(
                f"• {item['title']}: {sizes}"
            )

    # --------------------------------
    # Removed Sizes
    # --------------------------------

    removed_sizes = summary["removed_sizes"]

    if removed_sizes:

        lines.append("")
        lines.append(
            f"❌ <b>REMOVED SIZES ({len(removed_sizes)})</b>"
        )

        for item in removed_sizes:

            sizes = ", ".join(item["sizes"])

            lines.append(
                f"• {item['title']}: {sizes}"
            )

    # --------------------------------
    # Title Changes
    # --------------------------------

    title_changes = summary["title_changes"]

    if title_changes:

        lines.append("")
        lines.append(
            f"✏️ <b>TITLE CHANGES ({len(title_changes)})</b>"
        )

        for item in title_changes:

            lines.append(
                f"• {item['old']}\n"
                f"  → {item['new']}"
            )

    # --------------------------------
    # Description Changes
    # --------------------------------

    description_changes = summary["description_changes"]

    if description_changes:

        lines.append("")
        lines.append(
            f"📝 <b>DESCRIPTION CHANGES "
            f"({len(description_changes)})</b>"
        )

        for title in description_changes:
            lines.append(f"• {title}")

    if len(lines) == 3:

        lines.append("")
        lines.append(
            "✅ <b>No inventory changes detected.</b>"
        )

    return "\n".join(lines)


async def send_summary(store, summary):
    """
    Send the summary to Telegram.

    Long reports are automatically sent as a .txt file.
    """

    message = build_message(store, summary)

    bot = Bot(token=BOT_TOKEN)

    if len(message) <= MAX_LENGTH:

        await bot.send_message(
            chat_id=CHAT_ID,
            text=message,
            parse_mode=ParseMode.HTML,
        )

    else:

        file = BytesIO(
            message.encode("utf-8")
        )

        file.name = (
            f"shopify_report_"
            f"{datetime.now().strftime('%Y-%m-%d')}.txt"
        )

        await bot.send_document(
            chat_id=CHAT_ID,
            document=file,
            caption="📦 Shopify Tracker — Full Report",
        )
