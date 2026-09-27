import re

from sqlalchemy import or_

from app.database.models import Product, Store, Variant


def normalize(text):
    if not text:
        return ""

    return re.sub(
        r"[^a-z0-9]+",
        " ",
        str(text).lower(),
    ).strip()


def search_products(
    session,
    keyword=None,
    store=None,
    size=None,
    max_price=None,
    min_price=None,
    available_only=False,
    limit=None,
):
    """
    Search products directly from the local SQLite database.
    """

    query = (
        session.query(Product)
        .join(Store)
    )

    keyword = normalize(keyword)
    store = normalize(store)
    size = normalize(size)

    # Store filter
    if store:
        query = query.filter(
            Store.name.ilike(f"%{store}%")
        )

    # Keyword filter
    if keyword:
        query = query.filter(
            or_(
                Product.title.ilike(f"%{keyword}%"),
                Product.description.ilike(f"%{keyword}%"),
                Product.handle.ilike(f"%{keyword}%"),
            )
        )

    # Price filters
    if max_price is not None:
        query = query.filter(
            Product.price <= max_price
        )

    if min_price is not None:
        query = query.filter(
            Product.price >= min_price
        )

    # Availability
    if available_only:
        query = query.filter(
            Product.available.is_(True)
        )

    # Size
    if size:
        variants = (
            session.query(Variant.product_id)
            .filter(
                Variant.title.ilike(f"%{size}%"),
                Variant.available.is_(True),
            )
            .subquery()
        )

        query = query.filter(
            Product.id.in_(variants)
        )

    if limit is not None:
        query = query.limit(limit)

    products = query.all()

    return [
        {
            "id": product.id,
            "shopify_id": product.shopify_id,
            "store": product.store.name,
            "title": product.title,
            "handle": product.handle,
            "description": product.description,
            "price": product.price,
            "available_sizes": product.available_sizes,
            "available": product.available,
            "image_url": product.image_url,
            "images": [
                {
                    "url": image.image_url,
                }
                for image in product.images
            ],
            "product_url": product.product_url,
        }
        for product in products
    ]


def count_products(
    session,
    store=None,
    available_only=False,
):
    """
    Count products directly from SQLite.
    """

    query = (
        session.query(Product)
        .join(Store)
    )

    store = normalize(store)

    if store:
        query = query.filter(
            Store.name.ilike(f"%{store}%")
        )

    if available_only:
        query = query.filter(
            Product.available.is_(True)
        )

    return query.count()


def get_product_by_id(session, product_id):
    """
    Find a product by its local database ID or Shopify ID.
    """

    product = (
        session.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if product:
        return {
            "id": product.id,
            "shopify_id": product.shopify_id,
            "store": product.store.name,
            "title": product.title,
            "handle": product.handle,
            "description": product.description,
            "price": product.price,
            "available_sizes": product.available_sizes,
            "available": product.available,
            "image_url": product.image_url,
            "images": [
                {
                    "url": image.image_url,
                }
                for image in product.images
            ],
            "product_url": product.product_url,
        }

    product = (
        session.query(Product)
        .filter(Product.shopify_id == product_id)
        .first()
    )

    if product:
        return {
            "id": product.id,
            "shopify_id": product.shopify_id,
            "store": product.store.name,
            "title": product.title,
            "handle": product.handle,
            "description": product.description,
            "price": product.price,
            "available_sizes": product.available_sizes,
            "available": product.available,
            "image_url": product.image_url,
            "images": [
                {
                    "url": image.image_url,
                }
                for image in product.images
            ],
            "product_url": product.product_url,
        }

    return None
