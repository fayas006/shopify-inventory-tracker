def compare_product(old_product, new_data):
    """
    Compare an existing database product with newly fetched Shopify data.
    Returns a dictionary containing detected changes.
    """

    changes = {
        "price_change": None,
        "title_change": None,
        "description_change": None,
        "restocked": False,
        "sold_out": False,
        "new_sizes": [],
        "removed_sizes": [],
    }

    # -------------------------
    # Price
    # -------------------------

    old_price = old_product.price
    new_price = new_data["price"]

    if old_price != new_price:
        changes["price_change"] = {
            "old": old_price,
            "new": new_price,
        }

    # -------------------------
    # Title
    # -------------------------

    if old_product.title != new_data["title"]:
        changes["title_change"] = {
            "old": old_product.title,
            "new": new_data["title"],
        }

    # -------------------------
    # Description
    # -------------------------

    if old_product.description != new_data["description"]:
        changes["description_change"] = True

    # -------------------------
    # Availability
    # -------------------------

    old_available = old_product.available
    new_available = new_data["available"]

    if not old_available and new_available:
        changes["restocked"] = True

    if old_available and not new_available:
        changes["sold_out"] = True

    # -------------------------
    # Sizes
    # -------------------------

    old_sizes = set()

    if old_product.available_sizes:
        old_sizes = {
            size.strip()
            for size in old_product.available_sizes.split(",")
            if size.strip()
        }

    new_sizes = set()

    if new_data["available_sizes"]:
        new_sizes = {
            size.strip()
            for size in new_data["available_sizes"].split(",")
            if size.strip()
        }

    changes["new_sizes"] = sorted(new_sizes - old_sizes)
    changes["removed_sizes"] = sorted(old_sizes - new_sizes)

    return changes


def has_changes(changes):
    """
    Return True if anything meaningful changed.
    """

    return any(
        [
            changes["price_change"] is not None,
            changes["title_change"] is not None,
            changes["description_change"],
            changes["restocked"],
            changes["sold_out"],
            bool(changes["new_sizes"]),
            bool(changes["removed_sizes"]),
        ]
    )
