import requests
import pandas as pd
from tabulate import tabulate
from utils.display import print_header, clear_screen, print_menu

def handle(cache):
    """Handle Stock Splits data operations"""
    while True:
        clear_screen()
        print_header("Stock Splits Data")
        
        options = [
            "Get Stock Splits for a Symbol",
            "View All Cached Splits",
            "Export Splits Data",
            "Return to Main Menu"
        ]
        
        choice = print_menu(options)
        
        if choice == 1:
            get_stock_splits(cache)
        elif choice == 2:
            view_all_splits(cache)
        elif choice == 3:
            export_stock_splits(cache)
        elif choice == 4:
            break
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

def get_stock_splits(cache):
    """Get stock splits data for a specific symbol."""
    symbol = input("\nEnter stock symbol (e.g., AAPL): ").strip().upper()
    
    if not symbol:
        print("No symbol entered.")
        return
    
    cached_data = cache.get_cached_data("splits", symbol)
    
    if cached_data:
        print(f"\nFound cached splits data for {symbol}.")
        refresh = input("Do you want to refresh from API? (y/N): ").strip().lower()
        if refresh != 'y':
            display_stock_splits(cached_data, symbol)
            return
    
    if cache.check_api_limit_reached():
        print("\nWARNING: Daily API request limit (250) reached.")
        if cached_data:
            print("Using cached data instead.")
            display_stock_splits(cached_data, symbol)
        else:
            print("No cached data available for this symbol.")
        return
    
    print(f"\nFetching stock splits data for {symbol} from API...")
    endpoint = "/v3/historical-price-full/stock_split"
    url = f"{cache.base_url}{endpoint}/{symbol}?apikey={cache.api_key}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if not data or 'historical' not in data:
                print(f"No splits data available for {symbol}.")
                return
            cache.track_api_request(endpoint)
            cache.save_data("splits", symbol, data['historical'])
            display_stock_splits(data['historical'], symbol)
        else:
            print(f"API request failed with status code {response.status_code}")
    except Exception as e:
        print(f"Error fetching splits data: {str(e)}")

def display_stock_splits(data, symbol):
    """Display stock splits data in a readable format."""
    if not data:
        print("No data to display.")
        return
    
    df = pd.DataFrame(data)
    if 'date' in df.columns:
        df = df.sort_values('date', ascending=False)
    
    display_cols = ['date', 'numerator', 'denominator', 'splitRatio']
    display_cols = [col for col in display_cols if col in df.columns]
    
    if not display_cols:
        print("No relevant splits data found.")
        return
    
    rename_map = {
        'date': 'Date',
        'numerator': 'Numerator',
        'denominator': 'Denominator',
        'splitRatio': 'Split Ratio'
    }
    
    display_df = df[display_cols].rename(columns={k: v for k, v in rename_map.items() if k in display_cols})
    print(f"\nStock Splits Data for {symbol}:")
    print(tabulate(display_df.head(10), headers="keys", tablefmt="pretty"))
    
    if len(df) > 10:
        print(f"\nShowing 10 of {len(df)} records. Export to view all data.")

def view_all_splits(cache):
    """View a summary of all cached splits."""
    clear_screen()
    print_header("All Cached Stock Splits Data")
    
    query = """
    SELECT symbol, MAX(last_updated) as last_updated, COUNT(*) as data_points
    FROM cache_data
    WHERE data_type = 'splits'
    GROUP BY symbol
    """
    
    df = pd.read_sql_query(query, cache.db.conn)
    
    if df.empty:
        print("No splits data cached yet.")
        return
    
    print(tabulate(df, headers="keys", tablefmt="pretty"))

def export_stock_splits(cache):
    """Export stock splits data to file."""
    from utils.export import export_data
    clear_screen()
    print_header("Export Stock Splits Data")
    
    cache.db.execute("SELECT DISTINCT symbol FROM cache_data WHERE data_type = 'splits'")
    results = cache.db.fetchall()
    symbols = [row[0] for row in results] if results else []
    
    if not symbols:
        print("No splits data available to export.")
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
        cached_data = cache.get_cached_data("splits", symbol)
        if cached_data:
            export_data(cached_data, f"{symbol}_splits", "Stock Splits data")
