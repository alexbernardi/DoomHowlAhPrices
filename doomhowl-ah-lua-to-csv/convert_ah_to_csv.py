import re
import csv
import os

def parse_ah_data(file_path):
    """Parse the SimpleAHScan Lua file and extract auction data"""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    items = []
    
    # Find the entire data structure
    scan_match = re.search(r'SimpleAHScanData\s*=\s*\{(.*)\}', content, re.DOTALL)
    if not scan_match:
        print("Failed to match SimpleAHScanData structure")
        return items
        
    scan_content = scan_match.group(1)
    
    # Find faction and timestamp
    faction_match = re.search(r'\["faction"\]\s*=\s*"(.*?)"', scan_content)
    timestamp_match = re.search(r'\["timestamp"\]\s*=\s*(\d+)', scan_content)
    
    faction = faction_match.group(1) if faction_match else "Unknown"
    timestamp = timestamp_match.group(1) if timestamp_match else "0"
    
    # Find all item blocks directly
    item_pattern = r'\{\s*\["link"\]\s*=\s*"(.*?)"\s*,\s*\["id"\]\s*=\s*"(.*?)"\s*,.*?\["name"\]\s*=\s*"(.*?)"\s*,'
    item_matches = re.finditer(item_pattern, content, re.DOTALL)
    
    item_count = 0
    for item_match in item_matches:
        item_count += 1
        
        # Get the text around this match to extract all properties
        start_pos = item_match.start()
        # Find the closing brace for this item block
        block_text = content[start_pos:]
        end_pos = block_text.find("},")
        if end_pos == -1:
            end_pos = block_text.find("}")
        if end_pos != -1:
            item_text = block_text[:end_pos]
            
            # Create item dictionary with faction and timestamp
            item = {
                'faction': faction,
                'timestamp': timestamp,
                'link': item_match.group(1),
                'id': item_match.group(2),
                'name': item_match.group(3)
            }
            
            # Extract other properties
            for prop in ['count', 'level', 'quality', 'buyout', 'buyoutPerItem', 'minBid', 'minBidPerItem']:
                match = re.search(fr'\["{prop}"\]\s*=\s*([^,]+),', item_text)
                if match:
                    item[prop] = match.group(1).strip('"')
            
            items.append(item)
    
    print(f"Processed {item_count} items")
    return items

def write_to_csv(items, output_file):
    """Write parsed auction data to CSV file"""
    if not items:
        print("No items found to export")
        return
    
    # Define CSV columns
    fieldnames = ['name', 'id', 'count', 'buyoutPerItem', 'buyout', 'minBid', 
                 'minBidPerItem', 'level', 'quality', 'link', 'faction', 'timestamp']
    
    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for item in items:
            writer.writerow({field: item.get(field, '') for field in fieldnames})
    
    print(f"Exported {len(items)} items to {output_file}")

def main():
    # Set file paths
    lua_file = r"c:\Program Files (x86)\World of Warcraft\_classic_era_\WTF\Account\93532304#1\SavedVariables\SimpleAHScan.lua"
    output_file = "ah_scan_data.csv"
    
    # Check if file exists
    if not os.path.exists(lua_file):
        print(f"File not found: {lua_file}")
        return
    
    # Parse and export
    items = parse_ah_data(lua_file)
    write_to_csv(items, output_file)

if __name__ == "__main__":
    main()