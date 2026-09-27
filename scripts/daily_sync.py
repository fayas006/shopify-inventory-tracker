import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.tracker.run import run_tracker
from app.bot.tracker import send_tracker_report


def main():
    print("Starting daily Shopify inventory sync...")

    results = run_tracker(demo=False)

    print("\nDaily sync complete.")

    for result in results:
        summary = result["summary"]

        print(f"\nStore: {result['store']}")
        print(f"New products: {len(summary['new_products'])}")
        print(f"Price changes: {len(summary['price_changes'])}")
        print(f"Restocked: {len(summary['restocked'])}")
        print(f"Sold out: {len(summary['sold_out'])}")
        print(f"New sizes: {len(summary['new_sizes'])}")
        print(f"Removed sizes: {len(summary['removed_sizes'])}")

    print("\nSending tracker report to Telegram...")

    send_tracker_report(results)

    print("Tracker report sent successfully.")


if __name__ == "__main__":
    main()
