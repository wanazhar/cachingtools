"""
ESG Endpoint - Handles ESG data retrieval and processing
"""

import requests
import pandas as pd
from tabulate import tabulate
from utils.display import print_header, clear_screen, print_menu

def handle(cache):
    """
    Handle ESG data operations
    
    Args:
        cache (CacheManager): The cache manager instance
    """
    while True:
        clear_screen()
        print_header("ESG Data")
        
        options = [
            "Get ESG Data for a Symbol",
            "View All Cached ESG Data",
            "Export ESG Data",
            "Return to Main Menu"
        ]
        
        choice = print_menu(options)
        
        if choice == 1:  # Get ESG data
            get_esg_data(cache)
        elif choice == 2:  # View all
            view_all_esg_data(cache)
        elif choice == 3:  # Export
            export_esg_data(cache)
        elif choice == 4:  # Return
            break
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

def get_esg_data(cache):
    """Get ESG data for a specific symbol."""
    symbol = input("\nEnter stock symbol (e.g., AAPL): ").strip().upper()
    
    if not symbol:
        print("No symbol entered.")
        return
    
    # Check if we have cached data
    cached_data = cache.get_cached_data("esg", symbol)
    
    if cached_data:
        print(f"\nFound cached ESG data for {symbol}.")
        refresh = input("Do you want to refresh from API? (y/N): ").strip().lower()
        
        if refresh != 'y':
            display_esg_data(cached_data, symbol)
            return
    
    # Check if we've reached API limit
    if cache.check_api_limit_reached():
        print("\nWARNING: Daily API request limit (250) reached.")
        if cached_data:
            print("Using cached data instead.")
            display_esg_data(cached_data, symbol)
        else:
            print("No cached data available for this symbol.")
        return
    
    # Make API request
    print(f"\nFetching ESG data for {symbol} from API...")
    
    endpoint = "/v4/esg-environmental-social-governance-data"
    url = f"{cache.base_url}{endpoint}?symbol={symbol}&apikey={cache.api_key}"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            if not data:
                print(f"No ESG data available for {symbol}.")
                return
            
            # Track the API request
            cache.track_api_request(endpoint)
            
            # Save to cache
            cache.save_data("esg", symbol, data)
            
            # Display the data
            display_esg_data(data, symbol)
            
        else:
            print(f"API request failed with status code {response.status_code}")
            
    except Exception as e:
        print(f"Error fetching ESG data: {str(e)}")

def display_esg_data(data, symbol):
    """Display ESG data in a readable format."""
    if not data:
        print("No data to display.")
        return
    
    # Convert to DataFrame for easier display
    df = pd.DataFrame(data)
    
    if 'date' in df.columns:
        df = df.sort_values('date', ascending=False)
    
    # Select relevant columns for display
    display_cols = [
        'date', 'environmentalScore', 'socialScore', 
        'governanceScore', 'total'
    ]
    
    # Filter columns that exist in the DataFrame
    display_cols = [col for col in display_cols if col in df.columns]
    
    if not display_cols:
        print("No relevant ESG data found.")
        return
    
    # Rename columns for better display
    rename_map = {
        'date': 'Date', 
        'environmentalScore': 'Environmental', 
        'socialScore': 'Social',
        'governanceScore': 'Governance', 
        'total': 'Total ESG'
    }
    
    display_df = df[display_cols].rename(columns={k: v for k, v in rename_map.items() if k in display_cols})
    
    # Print the data
    print(f"\nESG Data for {symbol}:")
    print(tabulate(display_df.head(10), headers="keys", tablefmt="pretty"))
    
    if len(df) > 10:
        print(f"\nShowing 10 of {len(df)} records. Export to view all data.")

def view_all_esg_data(cache):
    """View a summary of all cached ESG data."""
    clear_screen()
    print_header("All Cached ESG Data")
    
    query = """
    SELECT 
        symbol, 
        MAX(last_updated) as last_updated,
        COUNT(*) as data_points
    FROM cache_data
    WHERE data_type = 'esg'
    GROUP BY symbol
    """
    
    df = pd.read_sql_query(query, cache.db.conn)
    
    if df.empty:
        print("No ESG data cached yet.")
        return
    
    print(tabulate(df, headers="keys", tablefmt="pretty"))

def export_esg_data(cache):
    """Export ESG data to file."""
    from utils.export import export_data
    
    clear_screen()
    print_header("Export ESG Data")
    
    # Get available symbols
    cache.db.execute(
        "SELECT DISTINCT symbol FROM cache_data WHERE data_type = 'esg'"
    )
    results = cache.db.fetchall()
    symbols = [row[0] for row in results] if results else []
    
    if not symbols:
        print("No ESG data available to export.")
        return
    
    print("Available symbols:")
    for i, symbol in enumerate(symbols, 1):
        print(f"{i}. {symbol}")
    print(f"{len(symbols) + 1}. All Symbols")
    print(f"{len(symbols) + 2}. Cancel")
    
    choice = int(input(f"\nEnter choice (1-{len(symbols) + 2}): "))
    
    if choice == len(symbols) + 2:  # Cancel
        return
    
    if choice == len(symbols) + 1:  # All symbols
        symbols_to_export = symbols
    elif 1 <= choice <= len(symbols):
        symbols_to_export = [symbols[choice - 1]]
    else:
        print("Invalid choice.")
        return
    
    # Export data
    for symbol in symbols_to_export:
        cached_data = cache.get_cached_data("esg", symbol)
        if cached_data:
            export_data(cached_data, f"{symbol}_esg_data", "ESG data")
