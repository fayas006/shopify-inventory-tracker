import argparse

from app.tracker.run import run_tracker


def main():
    parser = argparse.ArgumentParser(
        description="Shopify Inventory Tracker"
    )

    parser.add_argument(
        "--live",
        action="store_true",
        help="Fetch products from configured Shopify stores",
    )

    args = parser.parse_args()

    results = run_tracker(
        demo=not args.live
    )

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


if __name__ == "__main__":
    main()