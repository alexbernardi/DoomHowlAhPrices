"""
World of Warcraft Auction House Data Processing Pipeline

This script:
1. Watches for changes to the SimpleAHScan.lua file
2. Converts the Lua data to CSV format
3. Imports the CSV data to SQLite database
4. Cleans up temporary CSV files

Usage:
    Run this script in the background while playing World of Warcraft.
    Press Ctrl+C to exit.

Requirements:
    - watchdog library
    - convert_ah_to_csv.py script
    - import_to_sqlite.py script
"""
import time
import os
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Path to the Lua file
lua_file = r"c:\Program Files (x86)\World of Warcraft\_classic_era_\WTF\Account\93532304#1\SavedVariables\SimpleAHScan.lua"
# Get the directory of the Lua file
lua_dir = os.path.dirname(lua_file)
# Path to the CSV file
csv_file = "ah_scan_data.csv"

class AHDataProcessor(FileSystemEventHandler):
    """
    Handles the processing workflow when the Lua file changes:
    1. Convert Lua data to CSV
    2. Import CSV data to SQLite
    3. Delete the temporary CSV file
    """
    def on_modified(self, event):
        if not event.is_directory and event.src_path == lua_file:
            logger.info(f"Change detected in {lua_file}")
            
            try:
                # Step 1: Convert Lua to CSV
                logger.info("Converting Lua to CSV...")
                convert_result = subprocess.run(
                    [sys.executable, 'convert_ah_to_csv.py'], 
                    capture_output=True, 
                    text=True
                )
                
                if convert_result.returncode != 0:
                    logger.error(f"Conversion error: {convert_result.stderr}")
                    return
                
                logger.info(convert_result.stdout.strip())
                
                if not os.path.exists(csv_file):
                    logger.error(f"CSV file {csv_file} was not created.")
                    return
                
                # Step 2: Import CSV to SQLite
                logger.info("Importing to SQLite database...")
                import_result = subprocess.run(
                    [sys.executable, 'import_to_sqlite.py'], 
                    capture_output=True, 
                    text=True
                )
                
                if import_result.returncode != 0:
                    logger.error(f"Import error: {import_result.stderr}")
                    return
                
                logger.info(import_result.stdout.strip())
                
                # Step 3: Delete the CSV file
                logger.info(f"Cleaning up temporary file {csv_file}...")
                try:
                    os.remove(csv_file)
                    logger.info("Cleanup complete.")
                except Exception as e:
                    logger.error(f"Failed to delete CSV file: {e}")
                    
            except Exception as e:
                logger.error(f"Processing error: {e}")

def main():
    """Set up file monitoring and handle graceful shutdown."""
    event_handler = AHDataProcessor()
    observer = Observer()
    observer.schedule(event_handler, lua_dir, recursive=False)
    
    try:
        observer.start()
        logger.info(f"Watching for changes in {lua_file}...")
        logger.info("Press Ctrl+C to stop watching")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        observer.stop()
        
    observer.join()
    logger.info("Process terminated.")

if __name__ == "__main__":
    main()