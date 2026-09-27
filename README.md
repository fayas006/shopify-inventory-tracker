# Shopify Inventory Tracker

A lightweight Shopify inventory tracking system with multi-store
support, change detection, SQLite storage, natural-language product
search, and a Telegram bot.

## Features

-   Track products from multiple Shopify stores
-   Fetch Shopify products through the Shopify JSON product endpoint
-   Store products, variants, and images in SQLite
-   Detect inventory changes
-   Detect price changes
-   Detect new and removed sizes
-   Search inventory using natural-language queries
-   Retrieve product images using `/pic <id>`
-   Telegram bot interface
-   Demo mode using sample data
-   Live mode using configured Shopify stores
-   Configuration-based multi-store support

## Architecture

``` text
Shopify Stores
      |
      v
Shopify JSON API
      |
      v
Inventory Tracker
      |
      v
SQLite
   /     \
  v       v
Search  Telegram Bot
          /    \
         v      v
      Search  /pic <id>
```

## Project Structure

``` text
shopify-inventory-tracker/
├── app/
│   ├── ai/
│   ├── database/
│   ├── scraper/
│   └── tracker/
├── config/
│   ├── stores.example.json
│   └── stores.json
├── sample_data/
│   └── products.json
├── .env.example
├── .gitignore
├── main.py
├── requirements.txt
└── README.md
```

## Requirements

-   Python 3.10+
-   A Shopify store with products available through the Shopify JSON
    product endpoint
-   A Telegram Bot Token if using the Telegram bot

## Installation

Clone the repository:

``` bash
git clone https://github.com/fayas006/shopify-inventory-tracker
cd shopify-inventory-tracker
```

Create a virtual environment:

``` bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

``` bash
pip install -r requirements.txt
```

## Demo Mode

The project includes sample Shopify product data, so it can be tested
without connecting to a real store.

Run:

``` bash
python main.py
```

This creates a local SQLite database and loads the sample inventory.

Demo data is stored in `sample_data/products.json`.

## Shopify Store Configuration

Copy the example configuration:

``` bash
cp config/stores.example.json config/stores.json
```

Edit `config/stores.json`:

``` json
{
  "stores": [
    {
      "code": "store1",
      "name": "My First Store",
      "url": "https://store1.myshopify.com"
    },
    {
      "code": "store2",
      "name": "My Second Store",
      "url": "https://store2.myshopify.com"
    }
  ]
}
```

Additional stores can be added to the `stores` array.

The private `stores.json` file is excluded from Git.

## Live Tracking

After configuring your stores:

``` bash
python main.py --live
```

The tracker fetches products from each configured store and synchronizes
them with SQLite.

Detected changes include:

-   New products
-   Price changes
-   Restocked products
-   Sold-out products
-   New sizes
-   Removed sizes
-   Title changes
-   Description changes

## Telegram Bot

Create a Telegram bot and obtain its bot token.

Create a local `.env` file:

``` bash
cp .env.example .env
```

Add your token:

``` env
AI_BOT_TOKEN=your_telegram_bot_token
```

Start the bot:

``` bash
python -m app.ai.bot_polling
```

The bot uses the same SQLite inventory database created by the tracker.

## Telegram Search

The bot supports natural-language inventory searches.

Examples:

``` text
real madrid
real madrid size M
real madrid under 400
real madrid size M under 400
store1 barcelona XL
```

The parser extracts:

-   Product keywords
-   Store
-   Size
-   Maximum price
-   Minimum price

The search is performed against the SQLite inventory database.

## Product Images

Retrieve a product image with:

``` text
/pic <product_id>
```

Example:

``` text
/pic 1001
```

The bot retrieves the product from SQLite and sends its stored product
image through Telegram.

## Configuration

Environment variables are stored in `.env`.

Example:

``` env
AI_BOT_TOKEN=your_telegram_bot_token
CHAT_ID=your_telegram_chat_id
```

Never commit `.env` or other files containing credentials.

## Database

The project uses SQLite through SQLAlchemy.

The database contains:

-   Stores
-   Products
-   Variants
-   Product images

The generated database file is excluded from Git.

A fresh database can be generated with:

``` bash
python main.py
```

## Security

The repository is designed so private configuration and generated data
are not committed.

Excluded files include:

``` text
.env
config/stores.json
*.db
__pycache__/
```

Do not commit:

-   Telegram bot tokens
-   Private store configuration
-   Private inventory data
-   Database files containing real inventory

## Development

Run the demo tracker:

``` bash
python main.py
```

Check available options:

``` bash
python main.py --help
```

Run the Telegram bot locally:

``` bash
python -m app.ai.bot_polling
```

## License

This project is available for portfolio and educational purposes.
