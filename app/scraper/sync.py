from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Store, Product, Variant, ProductImage
from app.database.session import SessionLocal
from app.scraper.compare import compare_product
from app.scraper.fetch import fetch_products

def clean_image_url(url):
    if not url:
        return None

    url = url.strip()

    # Convert Markdown:
    # [https://example.com/image.jpg](https://example.com/image.jpg)
    # into:
    # https://example.com/image.jpg
    if url.startswith("[") and "](" in url and url.endswith(")"):
        url = url[1:url.index("](")]

    return url


def get_store(session, store_data):
    """Get an existing store or create it."""

    store = session.scalar(
        select(Store).where(
            Store.code == store_data["code"]
        )
    )

    if store:
        return store

    store = Store(
        name=store_data["name"],
        code=store_data["code"],
        url=store_data["url"],
    )

    session.add(store)
    session.flush()

    return store


def parse_product(shopify_product, store):
    """Convert Shopify data into our database format."""

    variants = shopify_product.get("variants", [])

    available_sizes = []

    for variant in variants:
        if variant.get("available"):
            size = variant.get("title")

            if size and size not in available_sizes:
                available_sizes.append(size)

    prices = []

    for variant in variants:
        try:
            prices.append(float(variant.get("price")))
        except (TypeError, ValueError):
            pass

    highest_price = max(prices) if prices else None

    product_available = any(
        variant.get("available", False)
        for variant in variants
    )

    created_at = None

    if shopify_product.get("created_at"):
        try:
            created_at = datetime.fromisoformat(
                shopify_product["created_at"].replace(
                    "Z",
                    "+00:00",
                )
            )
        except ValueError:
            pass

    # Get all Shopify product images
    images = []

    for position, image in enumerate(
        shopify_product.get("images", []),
        start=1,
    ):
        image_url = clean_image_url(
            image.get("src")
        )

        if image_url:
            images.append(
                {
                    "shopify_id": (
                        str(image["id"])
                        if image.get("id")
                        else None
                    ),
                    "image_url": image_url,
                    "position": position,
                }
            )

    # Keep the first image in the existing Product.image_url field
    image_url = (
        images[0]["image_url"]
        if images
        else None
    )

    return {
        "shopify_id": str(shopify_product["id"]),
        "title": shopify_product.get("title", ""),
        "handle": shopify_product.get("handle"),
        "product_url": (
            f"{store.url.rstrip('/')}/products/"
            f"{shopify_product.get('handle')}"
            if shopify_product.get("handle")
            else None
        ),
        "description": shopify_product.get("body_html"),
        "price": highest_price,
        "available_sizes": ",".join(available_sizes),
        "available": product_available,
        "image_url": image_url,
        "images": images,
        "created_at": created_at,
        "variants": variants,
    }


def sync_images(session, product, image_data):
    """
    Synchronize all Shopify images for a product.
    """

    existing_images = {
        image.shopify_id: image
        for image in product.images
        if image.shopify_id
    }

    current_image_ids = set()

    for image_info in image_data:

        shopify_id = image_info["shopify_id"]
        image_url = image_info["image_url"]
        position = image_info["position"]

        if shopify_id:
            current_image_ids.add(shopify_id)

        if shopify_id in existing_images:

            image = existing_images[shopify_id]

            image.image_url = image_url
            image.position = position

        else:

            image = ProductImage(
                product_id=product.id,
                shopify_id=shopify_id,
                image_url=image_url,
                position=position,
            )

            session.add(image)

    # Remove images that no longer exist on Shopify
    for shopify_id, image in existing_images.items():

        if shopify_id not in current_image_ids:
            session.delete(image)


