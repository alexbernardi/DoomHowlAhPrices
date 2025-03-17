import re
import csv
import os

def parse_ah_data(file_path):
    """Parse the SimpleAHScan Lua file and extract auction data"""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Find all auction items
    items = []
    
    # Find the nested data structure
    scans_match = re.search(r'\["scans"\] = \{\s*\{(.*?)\}\s*\}', content, re.DOTALL)
    if scans_match:
        scan_data = scans_match.group(1)
        
        # Extract faction and timestamp
        faction_match = re.search(r'\["faction"\] = "(.*?)"', scan_data)
        timestamp_match = re.search(r'\["timestamp"\] = ([0-9]+)', scan_data)
        
        faction = faction_match.group(1) if faction_match else "Unknown"
        timestamp = timestamp_match.group(1) if timestamp_match else "0"
        
        # Extract item data
        data_section = re.search(r'\["data"\] = \{(.*?)\}\s*,\s*(?:\["faction"\]|\})', scan_data, re.DOTALL)
        if data_section:
            item_blocks = re.finditer(r'\{(.*?)\},', data_section.group(1), re.DOTALL)
            
            for item_block in item_blocks:
                item_text = item_block.group(1)
                
                # Extract item properties
                item = {
                    'faction': faction,
                    'timestamp': timestamp
                }
                
                # Extract basic properties
                for prop in ['name', 'id', 'count', 'level', 'quality', 
                             'buyout', 'buyoutPerItem', 'minBid', 'minBidPerItem']:
                    match = re.search(fr'\["{prop}"\] = (.*?),', item_text)
                    if match:
                        value = match.group(1).strip('"')
                        item[prop] = value
                
                # Extract the item link separately as it has a special format
                link_match = re.search(r'\["link"\] = "(.*?)",', item_text)
                if link_match:
                    item['link'] = link_match.group(1)
                
                items.append(item)
    
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