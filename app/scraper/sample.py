import json
from pathlib import Path


def load_sample_products():
    """
    Load sample Shopify products for offline testing.
    """
    file_path = (
        Path(__file__).resolve().parents[2]
        / "sample_data"
        / "products.json"
    )

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)
