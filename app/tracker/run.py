from config import load_stores
from app.database.models import init_db
from app.database.session import SessionLocal
from app.scraper.fetch import fetch_products
from app.scraper.sample import load_sample_products
from app.scraper.sync import sync_store


def run_tracker(demo=False):
    """
    Fetch and synchronize configured Shopify stores.

    When demo=True, sample data is used instead of making
    network requests to Shopify.
    """
    init_db()

    session = SessionLocal()
    all_results = []

    try:
        if demo:
            stores = [
                {
                    "code": "demo",
                    "name": "Demo Store",
                    "url": "https://demo.myshopify.com",
                }
            ]

            products = load_sample_products()

            summary = sync_store(
                session,
                stores[0],
                products,
            )

            all_results.append(
                {
                    "store": stores[0]["name"],
                    "summary": summary,
                }
            )

        else:
            stores = load_stores()

            for store_data in stores:
                print()
                print("=" * 60)
                print(f"Processing store: {store_data['name']}")
                print("=" * 60)

                products = fetch_products(store_data["url"])

                summary = sync_store(
                    session,
                    store_data,
                    products,
                )

                all_results.append(
                    {
                        "store": store_data["name"],
                        "summary": summary,
                    }
                )

        session.commit()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()

    return all_results


if __name__ == "__main__":
    results = run_tracker(demo=True)

    print()
    print("=" * 60)
    print("TRACKER COMPLETE")
    print("=" * 60)

    for result in results:
        summary = result["summary"]

        print(f"\nStore: {result['store']}")
        print(f"New products: {len(summary['new_products'])}")
        print(f"Price changes: {len(summary['price_changes'])}")
        print(f"Restocked: {len(summary['restocked'])}")
        print(f"Sold out: {len(summary['sold_out'])}")
        print(f"New sizes: {len(summary['new_sizes'])}")
        print(f"Removed sizes: {len(summary['removed_sizes'])}")
