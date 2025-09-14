# Shopify Collection Weekly Automation

This repository contains an automated workflow for managing Shopify collections by fetching new products weekly and updating collections automatically.

## Overview

The automation script helps maintain up-to-date product collections by:

- **Fetching new Shopify products** added within the last week
- **Clearing existing manual collections** to remove outdated products
- **Updating collections** with fresh, relevant products
- **Scheduling regular automation** to run weekly

## Features

- 🛍️ **Product Discovery**: Automatically finds new products based on creation date
- 🔄 **Collection Management**: Clears and updates existing collections
- ⏰ **Weekly Scheduling**: Configurable automation timing
- 📊 **Logging & Monitoring**: Detailed logging for tracking automation status
- 🔧 **Configurable**: Easy setup with environment variables

## Files

- `shopify_collection_update.py` - Main automation script
- `README.md` - This documentation

## Setup

1. **Environment Variables**: Set up your Shopify API credentials
   ```
   SHOPIFY_API_KEY=your_api_key
   SHOPIFY_PASSWORD=your_password
   SHOPIFY_SHOP_NAME=your_shop_name
   COLLECTION_ID=your_collection_id
   ```

2. **Dependencies**: Install required Python packages
   ```bash
   pip install requests python-dotenv
   ```

3. **Schedule**: Configure your preferred scheduling method (cron, GitHub Actions, etc.)

## Usage

Run the script manually:
```bash
python shopify_collection_update.py
```

Or set up automated scheduling using your preferred method.

## How It Works

1. **Authentication**: Connects to Shopify using Admin API credentials
2. **Product Filtering**: Queries for products created in the last 7 days
3. **Collection Update**: Removes old products and adds new ones to the specified collection
4. **Logging**: Records all actions and any errors encountered

## Requirements

- Python 3.7+
- Shopify Admin API access
- Valid Shopify store credentials

## License

This project is open source and available under the MIT License.
