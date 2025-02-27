"""
Display utilities for terminal interface
"""

import os
import sys

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    """Print a formatted header."""
    terminal_width = get_terminal_width()
    print("=" * terminal_width)
    print(title.center(terminal_width))
    print("=" * terminal_width)
    print("")

def print_menu(options):
    """
    Print a menu and get user selection
    
    Args:
        options (list): List of menu options
        
    Returns:
        int: User's selection (1-based index)
    """
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
        
    while True:
        try:
            choice = input(f"\nEnter choice (1-{len(options)}): ")
            choice = int(choice)
            if 1 <= choice <= len(options):
                return choice
            else:
                print(f"Please enter a number between 1 and {len(options)}.")
        except ValueError:
            print("Please enter a valid number.")

def get_terminal_width():
    """Get terminal width, with fallback if it can't be determined."""
    try:
        return os.get_terminal_size().columns
    except (AttributeError, OSError):
        return 80  # Default width
