import requests


def fetch_products(store_url):
    """
    Fetch all products from a Shopify store.

    Args:
        store_url: Base URL of the Shopify store.

    Returns:
        List of Shopify products.
    """

    products = []
    page = 1

    while True:
        url = (
            f"{store_url.rstrip('/')}"
            f"/products.json?limit=250&page={page}"
        )

        print(f"Fetching page {page}: {url}")

        response = requests.get(
            url,
            timeout=30,
            headers={
                "User-Agent": "Shopify-Inventory-Tracker/1.0"
            },
        )

        response.raise_for_status()

        data = response.json()
        batch = data.get("products", [])

        if not batch:
            break

        products.extend(batch)

        print(f"  Found {len(batch)} products")

        if len(batch) < 250:
            break

        page += 1

    print(f"Total products fetched: {len(products)}")

    return products


def fetch_all_stores(stores):
    """
    Fetch products from multiple Shopify stores.

    Args:
        stores: List of store configurations.

    Returns:
        List of dictionaries containing store information
        and the products fetched from each store.
    """

    results = []

    for store in stores:
        store_id = store["code"]
        store_name = store["name"]
        store_url = store["url"]

        print()
        print("=" * 60)
        print(f"Fetching store: {store_name}")
        print(f"URL: {store_url}")
        print("=" * 60)

        products = fetch_products(store_url)

        results.append(
            {
                "store_id": store_code,
                "store_name": store_name,
                "store_url": store_url,
                "products": products,
            }
        )

    return results
