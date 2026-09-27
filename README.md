# Shopify Inventory Tracker

A reusable Shopify inventory automation system with multi-store support, inventory change detection, natural-language Telegram search, product image lookup, and scheduled daily change reports.

The project supports local SQLite development and cloud deployment with a shared PostgreSQL database.

## Features

- Track products from multiple Shopify stores
- Fetch Shopify products through the Shopify JSON product endpoint
- Store products, variants, and images using SQLAlchemy
- Detect inventory changes
- Detect price changes
- Detect new and removed sizes
- Detect restocks and sold-out products
- Natural-language inventory search through Telegram
- Product image lookup with `/pic <id>`
- Dedicated Telegram tracker bot for daily change reports
- Daily inventory synchronization
- Configurable database through `DATABASE_URL`
- SQLite support for local/demo use
- PostgreSQL support for cloud deployments
- Demo mode using sample data
- Live mode using configured Shopify stores
- Configuration-based multi-store support

## Architecture

```text
                    Shopify Stores
                          |
                          v
                  Shopify JSON API
                          |
                          v
                  Daily Inventory Sync
                     (scheduled)
                          |
                          v
                 Shared Database
                /                \
               v                  v
       Inventory Search      Change Detection
               |                  |
               v                  v
       Inventory Bot          Tracker Bot
         (24/7)              (daily report)
```

For cloud deployments, the Inventory Bot and Daily Tracker can run as separate processes while sharing the same PostgreSQL database.

```text
                    PostgreSQL
                   /          \
                  /            \
       Inventory Bot       Daily Tracker
        (24/7)              (8:30 AM)
            |                    |
            v                    v
        Telegram             Shopify
```

The application is hosting-provider agnostic. It can be adapted to Render, Railway, AWS, a VPS, Docker-based hosting, or another platform that can run Python processes and provide PostgreSQL.

## Project Structure

```text
shopify-inventory-tracker/
├── app/
│   ├── ai/
│   │   ├── bot.py
│   │   ├── bot_polling.py
│   │   ├── export.py
│   │   ├── parser.py
│   │   └── search.py
│   ├── bot/
│   │   ├── telegram.py
│   │   └── tracker.py
│   ├── database/
│   │   ├── init.py
│   │   ├── models.py
│   │   └── session.py
│   ├── scraper/
│   │   ├── compare.py
│   │   ├── fetch.py
│   │   ├── sample.py
│   │   └── sync.py
│   └── tracker/
│       └── run.py
├── config/
│   ├── stores.example.json
│   └── stores.json
├── scripts/
│   └── daily_sync.py
├── sample_data/
│   └── products.json
├── .env.example
├── .gitignore
├── main.py
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.10+
- Shopify store access
- Telegram bot for interactive inventory search
- Separate Telegram bot for daily tracker reports
- PostgreSQL for multi-process cloud deployment
- SQLite for local/demo use

## Installation

Clone the repository:

```bash
git clone https://github.com/fayas006/shopify-inventory-tracker
cd shopify-inventory-tracker
```

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Local Demo

The project includes sample Shopify product data and can be tested without connecting to a real store.

Run:

```bash
python main.py
```

When `DATABASE_URL` is not configured, the project automatically uses:

```text
sqlite:///tracker.db
```

Demo data is stored in:

```text
sample_data/products.json
```

The generated SQLite database is excluded from Git.

## Shopify Store Configuration

Copy the example configuration:

```bash
cp config/stores.example.json config/stores.json
```

Edit `config/stores.json` with the stores you want to track:

```json
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

After configuring the stores:

```bash
python main.py --live
```

The tracker fetches products from each configured store and synchronizes them with the database.

Detected changes include:

- New products
- Price changes
- Restocked products
- Sold-out products
- New sizes
- Removed sizes
- Title changes
- Description changes

## Daily Tracker

The daily tracker performs a live synchronization and sends the detected changes through the dedicated Tracker Bot.

Run manually with:

```bash
python scripts/daily_sync.py
```

In a cloud deployment, schedule this command to run every day at **8:30 AM**.

