import requests
import pandas as pd
from tabulate import tabulate
from utils.display import print_header, clear_screen, print_menu

def handle(cache):
    """Handle Economic Indicators data operations"""
    while True:
        clear_screen()
        print_header("Economic Indicators Data")
        
        options = [
            "Get Economic Indicator Data",
            "View All Cached Indicators",
            "Export Indicator Data",
            "Return to Main Menu"
        ]
        
        choice = print_menu(options)
        
        if choice == 1:
            get_economic_indicators(cache)
        elif choice == 2:
            view_all_indicators(cache)
        elif choice == 3:
            export_economic_indicators(cache)
        elif choice == 4:
            break
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

def get_economic_indicators(cache):
    """Get economic indicators data."""
    print("\nAvailable indicators: GDP, CPI, unemploymentRate")
    indicator = input("Enter economic indicator: ").strip().lower()
    
    if not indicator:
        print("No indicator entered.")
        return
    
    cached_data = cache.get_cached_data("economic", indicator)
    
    if cached_data:
        print(f"\nFound cached data for {indicator}.")
        refresh = input("Do you want to refresh from API? (y/N): ").strip().lower()
        if refresh != 'y':
            display_economic_indicators(cached_data, indicator)
            return
    
    if cache.check_api_limit_reached():
        print("\nWARNING: Daily API request limit (250) reached.")
        if cached_data:
            print("Using cached data instead.")
            display_economic_indicators(cached_data, indicator)
        else:
            print("No cached data available for this indicator.")
        return
    
    print(f"\nFetching economic indicator data for {indicator} from API...")
    endpoint = "/v3/economic"
    url = f"{cache.base_url}{endpoint}?name={indicator}&apikey={cache.api_key}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if not data:
                print(f"No data available for {indicator}.")
                return
            cache.track_api_request(endpoint)
            cache.save_data("economic", indicator, data)
            display_economic_indicators(data, indicator)
        else:
            print(f"API request failed with status code {response.status_code}")
    except Exception as e:
        print(f"Error fetching economic indicator data: {str(e)}")

def display_economic_indicators(data, indicator):
    """Display economic indicators data in a readable format."""
    if not data:
        print("No data to display.")
        return
    
    df = pd.DataFrame(data)
    if 'date' in df.columns:
        df = df.sort_values('date', ascending=False)
    
    display_cols = ['date', 'value']
    display_cols = [col for col in display_cols if col in df.columns]
    
    if not display_cols:
        print("No relevant indicator data found.")
        return
    
    rename_map = {
        'date': 'Date',
        'value': 'Value'
    }
    
    display_df = df[display_cols].rename(columns={k: v for k, v in rename_map.items() if k in display_cols})
    print(f"\nEconomic Indicator Data for {indicator}:")
    print(tabulate(display_df.head(10), headers="keys", tablefmt="pretty"))
    
    if len(df) > 10:
        print(f"\nShowing 10 of {len(df)} records. Export to view all data.")

def view_all_indicators(cache):
    """View a summary of all cached indicators."""
    clear_screen()
    print_header("All Cached Economic Indicators Data")
    
    query = """
    SELECT symbol as indicator, MAX(last_updated) as last_updated, COUNT(*) as data_points
    FROM cache_data
    WHERE data_type = 'economic'
    GROUP BY symbol
    """
    
    df = pd.read_sql_query(query, cache.db.conn)
    
    if df.empty:
        print("No economic indicator data cached yet.")
        return
    
    print(tabulate(df, headers="keys", tablefmt="pretty"))

def export_economic_indicators(cache):
    """Export economic indicators data to file."""
    from utils.export import export_data
    clear_screen()
    print_header("Export Economic Indicators Data")
    
    cache.db.execute("SELECT DISTINCT symbol FROM cache_data WHERE data_type = 'economic'")
    results = cache.db.fetchall()
    indicators = [row[0] for row in results] if results else []
    
    if not indicators:
        print("No indicator data available to export.")
        return
    
    print("Available indicators:")
    for i, indicator in enumerate(indicators, 1):
        print(f"{i}. {indicator}")
    print(f"{len(indicators) + 1}. All Indicators")
    print(f"{len(indicators) + 2}. Cancel")
    
    choice = int(input(f"\nEnter choice (1-{len(indicators) + 2}): "))
    
    if choice == len(indicators) + 2:
        return
    
    indicators_to_export = indicators if choice == len(indicators) + 1 else [indicators[choice - 1]] if 1 <= choice <= len(indicators) else []
    
    if not indicators_to_export:
        print("Invalid choice.")
        return
    
    for indicator in indicators_to_export:
        cached_data = cache.get_cached_data("economic", indicator)
        if cached_data:
            export_data(cached_data, f"{indicator}_economic", "Economic Indicator data")
