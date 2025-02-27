"""
Export utilities - For exporting data to different formats
"""

import os
import pandas as pd
from datetime import datetime
from utils.config import get_config

def export_data(data, filename_base, data_description):
    """
    Export data to file
    
    Args:
        data: Data to export (list/dict that can be converted to DataFrame)
        filename_base (str): Base filename without extension
        data_description (str): Description of the data for user messages
    """
    config = get_config()
    export_format = config.get('export_format', 'xlsx').lower()
    export_dir = config.get('export_dir', 'exports')
    
    # Create export directory if it doesn't exist
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    
    # Convert data to DataFrame if it's not already
    if not isinstance(data, pd.DataFrame):
        df = pd.DataFrame(data)
    else:
        df = data
    
    # Add timestamp to filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_base}_{timestamp}"
    
    # Export based on format
    if export_format == 'csv':
        filepath = os.path.join(export_dir, f"{filename}.csv")
        df.to_csv(filepath, index=False)
    else:  # xlsx
        filepath = os.path.join(export_dir, f"{filename}.xlsx")
        df.to_excel(filepath, index=False)
    
    print(f"\n{data_description} exported successfully to {filepath}")
    
    return filepath
