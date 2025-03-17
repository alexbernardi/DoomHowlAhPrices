# SimpleAHScan

## Overview
SimpleAHScan is a lightweight World of Warcraft Classic addon that enables quick scanning of the Auction House. It provides a simple one-click solution for gathering auction data without complex filters or setups.

## Installation
1. Download the addon files
2. Extract the contents into your World of Warcraft Classic addons directory:
   - `C:\Program Files (x86)\World of Warcraft\_classic_era_\Interface\AddOns\`
3. Ensure the folder structure is maintained:
   ```
   SimpleAHScan/
   ├── SimpleAHScan.toc
   └── core.lua
   ```

## Features
- One-click scanning of the entire auction house
- Tracks cooldown for GetAll scans (15-minute cooldown)
- Saves recent scan data
- Visual feedback during scan operations
- Sound notifications when scans complete

## Usage
1. Open the Auction House by talking to an Auctioneer
2. Click the "Scan" button located in the bottom right of the Browse tab
3. Wait for the scan to complete (results will be displayed in chat)
4. The addon automatically saves data from your 10 most recent scans

## Commands
- `/simpleAH` - Access addon options

## Scan Cooldown
Full auction house scans using the GetAll function are limited by Blizzard to once every 15 minutes. The addon will show you the remaining cooldown time on the scan button.

## Data Storage
The addon saves the following information for each auction item:
- Item ID and name
- Item link and quality level
- Quantity
- Minimum bid (total and per item)
- Buyout price (total and per item)
- Owner name (if available)

## Support
For issues or feature requests, please report them through GitHub or contact the addon developer.