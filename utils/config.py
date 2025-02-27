"""
Configuration utilities - For handling user configurations
"""

import os
import json

CONFIG_FILE = 'config.json'

def get_config():
    """
    Get configuration from file or create default
    
    Returns:
        dict: Configuration settings
    """
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return create_default_config()
    else:
        return create_default_config()

def create_default_config():
    """
    Create default configuration
    
    Returns:
        dict: Default configuration
    """
    config = {
        'database_path': 'financial_data.db',
        'export_format': 'xlsx',
        'export_dir': 'exports'
    }
    
    save_config(config)
    return config

def save_config(config):
    """
    Save configuration to file
    
    Args:
        config (dict): Configuration to save
    """
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)
