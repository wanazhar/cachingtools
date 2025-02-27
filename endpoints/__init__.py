"""
Endpoints package - Contains handlers for different financial data endpoints
"""

import os
import importlib

def get_available_endpoints():
    """
    Get a list of available endpoints based on the Python files in this directory.
    
    Returns:
        list: List of endpoint names (without .py extension)
    """
    # Get the directory of this file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # List Python files in this directory
    files = [f for f in os.listdir(current_dir) 
             if f.endswith('.py') and f != '__init__.py']
    
    # Remove .py extension
    endpoints = [os.path.splitext(f)[0] for f in files]
    
    return endpoints
