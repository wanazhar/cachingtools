import requests
import pandas as pd
from tabulate import tabulate
from utils.display import print_header, clear_screen, print_menu

def handle(cache):
    """Handle SEC Filings data operations"""
    while True:
        clear_screen()
        print_header("SEC Filings Data")
        
        options = [
            "Get SEC Filings for a Symbol",
            "View All Cached Filings",
            "Export Filings Data",
            "Return to Main Menu"
        ]
        
        choice = print_menu(options)
        
        if choice == 1:
            get_sec_filings(cache)
        elif choice == 2:
            view_all_filings(cache)
        elif choice == 3:
            export_sec_filings(cache)
        elif choice == 4:
            break
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

def get_sec_filings(cache):
    """Get SEC filings data for a specific symbol."""
    symbol = input("\nEnter stock symbol (e.g., AAPL): ").strip().upper()
    
    if not symbol:
        print("No symbol entered.")
        return
    
    cached_data = cache.get_cached_data("filings", symbol)
    
    if cached_data:
        print(f"\nFound cached filings data for {symbol}.")
        refresh = input("Do you want to refresh from API? (y/N): ").strip().lower()
        if refresh != 'y':
            display_sec_filings(cached_data, symbol)
            return
    
    if cache.check_api_limit_reached():
        print("\nWARNING: Daily API request limit (250) reached.")
        if cached_data:
            print("Using cached data instead.")
            display_sec_filings(cached_data, symbol)
        else:
            print("No cached data available for this symbol.")
        return
    
    print(f"\nFetching SEC filings data for {symbol} from API...")
    endpoint = "/v3/sec_filings"
    url = f"{cache.base_url}{endpoint}/{symbol}?apikey={cache.api_key}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if not data:
                print(f"No filings data available for {symbol}.")
                return
            cache.track_api_request(endpoint)
            cache.save_data("filings", symbol, data)
            display_sec_filings(data, symbol)
        else:
            print(f"API request failed with status code {response.status_code}")
    except Exception as e:
        print(f"Error fetching filings data: {str(e)}")

def display_sec_filings(data, symbol):
    """Display SEC filings data in a readable format."""
    if not data:
        print("No data to display.")
        return
    
    df = pd.DataFrame(data)
    if 'filingDate' in df.columns:
        df = df.sort_values('filingDate', ascending=False)
    
    display_cols = ['filingDate', 'type', 'title']
    display_cols = [col for col in display_cols if col in df.columns]
    
    if not display_cols:
        print("No relevant filings data found.")
        return
    
    rename_map = {
        'filingDate': 'Date',
        'type': 'Type',
        'title': 'Title'
    }
    
    display_df = df[display_cols].rename(columns={k: v for k, v in rename_map.items() if k in display_cols})
    print(f"\nSEC Filings Data for {symbol}:")
    print(tabulate(display_df.head(10), headers="keys", tablefmt="pretty"))
    
    if len(df) > 10:
        print(f"\nShowing 10 of {len(df)} records. Export to view all data.")

def view_all_filings(cache):
    """View a summary of all cached filings."""
    clear_screen()
    print_header("All Cached SEC Filings Data")
    
    query = """
    SELECT symbol, MAX(last_updated) as last_updated, COUNT(*) as data_points
    FROM cache_data
    WHERE data_type = 'filings'
    GROUP BY symbol
    """
    
    df = pd.read_sql_query(query, cache.db.conn)
    
    if df.empty:
        print("No filings data cached yet.")
        return
    
    print(tabulate(df, headers="keys", tablefmt="pretty"))

def export_sec_filings(cache):
    """Export SEC filings data to file."""
    from utils.export import export_data
    clear_screen()
    print_header("Export SEC Filings Data")
    
    cache.db.execute("SELECT DISTINCT symbol FROM cache_data WHERE data_type = 'filings'")
    results = cache.db.fetchall()
    symbols = [row[0] for row in results] if results else []
    
    if not symbols:
        print("No filings data available to export.")
        return
    
    print("Available symbols:")
    for i, symbol in enumerate(symbols, 1):
        print(f"{i}. {symbol}")
    print(f"{len(symbols) + 1}. All Symbols")
    print(f"{len(symbols) + 2}. Cancel")
    
    choice = int(input(f"\nEnter choice (1-{len(symbols) + 2}): "))
    
    if choice == len(symbols) + 2:
        return
    
    symbols_to_export = symbols if choice == len(symbols) + 1 else [symbols[choice - 1]] if 1 <= choice <= len(symbols) else []
    
    if not symbols_to_export:
        print("Invalid choice.")
        return
    
    for symbol in symbols_to_export:
        cached_data = cache.get_cached_data("filings", symbol)
        if cached_data:
            export_data(cached_data, f"{symbol}_filings", "SEC Filings data")
