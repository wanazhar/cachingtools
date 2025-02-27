"""
Database - Database connection and setup for Financial Data Cache
"""

import sqlite3
import os

class Database:
    def __init__(self, database_path):
        """
        Initialize the database connection
        
        Args:
            database_path (str): Path to the SQLite database file
        """
        # Create directory if it doesn't exist
        db_dir = os.path.dirname(database_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            
        self.conn = sqlite3.connect(database_path)
        self.cursor = self.conn.cursor()
        self.setup_tables()
    
    def setup_tables(self):
        """Create required database tables if they don't exist."""
        # API request tracking table
        self.execute('''
        CREATE TABLE IF NOT EXISTS api_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            endpoint TEXT,
            date TEXT,
            count INTEGER
        )
        ''')
        
        # Generic cache table for all data types
        self.execute('''
        CREATE TABLE IF NOT EXISTS cache_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_type TEXT,
            symbol TEXT,
            date TEXT,
            last_updated TEXT,
            raw_data TEXT,
            UNIQUE(data_type, symbol, date)
        )
        ''')
        
        self.commit()
    
    def execute(self, query, params=()):
        """Execute a SQL query with parameters."""
        return self.cursor.execute(query, params)
    
    def fetchone(self):
        """Fetch one result from the last query."""
        return self.cursor.fetchone()
    
    def fetchall(self):
        """Fetch all results from the last query."""
        return self.cursor.fetchall()
    
    def commit(self):
        """Commit changes to the database."""
        self.conn.commit()
    
    def close(self):
        """Close the database connection."""
        self.conn.close()