The application does not hardcode the schedule. The hosting platform's scheduler controls when the command runs.

## Telegram Bots

The project uses two separate Telegram bots.

### Inventory Bot

The Inventory Bot provides interactive inventory search.

Start it locally:

```bash
python -m app.ai.bot_polling
```

Configure:

```env
AI_BOT_TOKEN=your_inventory_bot_token
```

Example queries:

```text
real madrid
real madrid size M
real madrid under 400
real madrid size M under 400
store1 barcelona XL
```

The parser extracts:

- Product keywords
- Store
- Size
- Maximum price
- Minimum price

### Tracker Bot

The Tracker Bot sends the daily inventory change report.

Configure:

```env
TRACKER_BOT_TOKEN=your_tracker_bot_token
TRACKER_CHAT_ID=your_tracker_chat_id
```

The daily tracker runs:

```bash
python scripts/daily_sync.py
```

and sends the resulting change summary to the configured Telegram chat.

## Product Images

Retrieve a product image using:

```text
/pic <product_id>
```

Example:

```text
/pic 1001
```

The bot retrieves the product and sends its stored image through Telegram.

## Environment Variables

Create a local `.env` file:

```bash
cp .env.example .env
```

Example:

```env
# Interactive inventory Telegram bot
AI_BOT_TOKEN=your_inventory_bot_token

# Daily tracker Telegram bot
TRACKER_BOT_TOKEN=your_tracker_bot_token
TRACKER_CHAT_ID=your_tracker_chat_id

# Database
# Leave unset for local SQLite.
# Set this to PostgreSQL for cloud deployment.
DATABASE_URL=sqlite:///tracker.db
```

Never commit `.env` or credentials.

## Database

The project uses SQLAlchemy and supports two database modes.

### Local / Demo

If `DATABASE_URL` is not set, SQLite is used:

```text
sqlite:///tracker.db
```

### Cloud

For a deployment where the Inventory Bot and Daily Tracker run as separate processes, use PostgreSQL:

```env
DATABASE_URL=postgresql://username:password@host:5432/database
```

Both processes should use the same `DATABASE_URL` so they share the same inventory data.

```text
                  PostgreSQL
                 /          \
                /            \
       Inventory Bot      Daily Tracker
           24/7              8:30 AM
```

## Deployment

The application is designed to be hosting-provider agnostic.

A typical cloud setup contains two processes.

### Inventory Bot

Runs continuously:

```bash
python -m app.ai.bot_polling
```

### Daily Tracker

Runs once per day:

```bash
python scripts/daily_sync.py
```

Schedule the tracker for 8:30 AM in the desired timezone.

Both processes should point to the same PostgreSQL database.

The user provides their own:

- GitHub repository
- Shopify store configuration
- Telegram bot tokens
- PostgreSQL database
- Cloud hosting account

The repository does not contain personal store data or credentials.

## Example Cloud Architecture

```text
                    User's Cloud
                         |
          ┌──────────────┴──────────────┐
          |                             |
          v                             v
   Inventory Bot                 Daily Tracker
      24/7                       Every day 8:30
          |                             |
          └──────────────┬──────────────┘
                         v
                    PostgreSQL
                         |
                         v
                  Shopify Stores
```

The exact cloud provider can vary. Render, Railway, AWS, VPS hosting, Docker-compatible platforms, and similar services can run the processes as long as they provide the required Python runtime and persistent PostgreSQL database.

## Security

Private configuration and generated data are excluded from Git.

Ignored files include:

```text
.env
config/stores.json
*.db
__pycache__/
```

Do not commit:

- Telegram bot tokens
- PostgreSQL credentials
- Private Shopify store configuration
- Private inventory data
- Database files containing real inventory

## Development Commands

Run the demo tracker:

```bash
python main.py
```

Run live tracking:

```bash
python main.py --live
```

Run the daily synchronization:

```bash
python scripts/daily_sync.py
```

Run the interactive Telegram bot:

```bash
python -m app.ai.bot_polling
```

Check command-line options:

```bash
python main.py --help
```

## License

This project is available for portfolio and educational purposes.
