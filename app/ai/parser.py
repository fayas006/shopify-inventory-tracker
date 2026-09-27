import re


SIZE_PATTERN = re.compile(
    r"\b(2XL|3XL|4XL|XXXL|XXL|XL|L|M|S)\b",
    re.IGNORECASE,
)

PRICE_PATTERN = re.compile(
    r"(?:under|below|less than|max(?:imum)?|upto|up to)\s*₹?\s*(\d+(?:\.\d+)?)",
    re.IGNORECASE,
)

MIN_PRICE_PATTERN = re.compile(
    r"(?:above|over|more than|minimum|min)\s*₹?\s*(\d+(?:\.\d+)?)",
    re.IGNORECASE,
)


def parse_message(message, stores=None):
    text = message.strip()
    lowered = text.lower()

    result = {
        "keyword": None,
        "store": None,
        "size": None,
        "max_price": None,
        "min_price": None,
    }

    # Detect configured store
    store_aliases = {}

    for store in stores or []:
        name = store["name"]

        store_aliases[name.lower()] = name

        # Also allow the store code as an alias
        if store.get("code"):
            store_aliases[store["code"].lower()] = name

    for alias, store_name in sorted(
        store_aliases.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    ):
        if re.search(
            rf"\b{re.escape(alias)}\b",
            lowered,
        ):
            result["store"] = store_name
            break

    # Detect size
    size_match = SIZE_PATTERN.search(text)

    if size_match:
        result["size"] = size_match.group(1).upper()

    # Detect maximum price
    max_price_match = PRICE_PATTERN.search(text)

    if max_price_match:
        result["max_price"] = float(
            max_price_match.group(1)
        )

    # Detect minimum price
    min_price_match = MIN_PRICE_PATTERN.search(text)

    if min_price_match:
        result["min_price"] = float(
            min_price_match.group(1)
        )

    # Remove filter phrases from keyword
    keyword = text

    for match in [
        max_price_match,
        min_price_match,
        size_match,
    ]:
        if match:
            keyword = keyword.replace(
                match.group(0),
                "",
            )

    # Remove detected store name/code
    if result["store"]:
        for alias in store_aliases:
            keyword = re.sub(
                rf"\b{re.escape(alias)}\b",
                "",
                keyword,
                flags=re.IGNORECASE,
            )

    # Remove common search words
    keyword = re.sub(
        r"\b(find|show|search|me|products?|jerseys?|"
        r"shirts?|available|with|size|under|below|"
        r"above|over|less than|more than|upto|up to)\b",
        " ",
        keyword,
        flags=re.IGNORECASE,
    )

    keyword = re.sub(
        r"\s+",
        " ",
        keyword,
    ).strip()

    result["keyword"] = keyword or None

    return result