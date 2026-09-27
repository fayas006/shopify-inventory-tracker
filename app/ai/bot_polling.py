import sys
import io
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

import os
import asyncio

from dotenv import load_dotenv
from config import load_stores
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from app.ai.parser import parse_message
from app.ai.search import (
    search_products,
    count_products,
    get_product_by_id,
)
from app.database.session import SessionLocal

load_dotenv()

BOT_TOKEN = os.getenv("AI_BOT_TOKEN")


def format_product(product):
    title = product.get("title", "Unknown product")
    price = product.get("price", "N/A")
    store = product.get("store", "Unknown store")
    sizes = product.get("available_sizes", [])

    return (
        f"🏷️ {title}\n"
        f"💰 ₹{price}\n"
        f"🏪 {store}\n"
        f"📏 Sizes: {', '.join(sizes) if sizes else 'None'}"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "👋 Inventory Search Bot\n\n"
        "Search products naturally, for example:\n\n"
        "• real madrid\n"
        "• real madrid size M under 400\n"
        "• store1 barcelona XL\n"

        "• store2 madrid under 350\n\n"
        "You can also ask:\n"
        "• total products\n"
        "• available products"
    )


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    session = SessionLocal()

    message = update.message.text.strip()

    if not message:
        return

    # Count queries
    lowered = message.lower()
        # Product image command
    if lowered.startswith("/pic"):
        parts = message.split(maxsplit=1)

        if len(parts) < 2:
            await update.message.reply_text(
                "Usage: /pic <product_id>"
            )
            return

        product_id = parts[1].strip()

        product = get_product_by_id(
            session,
            product_id
        )

        if not product:
            await update.message.reply_text(
                "❌ Product not found."
            )
            return

        images = product.get("images", [])

        if not images:
            await update.message.reply_text(
                "❌ No image available for this product."
            )
            return

        image_url = images[0].get("url")

        if not image_url:
            await update.message.reply_text(
                "❌ Product image URL is missing."
            )
            return

        await update.message.reply_photo(
            photo=image_url,
            caption=format_product(product)
        )

        return

    if "total products" in lowered:
        count = count_products(session)

        await update.message.reply_text(
            f"📦 Total products: {count}"
        )
        return

    if "available products" in lowered:
        count = count_products(
            session,
            available_only=True
        )

        await update.message.reply_text(
            f"✅ Available products: {count}"
        )
        return

    # Parse search
    filters = parse_message(
        message,
        stores=load_stores(),
    )

    results = search_products(
        session,
        keyword=filters["keyword"],
        store=filters["store"],
        size=filters["size"],
        max_price=filters["max_price"],
        min_price=filters["min_price"],
        available_only=True,
        limit=None,
    )

    if not results:

        await update.message.reply_text(
            "❌ No matching products found."
        )

        return

    response_parts = [
        f"📦 Found {len(results)} matching products:\n"
    ]

    for index, product in enumerate(results, start=1):
        response_parts.append(
            f"{index}. {format_product(product)}\n"
        )

    response = "\n\n".join(response_parts)

    # Normal telegram message

    if len(response) <= 4096:

        await update.message.reply_text(
            response
        )

    else:

        file_data = io.BytesIO(response.encode("utf-8"))

        file_data.name = "results.txt"

        await update.message.reply_document(
            document=file_data,
            caption=f"📦 Found {len(results)} matching products"
            f"were found. See attached file for details."
            
        )
            


async def main():

    if not BOT_TOKEN:
        raise RuntimeError(
            "AI_BOT_TOKEN is missing from .env"
        )

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    application.add_handler(
        CommandHandler(
            "start",
            start,
        )
    )

    application.add_handler(
        MessageHandler(
            filters.Regex(r"^/pic(?:\s+.*)?$"),
            handle_message,
        )
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message,
        )
    )

    print("AI inventory bot is running...")

    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
