import requests
import pandas as pd
from tabulate import tabulate
from utils.display import print_header, clear_screen, print_menu

def handle(cache):
    """Handle Company Outlook data operations"""
    while True:
        clear_screen()
        print_header("Company Outlook Data")
        
        options = [
            "Get Company Outlook for a Symbol",
            "View All Cached Outlooks",
            "Export Outlook Data",
            "Return to Main Menu"
        ]
        
        choice = print_menu(options)
        
        if choice == 1:
            get_company_outlook(cache)
        elif choice == 2:
            view_all_outlooks(cache)
        elif choice == 3:
            export_company_outlook(cache)
        elif choice == 4:
            break
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

def get_company_outlook(cache):
    """Get company outlook data for a specific symbol."""
    symbol = input("\nEnter stock symbol (e.g., AAPL): ").strip().upper()
    
    if not symbol:
        print("No symbol entered.")
        return
    
    cached_data = cache.get_cached_data("outlook", symbol)
    
    if cached_data:
        print(f"\nFound cached outlook data for {symbol}.")
        refresh = input("Do you want to refresh from API? (y/N): ").strip().lower()
        if refresh != 'y':
            display_company_outlook(cached_data, symbol)
            return
    
    if cache.check_api_limit_reached():
        print("\nWARNING: Daily API request limit (250) reached.")
        if cached_data:
            print("Using cached data instead.")
            display_company_outlook(cached_data, symbol)
        else:
            print("No cached data available for this symbol.")
        return
    
    print(f"\nFetching company outlook data for {symbol} from API...")
    endpoint = "/v4/company-outlook"
    url = f"{cache.base_url}{endpoint}?symbol={symbol}&apikey={cache.api_key}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if not data:
                print(f"No outlook data available for {symbol}.")
                return
            cache.track_api_request(endpoint)
            cache.save_data("outlook", symbol, data)
            display_company_outlook(data, symbol)
        else:
            print(f"API request failed with status code {response.status_code}")
    except Exception as e:
        print(f"Error fetching outlook data: {str(e)}")

def display_company_outlook(data, symbol):
    """Display company outlook data in a readable format."""
    if not data or 'profile' not in data:
        print("No data to display.")
        return
    
    # Extract profile data (this endpoint returns nested data)
    profile = data.get('profile', {})
    df = pd.DataFrame([profile])
    
    display_cols = ['companyName', 'price', 'beta', 'volAvg', 'mktCap']
    display_cols = [col for col in display_cols if col in df.columns]
    
    if not display_cols:
        print("No relevant outlook data found.")
        return
    
    rename_map = {
        'companyName': 'Company',
        'price': 'Price',
        'beta': 'Beta',
        'volAvg': 'Avg Volume',
        'mktCap': 'Market Cap'
    }
    
    display_df = df[display_cols].rename(columns={k: v for k, v in rename_map.items() if k in display_cols})
    print(f"\nCompany Outlook Data for {symbol}:")
    print(tabulate(display_df, headers="keys", tablefmt="pretty", showindex=False))

def view_all_outlooks(cache):
    """View a summary of all cached outlooks."""
    clear_screen()
    print_header("All Cached Company Outlook Data")
    
    query = """
    SELECT symbol, MAX(last_updated) as last_updated, COUNT(*) as data_points
    FROM cache_data
    WHERE data_type = 'outlook'
    GROUP BY symbol
    """
    
    df = pd.read_sql_query(query, cache.db.conn)
    
    if df.empty:
        print("No outlook data cached yet.")
        return
    
    print(tabulate(df, headers="keys", tablefmt="pretty"))

def export_company_outlook(cache):
    """Export company outlook data to file."""
    from utils.export import export_data
    clear_screen()
    print_header("Export Company Outlook Data")
    
    cache.db.execute("SELECT DISTINCT symbol FROM cache_data WHERE data_type = 'outlook'")
    results = cache.db.fetchall()
    symbols = [row[0] for row in results] if results else []
    
    if not symbols:
        print("No outlook data available to export.")
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
        cached_data = cache.get_cached_data("outlook", symbol)
        if cached_data:
            export_data(cached_data, f"{symbol}_outlook", "Company Outlook data")
