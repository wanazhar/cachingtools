#!/usr/bin/env python3
"""
Financial Data Cache - CLI Tool

Access and cache financial data from Financial Modeling Prep API
with local storage to minimize API usage.
"""

import os
import sys
import argparse
from dotenv import load_dotenv
from tabulate import tabulate

from core.cache_manager import CacheManager
from utils.config import get_config
from utils.display import print_header, print_menu, clear_screen
from endpoints import get_available_endpoints

def display_logo():
    """Display the CachingTools ASCII art logo."""
    logo = r"""
   ______           __    _            ______            __    
  / ____/___ ______/ /_  (_)___  ____ /_  __/___  ____  / /____
 / /   / __ `/ ___/ __ \/ / __ \/ __ `// / / __ \/ __ \/ / ___/
/ /___/ /_/ / /__/ / / / / / / / /_/ // / / /_/ / /_/ / (__  ) 
\____/\__,_/\___/_/ /_/_/_/ /_/\__, //_/  \____/\____/_/____/  
                              /____/                           
    """
    print(logo)
    print("vibecoded by wanazhar x claude 3.7 sonnet\n")

def main():
    # Clear screen and display logo
    clear_screen()
    display_logo()
    
    # Load environment variables
    load_dotenv()
    
    # Check for API key
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        print("Error: FMP_API_KEY not found in .env file")
        print("Please create a .env file with your Financial Modeling Prep API key:")
        print("FMP_API_KEY=your_api_key_here")
        sys.exit(1)
    
    # Initialize cache manager
    cache = CacheManager(api_key)
    
    # Get available endpoints
    endpoints = get_available_endpoints()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Financial Data Cache CLI Tool")
    parser.add_argument("--summary", action="store_true", help="Show cache summary")
    args = parser.parse_args()
    
    # Show summary if requested
    if args.summary:
        display_summary(cache)
        sys.exit(0)
    
    # Main application loop
    while True:
        clear_screen()
        display_logo()
        print_header("Financial Data Cache Tool")
        
        # Display main menu
        options = ["View Cache Summary"]
        options.extend([endpoint.title() for endpoint in endpoints])
        options.extend(["Configure Settings", "Exit"])
        
        choice = print_menu(options)
        
        if choice == 1:  # Summary
            display_summary(cache)
        elif 2 <= choice < 2 + len(endpoints):  # Endpoints
            endpoint_name = endpoints[choice - 2]
            handle_endpoint(cache, endpoint_name)
        elif choice == 2 + len(endpoints):  # Settings
            configure_settings()
        elif choice == 2 + len(endpoints) + 1:  # Exit
            print("\nGoodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

def display_summary(cache):
    """Display a summary of all cached data."""
    clear_screen()
    display_logo()
    print_header("Cache Summary")
    
    # Get today's API usage
    usage = cache.get_daily_request_count()
    print(f"API Requests Today: {usage}/250\n")
    
    # Get all cached data summary
    all_data = cache.get_cache_summary()
    
    if all_data.empty:
        print("No data cached yet.")
    else:
        print(tabulate(all_data, headers="keys", tablefmt="pretty"))

def handle_endpoint(cache, endpoint_name):
    """Handle operations for a specific endpoint."""
    # Import the endpoint module dynamically
    module_name = f"endpoints.{endpoint_name}"
    endpoint_module = __import__(module_name, fromlist=[''])
    
    # Call the endpoint handler
    endpoint_module.handle(cache)

def configure_settings():
    """Configure application settings."""
    clear_screen()
    display_logo()
    print_header("Settings")
    
    config = get_config()
    
    print("Current Settings:")
    print(f"1. Database Path: {config.get('database_path', 'financial_data.db')}")
    print(f"2. Export Format: {config.get('export_format', 'xlsx')}")
    print(f"3. Export Directory: {config.get('export_dir', 'exports')}")
    print("4. Return to Main Menu")
    
    choice = int(input("\nEnter choice (1-4): "))
    
    if choice == 1:
        path = input("Enter new database path: ")
        config['database_path'] = path
    elif choice == 2:
        format_choice = input("Enter export format (csv/xlsx): ")
        if format_choice.lower() in ['csv', 'xlsx']:
            config['export_format'] = format_choice.lower()
    elif choice == 3:
        dir_path = input("Enter export directory: ")
        config['export_dir'] = dir_path
    
    # Save updated config
    if choice in [1, 2, 3]:
        from utils.config import save_config
        save_config(config)
        print("Settings updated successfully!")

if __name__ == "__main__":
    main()
