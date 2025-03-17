# DoomHowl Auction House Price Tracker

A complete solution for tracking World of Warcraft auction house prices on the Doom Howl server, featuring data collection via addon, ETL pipeline, and web visualization.

## 📊 Project Overview

This project consists of four main components:

1. **WoW Addon** - SimpleAHScan for data collection in-game
2. **ETL Pipeline** - Extraction, transformation, and loading of auction data
3. **Database** - SQLite storage of processed auction data
4. **Web Application** - React frontend to visualize and analyze price trends

## 🎮 SimpleAHScan WoW Addon

### About
SimpleAHScan is an addon for World of Warcraft that automatically scans the auction house and saves the data to a LUA file. This allows for tracking of item prices over time.

### Installation
1. Download the SimpleAHScan addon
2. Place it in your `World of Warcraft\_classic_era_\Interface\AddOns\` directory
3. Enable the addon in-game through the addon menu

### Usage
1. Open the Auction House in-game
2. The addon will automatically scan and collect data
3. Data is saved to: `World of Warcraft\_classic_era_\WTF\Account\{ACCOUNT_ID}\SavedVariables\SimpleAHScan.lua`

## 🔄 ETL Pipeline

### 1️⃣ Extraction: LUA to CSV

The convert_ah_to_csv.py script extracts auction data from the addon's LUA file:

```python
# Extract data from SimpleAHScan.lua to CSV
python convert_ah_to_csv.py
```

**How it works:**
- Parses the LUA file using regex to extract structured data
- Captures item details: name, ID, prices (buyout and bid), quality, etc.
- Adds metadata like faction and timestamp
- Exports all data to a CSV file for further processing

### 2️⃣ Transformation

The transformation process normalizes and enriches the raw data:

- **Data Cleaning**: Removing duplicates and invalid entries
- **Price Normalization**: Converting copper prices to gold
- **Item Classification**: Categorizing items by type
- **Historical Analysis**: Calculating price trends over time

### 3️⃣ Loading to SQLite

The final step loads the processed data into a SQLite database:

```python
# Load processed CSV data into SQLite
python load_to_sqlite.py
```

**Database Schema:**
- `items`: Master item list with static properties
- `auctions`: Individual auction listings
- `price_history`: Historical price aggregations
- `market_stats`: Market analysis and trends

## 💻 Web Application

A React-based web application provides visualization and analysis tools:

- **Real-time Price Tracking**: Current auction house listings
- **Historical Trends**: Price history charts
- **Market Analysis**: Identify profitable items
- **Battle.net API Integration**: Enhanced item data

### Setup & Deployment

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Deploy to Vercel
git push
```

## 🛠️ Technical Requirements

- **WoW Classic Era Client** for the addon
- **Python 3.7+** for ETL pipeline
- **Node.js** for web application
- **Battle.net Developer Account** for API access

## 📋 Complete Workflow

1. Collect data using the SimpleAHScan addon in-game
2. Run the extraction script to convert LUA to CSV
3. Process the data through transformation scripts
4. Load the data into SQLite database
5. Visualize and analyze using the web application

## 🔗 Additional Resources

- [SimpleAHScan Addon Documentation](https://example.com)
- [Battle.net API Documentation](https://develop.battle.net/documentation)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

## 📄 License

MIT