def sync_product(session, shopify_product, store):
    """
    Insert or update a product.

    Returns:
        ("new", None)
        ("updated", changes)
        ("unchanged", None)
    """

    shopify_id = str(shopify_product["id"])

    product = session.scalar(
        select(Product).where(
            Product.store_id == store.id,
            Product.shopify_id == shopify_id,
        )
    )

    data = parse_product(
        shopify_product,
        store,
    )

    # --------------------------------
    # NEW PRODUCT
    # --------------------------------

    if product is None:

        product = Product(
            store_id=store.id,
            shopify_id=data["shopify_id"],
            title=data["title"],
            handle=data["handle"],
            product_url=data["product_url"],
            description=data["description"],
            price=data["price"],
            available_sizes=data["available_sizes"],
            available=data["available"],
            image_url=data["image_url"],
            created_at=data["created_at"],
        )

        session.add(product)
        session.flush()

        # Add all images
        sync_images(
            session,
            product,
            data["images"],
        )

        # Add variants
        for variant_data in data["variants"]:

            variant = Variant(
                product_id=product.id,
                shopify_id=str(
                    variant_data["id"]
                ),
                title=variant_data.get("title"),
                size=variant_data.get("title"),
                price=(
                    float(variant_data["price"])
                    if variant_data.get("price")
                    else None
                ),
                available=variant_data.get(
                    "available",
                    False,
                ),
            )

            session.add(variant)

        return "new", None

    # --------------------------------
    # COMPARE BEFORE UPDATING
    # --------------------------------

    changes = compare_product(
        product,
        data,
    )

    # --------------------------------
    # UPDATE PRODUCT
    # --------------------------------

    product.title = data["title"]
    product.handle = data["handle"]
    product.product_url = data["product_url"]
    product.description = data["description"]
    product.price = data["price"]
    product.available_sizes = data["available_sizes"]
    product.available = data["available"]
    product.image_url = data["image_url"]

    # --------------------------------
    # UPDATE IMAGES
    # --------------------------------

    sync_images(
        session,
        product,
        data["images"],
    )

    # --------------------------------
    # UPDATE VARIANTS
    # --------------------------------

    existing_variants = {
        variant.shopify_id: variant
        for variant in product.variants
    }

    current_variant_ids = set()

    for variant_data in data["variants"]:

        variant_id = str(
            variant_data["id"]
        )

        current_variant_ids.add(
            variant_id
        )

        if variant_id in existing_variants:

            variant = existing_variants[
                variant_id
            ]

            variant.title = variant_data.get(
                "title"
            )

            variant.size = variant_data.get(
                "title"
            )

            variant.price = (
                float(variant_data["price"])
                if variant_data.get("price")
                else None
            )

            variant.available = variant_data.get(
                "available",
                False,
            )

        else:

            variant = Variant(
                product_id=product.id,
                shopify_id=variant_id,
                title=variant_data.get("title"),
                size=variant_data.get("title"),
                price=(
                    float(variant_data["price"])
                    if variant_data.get("price")
                    else None
                ),
                available=variant_data.get(
                    "available",
                    False,
                ),
            )

            session.add(variant)

    # --------------------------------
    # REMOVE DELETED VARIANTS
    # --------------------------------

    for variant_id, variant in existing_variants.items():

        if variant_id not in current_variant_ids:
            session.delete(variant)

    # --------------------------------
    # RETURN CHANGES
    # --------------------------------

    if any(
        [
            changes["price_change"] is not None,
            changes["title_change"] is not None,
            changes["description_change"],
            changes["restocked"],
            changes["sold_out"],
            bool(changes["new_sizes"]),
            bool(changes["removed_sizes"]),
        ]
    ):
        return "updated", changes

    return "unchanged", None


def sync_store(session, store_data, products):
    """
    Sync all Shopify products for one store
    and return a change summary.
    """

    store = get_store(
        session,
        store_data,
    )

    summary = {
        "new_products": [],
        "price_changes": [],
        "restocked": [],
        "sold_out": [],
        "new_sizes": [],
        "removed_sizes": [],
        "title_changes": [],
        "description_changes": [],
    }

    for shopify_product in products:

        result, changes = sync_product(
            session,
            shopify_product,
            store,
        )

        title = shopify_product.get(
            "title",
            "Unknown product",
        )

        # -------------------------
        # New product
        # -------------------------

        if result == "new":

            prices = []

            for variant in shopify_product.get(
                "variants",
                [],
            ):
                try:
                    prices.append(
                        float(
                            variant.get("price")
                        )
                    )
                except (
                    TypeError,
                    ValueError,
                ):
                    pass

            highest_price = (
                max(prices)
                if prices
                else None
            )

            summary["new_products"].append(
                {
                    "title": title,
                    "price": highest_price,
                }
            )

            continue

        # -------------------------
        # No changes
        # -------------------------

        if result == "unchanged":
            continue

        # -------------------------
        # Price
        # -------------------------

        if changes["price_change"]:

            summary["price_changes"].append(
                {
                    "title": title,
                    "old": changes[
                        "price_change"
                    ]["old"],
                    "new": changes[
                        "price_change"
                    ]["new"],
                }
            )

        # -------------------------
        # Restocked
        # -------------------------

        if changes["restocked"]:
            summary["restocked"].append(
                title
            )

        # -------------------------
        # Sold out
        # -------------------------

        if changes["sold_out"]:
            summary["sold_out"].append(
                title
            )

        # -------------------------
        # New sizes
        # -------------------------

        if changes["new_sizes"]:

            summary["new_sizes"].append(
                {
                    "title": title,
                    "sizes": changes[
                        "new_sizes"
                    ],
                }
            )

        # -------------------------
        # Removed sizes
        # -------------------------

        if changes["removed_sizes"]:

            summary["removed_sizes"].append(
                {
                    "title": title,
                    "sizes": changes[
                        "removed_sizes"
                    ],
                }
            )

        # -------------------------
        # Title
        # -------------------------

        if changes["title_change"]:

            summary["title_changes"].append(
                {
                    "old": changes[
                        "title_change"
                    ]["old"],
                    "new": changes[
                        "title_change"
                    ]["new"],
                }
            )

        # -------------------------
        # Description
        # -------------------------

        if changes["description_change"]:

            summary["description_changes"].append(
                title
            )

    return summary
