# 🚀 CachingTools - Financial Data Cache System

<div align="center">
  
```
   ______           __    _            ______            __    
  / ____/___ ______/ /_  (_)___  ____ /_  __/___  ____  / /____
 / /   / __ `/ ___/ __ \/ / __ \/ __ `// / / __ \/ __ \/ / ___/
/ /___/ /_/ / /__/ / / / / / / / /_/ // / / /_/ / /_/ / (__  ) 
\____/\__,_/\___/_/ /_/_/_/ /_/\__, //_/  \____/\____/_/____/  
                              /____/                           
```

**another vibecode / work in progress**

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)

</div>

## 📋 Overview

CachingTools is a terminal-based application that helps you efficiently work with financial data APIs by intelligently caching responses to minimize API usage. Perfect for users on free-tier API plans with request limitations.

### 🌟 Key Features

- **Smart Caching**: Stores API responses locally to minimize repeated requests
- **Terminal UI**: Easy-to-use text-based interface with menus
- **API Limit Protection**: Tracks daily usage to avoid exceeding your free tier limits
- **Data Export**: Export data to Excel or CSV formats
- **Modular Design**: Easily extensible to add more endpoints

## 🔍 Perfect For

- Users with free-tier Financial Modeling Prep API access (limited to 250 daily requests)
- Financial analysts working with market data
- Developers building finance-related applications
- Students learning financial data analysis

## 🛠️ Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- Financial Modeling Prep API key ([Get one here](https://financialmodelingprep.com/developer/docs/))

### Step-by-Step Setup for Beginners

1. **Clone the repository or download the files:**

```bash
git clone https://github.com/wanazhar/cachingtools.git
cd cachingtools
```

2. **Create a virtual environment (recommended but optional):**

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install required packages:**

```bash
pip install -r requirements.txt
```

4. **Configure your API key:**
   - Create a file named `.env` in the root directory
   - Add your API key like this:
   ```
   FMP_API_KEY=your_api_key_here
   ```

5. **Run the application:**

```bash
python main.py
```

## 🚀 Getting Started Guide

### First Launch

When you first run the application, you'll see the main menu. Since no data has been cached yet, let's retrieve some data:

1. Select the **ESG** option from the menu
2. Choose **Get ESG Data for a Symbol**
3. Enter a stock symbol (e.g., `AAPL` for Apple)
4. The system will fetch the data from the API and store it locally
5. View the data in a nicely formatted table

### Subsequent Use

The next time you request the same data:

1. The system will check the local cache first
2. It will display the cached data without making another API request
3. You can choose to refresh the data if needed

### Exporting Data

To export data to a file:

1. Select the **ESG** option from the menu
2. Choose **Export ESG Data**
3. Select which symbol(s) to export
4. The data will be exported to the configured format (Excel or CSV)

## 📁 Project Structure

```
financial_cache/
│
├── .env                  # Environment variables (API keys)
├── main.py               # Main entry point with CLI interface
├── requirements.txt      # Dependencies
│
├── core/
│   ├── __init__.py
│   ├── cache_manager.py  # Base caching functionality
│   └── database.py       # Database connection and setup
│
├── endpoints/
│   ├── __init__.py
│   ├── esg.py            # ESG data endpoint
│   └── [other endpoints] # Future endpoints
│
└── utils/
    ├── __init__.py
    ├── display.py        # Terminal display helpers
    ├── export.py         # Export functionality
    └── config.py         # Configuration handling
```

## 📊 Available Endpoints

Currently, the system supports:

- **ESG Data**: Environmental, Social, and Governance scores for companies

## 🧩 Adding New Endpoints

To add a new endpoint:

1. Create a new Python file in the `endpoints` directory (e.g., `financial.py`)
2. Follow the pattern in `esg.py` to implement your endpoint handler
3. The system will automatically detect and add it to the menu

Example structure for a new endpoint:

```python
def handle(cache):
    # Your endpoint code here
    pass
    
def get_endpoint_data(cache):
    # Data retrieval logic
    pass
    
def display_endpoint_data(data, symbol):
    # Display logic
    pass
```

## ⚙️ Configuration

You can configure the application through the **Settings** menu:

- **Database Path**: Where cached data is stored
- **Export Format**: Choose between Excel (xlsx) or CSV
- **Export Directory**: Where exported files are saved

## 🔄 Command Line Arguments

Run with the `--summary` flag to quickly view your cache summary:

```bash
python main.py --summary
```

## 📝 API Usage Tracking

The application tracks your daily API usage to help you stay within the 250 request limit. The current count is shown in the Cache Summary screen.

## 🤝 Contributing

Contributions are welcome! Feel free to:

- Add new endpoints
- Improve the UI
- Enhance documentation
- Fix bugs

## 📜 License

This project is released under the MIT License.

## 📧 Contact

If you have any questions or feedback, please open an issue on GitHub or contact the developer.

---

<div align="center">
  <p>Happy financial data analysis! 📈</p>
</div>
