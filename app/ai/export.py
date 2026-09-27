import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

import json
from datetime import datetime

from app.database.models import Product, Store
from app.database.session import SessionLocal


OUTPUT_FILE = "ai_data.json"
CHANGES_FILE = "ai_latest_changes.json"


def export_products():
    session = SessionLocal()

    try:
        products = (
            session.query(Product)
            .join(Store)
            .all()
        )

        data = {
            "generated_at": datetime.now().isoformat(),
            "product_count": len(products),
            "products": [],
        }

        for product in products:

            images = []

            for image in product.images:
                if image.image_url:
                    images.append(
                        {
                            "url": image.image_url,
                            "position": image.position,
                        }
                    )

            variants = []

            for variant in product.variants:
                variants.append(
                    {
                        "shopify_id": variant.shopify_id,
                        "title": variant.title,
                        "size": variant.size,
                        "price": variant.price,
                        "available": variant.available,
                    }
                )

            data["products"].append(
                {
                    "id": product.id,
                    "shopify_id": product.shopify_id,
                    "store": product.store.name,
                    "store_code": product.store.code,
                    "title": product.title,
                    "handle": product.handle,
                    "product_url": product.product_url,
                    "description": product.description,
                    "price": product.price,
                    "available_sizes": (
                        [
                            size.strip()
                            for size in product.available_sizes.split(",")
                            if size.strip()
                        ]
                        if product.available_sizes
                        else []
                    ),
                    "available": product.available,
                    "images": images,
                    "variants": variants,
                    "created_at": (
                        product.created_at.isoformat()
                        if product.created_at
                        else None
                    ),
                    "updated_at": (
                        product.updated_at.isoformat()
                        if product.updated_at
                        else None
                    ),
                }
            )

        with open(
            OUTPUT_FILE,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2,
            )

        print(
            f"Exported {len(products)} products "
            f"to {OUTPUT_FILE}"
        )

    finally:
        session.close()


def export_changes(store, summary):
    """
    Save the latest sync changes for the AI bot.
    """

    if Path(CHANGES_FILE).exists():
        try:
            with open(
                CHANGES_FILE,
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)
        except (json.JSONDecodeError, OSError):
            data = {}
    else:
        data = {}

    if "stores" not in data:
        data["stores"] = {}

    data["generated_at"] = datetime.now().isoformat()

    data["stores"][store["code"]] = {
        "store": store["name"],
        "updated_at": datetime.now().isoformat(),
        "summary": summary,
    }

    with open(
        CHANGES_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print(
        f"Saved latest changes for "
        f"{store['name']}"
    )


if __name__ == "__main__":
    export_products()