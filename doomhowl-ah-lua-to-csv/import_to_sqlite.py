import pandas as pd
import sqlite3
import numpy as np
import os
from datetime import datetime

def import_csv_to_sqlite(csv_file, db_file):
    # Read CSV file
    print(f"Reading CSV file: {csv_file}")
    df = pd.read_csv(csv_file)

    # Filter out records with buyout = 0
    print("Filtering out records with zero buyout...")
    df = df[df['buyoutPerItem'] > 0]
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    
    # Group by item_id and name to aggregate
    print("Aggregating data by item...")
    grouped = df.groupby(['id', 'name', 'timestamp']).agg({
        'count': 'sum',  # Total count of items across all listings
        'buyoutPerItem': ['min', 'max', 'mean', 'median', 'std']
    }).reset_index()
    
    # Flatten column names
    grouped.columns = ['item_id', 'name', 'scan_timestamp', 
                      'total_quantity', 
                      'min_buyout_per_unit', 'max_buyout_per_unit', 
                      'mean_buyout_per_unit', 'median_buyout_per_unit', 
                      'std_dev_per_unit']
    
    # Calculate pressure metrics (simplified approach)
    print("Calculating price pressure metrics...")
    pressure_results = []
    
    for item_id in grouped['item_id'].unique():
        item_df = df[df['id'] == str(item_id)]
        item_row = grouped[grouped['item_id'] == item_id].iloc[0]
        
        min_price = item_row['min_buyout_per_unit'] 
        max_price = item_row['max_buyout_per_unit']
        
        min_threshold = min_price * 1.1  # Within 10% of minimum price
        max_threshold = max_price * 0.9  # Within 10% of maximum price
        
        # Calculate items near min and max price
        near_min_items = item_df[item_df['buyoutPerItem'] <= min_threshold]['count'].sum()
        near_max_items = item_df[item_df['buyoutPerItem'] >= max_threshold]['count'].sum()
        
        total_items = item_row['total_quantity']
        
        # Calculate pressure as percentage
        min_pressure = near_min_items / total_items if total_items > 0 else 0
        max_pressure = near_max_items / total_items if total_items > 0 else 0
        
        pressure_results.append((item_id, min_pressure, max_pressure))
    
    # Add pressure metrics to grouped DataFrame
    for item_id, min_pressure, max_pressure in pressure_results:
        idx = grouped[grouped['item_id'] == item_id].index
        grouped.loc[idx, 'min_pressure'] = min_pressure
        grouped.loc[idx, 'max_pressure'] = max_pressure
    
    # Connect to SQLite database
    print(f"Connecting to database: {db_file}")
    conn = sqlite3.connect(db_file)
    
    # Create table if it doesn't exist
    conn.execute('''
    CREATE TABLE IF NOT EXISTS ah_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER,
        name TEXT,
        scan_timestamp DATETIME,
        total_quantity INTEGER,
        min_buyout_per_unit REAL,
        max_buyout_per_unit REAL,
        mean_buyout_per_unit REAL,
        median_buyout_per_unit REAL,
        std_dev_per_unit REAL,
        min_pressure REAL,
        max_pressure REAL
    )
    ''')
    
    # Insert data into the database
    print("Inserting data into database...")
    grouped.to_sql('ah_items', conn, if_exists='append', index=False)
    
    # Close connection
    conn.close()
    print("Import completed successfully!")

if __name__ == "__main__":
    csv_file = "ah_scan_data.csv"
    db_file = r"C:\Users\ajrb7\Desktop\DoomHowlAhPrices\doomhowl-ah-database\doomhowl-ah-database"
    
    if os.path.exists(csv_file):
        import_csv_to_sqlite(csv_file, db_file)
    else:
        print(f"Error: CSV file '{csv_file}' not found.")