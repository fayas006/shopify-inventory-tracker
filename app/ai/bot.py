import io
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from telegram import Bot, Update

from app.ai.parser import parse_message
from app.ai.search import (
    search_products,
    count_products,
    get_product_by_id,
)


load_dotenv()

BOT_TOKEN = os.getenv("AI_BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError(
        "AI_BOT_TOKEN is missing from .env"
    )

bot = Bot(token=BOT_TOKEN)


def format_product(product):
    product_id = product.get("id", "N/A")
    title = product.get("title", "Unknown product")
    price = product.get("price", "N/A")
    store = product.get("store", "Unknown store")
    sizes = product.get("available_sizes", [])

    return (
        f"🆔 ID: {product_id}\n"
        f"🏷️ {title}\n"
        f"💰 ₹{price}\n"
        f"🏪 {store}\n"
        f"📏 Sizes: "
        f"{', '.join(sizes) if sizes else 'None'}"
    )

    message = update.message.text

    if not message:
        return

    message = message.strip()
    lowered = message.lower()

    # Start
    if lowered == "/start":
        await update.message.reply_text(
            "👋 Inventory Search Bot\n\n"
            "Search products naturally:\n\n"
            "• real madrid\n"
            "• real madrid size M under 400\n"
            "• store1 barcelona XL\n"
            "• store2 madrid under 350\n\n"
            "You can also ask:\n"
            "• total products\n"
            "• available products"
        )
        return

        # Product images
    if lowered.startswith("/pic"):

        parts = message.split()

        if len(parts) != 2:
            await update.message.reply_text(
                "Usage: /pic <product_id>\n\n"
                "Example: /pic 123"
            )
            return

        product_id = parts[1]

        if not product_id.isdigit():
            await update.message.reply_text(
                "❌ Product ID must be a number."
            )
            return

        product = get_product_by_id(
            product_id
        )

        if not product:
            await update.message.reply_text(
                f"❌ Product ID {product_id} "
                f"not found."
            )
            return

        images = product.get(
            "images",
            [],
        )

        if not images:
            await update.message.reply_text(
                "❌ This product has no images."
            )
            return

        title = product.get(
            "title",
            "Product",
        )

        await update.message.reply_text(
            f"📸 {title}\n"
            f"🆔 ID: {product_id}\n"
            f"Images: {len(images)}"
        )

        for image in images:

            image_url = image.get("url")

            if not image_url:
                continue

            try:
                await update.message.reply_photo(
                    photo=image_url
                )

            except Exception as error:
                print(
                    f"Failed to send image: {error}"
                )

        return

    # Total products
    if "total products" in lowered:
        count = count_products()

        await update.message.reply_text(
            f"📦 Total products: {count}"
        )

        return

    # Available products
    if "available products" in lowered:
        count = count_products(
            available_only=True
        )

        await update.message.reply_text(
            f"✅ Available products: {count}"
        )

        return

    # Search
    filters = parse_message(message)

    results = search_products(
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
        f"🔎 Found {len(results)} result(s):\n"
    ]

    for index, product in enumerate(
        results,
        start=1,
    ):
        response_parts.append(
            f"{index}. "
            f"{format_product(product)}\n"
        )

    response = "\n\n".join(
        response_parts
    )

    # Normal message
    if len(response) <= 4000:
        await update.message.reply_text(
            response
        )
        return

    # Long response → TXT file
    file_data = io.BytesIO(
        response.encode("utf-8")
    )

    file_data.name = "inventory_results.txt"

    await update.message.reply_document(
        document=file_data,
        caption=(
            f"📄 {len(results)} matching "
            f"products found. "
            f"Full results attached."
        ),
    )


@asynccontextmanager
async def lifespan(app):
    await bot.initialize()

    yield

    await bot.shutdown()


app = FastAPI(
    lifespan=lifespan
)


@app.get("/")
async def health_check():
    return {
        "status": "online",
        "service": "shopify inventory bot",
    }


@app.post("/telegram-webhook")
async def telegram_webhook(
    request: Request,
):
    data = await request.json()

    update = Update.de_json(
        data,
        bot,
    )

    await handle_message(update)

    return {
        "ok": True
    }