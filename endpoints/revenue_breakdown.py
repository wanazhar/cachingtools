import requests
import pandas as pd
from tabulate import tabulate
from utils.display import print_header, clear_screen, print_menu

def handle(cache):
    """Handle Revenue Breakdown data operations"""
    while True:
        clear_screen()
        print_header("Revenue Breakdown Data")
        
        options = [
            "Get Revenue Breakdown for a Symbol",
            "View All Cached Breakdowns",
            "Export Breakdown Data",
            "Return to Main Menu"
        ]
        
        choice = print_menu(options)
        
        if choice == 1:
            get_revenue_breakdown(cache)
        elif choice == 2:
            view_all_breakdowns(cache)
        elif choice == 3:
            export_revenue_breakdown(cache)
        elif choice == 4:
            break
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

def get_revenue_breakdown(cache):
    """Get revenue breakdown data for a specific symbol."""
    symbol = input("\nEnter stock symbol (e.g., AAPL): ").strip().upper()
    
    if not symbol:
        print("No symbol entered.")
        return
    
    cached_data = cache.get_cached_data("revenue", symbol)
    
    if cached_data:
        print(f"\nFound cached revenue breakdown data for {symbol}.")
        refresh = input("Do you want to refresh from API? (y/N): ").strip().lower()
        if refresh != 'y':
            display_revenue_breakdown(cached_data, symbol)
            return
    
    if cache.check_api_limit_reached():
        print("\nWARNING: Daily API request limit (250) reached.")
        if cached_data:
            print("Using cached data instead.")
            display_revenue_breakdown(cached_data, symbol)
        else:
            print("No cached data available for this symbol.")
        return
    
    print(f"\nFetching revenue breakdown data for {symbol} from API...")
    endpoint = "/v4/revenue-breakdown"
    url = f"{cache.base_url}{endpoint}?symbol={symbol}&apikey={cache.api_key}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if not data or 'breakdown' not in data:
                print(f"No revenue breakdown data available for {symbol}.")
                return
            cache.track_api_request(endpoint)
            cache.save_data("revenue", symbol, data)
            display_revenue_breakdown(data, symbol)
        else:
            print(f"API request failed with status code {response.status_code}")
    except Exception as e:
        print(f"Error fetching revenue breakdown data: {str(e)}")

def display_revenue_breakdown(data, symbol):
    """Display revenue breakdown data in a readable format."""
    if not data or 'breakdown' not in data:
        print("No data to display.")
        return
    
    # Flatten the nested breakdown data
    breakdown = data.get('breakdown', {})
    flat_data = []
    for period, segments in breakdown.items():
        for segment, value in segments.items():
            flat_data.append({'period': period, 'segment': segment, 'value': value})
    
    df = pd.DataFrame(flat_data)
    if 'period' in df.columns:
        df = df.sort_values('period', ascending=False)
    
    display_cols = ['period', 'segment', 'value']
    display_cols = [col for col in display_cols if col in df.columns]
    
    if not display_cols:
        print("No relevant revenue breakdown data found.")
        return
    
    rename_map = {
        'period': 'Period',
        'segment': 'Segment',
        'value': 'Revenue'
    }
    
    display_df = df[display_cols].rename(columns={k: v for k, v in rename_map.items() if k in display_cols})
    print(f"\nRevenue Breakdown Data for {symbol}:")
    print(tabulate(display_df.head(10), headers="keys", tablefmt="pretty"))
    
    if len(df) > 10:
        print(f"\nShowing 10 of {len(df)} records. Export to view all data.")

def view_all_breakdowns(cache):
    """View a summary of all cached revenue breakdowns."""
    clear_screen()
    print_header("All Cached Revenue Breakdown Data")
    
    query = """
    SELECT symbol, MAX(last_updated) as last_updated, COUNT(*) as data_points
    FROM cache_data
    WHERE data_type = 'revenue'
    GROUP BY symbol
    """
    
    df = pd.read_sql_query(query, cache.db.conn)
    
    if df.empty:
        print("No revenue breakdown data cached yet.")
        return
    
    print(tabulate(df, headers="keys", tablefmt="pretty"))

def export_revenue_breakdown(cache):
    """Export revenue breakdown data to file."""
    from utils.export import export_data
    clear_screen()
    print_header("Export Revenue Breakdown Data")
    
    cache.db.execute("SELECT DISTINCT symbol FROM cache_data WHERE data_type = 'revenue'")
    results = cache.db.fetchall()
    symbols = [row[0] for row in results] if results else []
    
    if not symbols:
        print("No revenue breakdown data available to export.")
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
        cached_data = cache.get_cached_data("revenue", symbol)
        if cached_data:
            export_data(cached_data, f"{symbol}_revenue_breakdown", "Revenue Breakdown data")
