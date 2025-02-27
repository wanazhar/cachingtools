"""
Cache Manager - Core functionality for the Financial Data Cache system
"""

import pandas as pd
from datetime import datetime
from core.database import Database

class CacheManager:
    def __init__(self, api_key, database_path=None):
        """
        Initialize the cache manager
        
        Args:
            api_key (str): Financial Modeling Prep API key
            database_path (str, optional): Path to the SQLite database
        """
        from utils.config import get_config
        
        config = get_config()
        self.api_key = api_key
        self.base_url = "https://financialmodelingprep.com/api"
        
        # Use provided database path or get from config
        if database_path:
            self.database_path = database_path
        else:
            self.database_path = config.get('database_path', 'financial_data.db')
        
        # Initialize database
        self.db = Database(self.database_path)
    
    def track_api_request(self, endpoint):
        """
        Track an API request to monitor daily usage
        
        Args:
            endpoint (str): API endpoint being accessed
        """
        today = datetime.now().strftime("%Y-%m-%d")
        self.db.execute(
            "SELECT count FROM api_requests WHERE endpoint=? AND date=?", 
            (endpoint, today)
        )
        result = self.db.fetchone()
        
        if result:
            count = result[0] + 1
            self.db.execute(
                "UPDATE api_requests SET count=? WHERE endpoint=? AND date=?", 
                (count, endpoint, today)
            )
        else:
            self.db.execute(
                "INSERT INTO api_requests (endpoint, date, count) VALUES (?, ?, ?)", 
                (endpoint, today, 1)
            )
        
        self.db.commit()
    
    def get_daily_request_count(self):
        """Get the count of API requests made today."""
        today = datetime.now().strftime("%Y-%m-%d")
        self.db.execute(
            "SELECT SUM(count) FROM api_requests WHERE date=?", 
            (today,)
        )
        result = self.db.fetchone()
        
        return result[0] if result and result[0] else 0
    
    def check_api_limit_reached(self):
        """Check if the daily API limit has been reached."""
        daily_count = self.get_daily_request_count()
        return daily_count >= 250
    
    def get_cache_summary(self):
        """Get a summary of all cached data."""
        query = """
        SELECT 
            data_type, 
            symbol, 
            MAX(last_updated) as last_updated,
            COUNT(*) as data_points
        FROM cache_data
        GROUP BY data_type, symbol
        """
        
        return pd.read_sql_query(query, self.db.conn)
    
    def get_cached_data(self, data_type, symbol):
        """
        Get cached data for a specific type and symbol
        
        Args:
            data_type (str): Type of data (e.g., 'esg', 'profile')
            symbol (str): Stock symbol
            
        Returns:
            dict: Cached data or None if not found
        """
        self.db.execute(
            "SELECT raw_data FROM cache_data WHERE data_type=? AND symbol=? ORDER BY last_updated DESC LIMIT 1", 
            (data_type, symbol)
        )
        result = self.db.fetchone()
        
        if result and result[0]:
            import json
            return json.loads(result[0])
        return None
    
    def save_data(self, data_type, symbol, data):
        """
        Save data to the cache
        
        Args:
            data_type (str): Type of data (e.g., 'esg', 'profile')
            symbol (str): Stock symbol
            data (dict): Data to save
        """
        import json
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.db.execute(
            "INSERT INTO cache_data (data_type, symbol, last_updated, raw_data) VALUES (?, ?, ?, ?)",
            (data_type, symbol, now, json.dumps(data))
        )
        self.db.commit()
