import json
from pathlib import Path


CONFIG_FILE = Path(__file__).parent / "stores.json"


def load_stores():
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            "config/stores.json not found. "
            "Copy config/stores.example.json to config/stores.json "
            "and configure your Shopify stores."
        )

    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        config = json.load(file)

    stores = config.get("stores", [])

    if not stores:
        raise ValueError("No Shopify stores configured.")

    return stores
