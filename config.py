"""
Global configuration for the supermarket price analysis pipeline.
"""
import os

# ── Project Root ───────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# ── Data Directories ──────────────────────────────────────────
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
MATCHED_DIR = os.path.join(DATA_DIR, "matched")
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")

# Create directories if they don't exist
for d in [RAW_DIR, PROCESSED_DIR, MATCHED_DIR, LOGS_DIR]:
    os.makedirs(d, exist_ok=True)

# ── Scraping Config ───────────────────────────────────────────
RATE_LIMIT_DELAY = 1.0          # seconds between requests
MAX_RETRIES = 5
RETRY_BACKOFF_FACTOR = 2.0      # exponential backoff multiplier
REQUEST_TIMEOUT = 30            # seconds

# ── Store Definitions ─────────────────────────────────────────
STORES = {
    "alfatah": {
        "name": "Al-Fatah",
        "base_url": "https://alfatah.pk",
        "api_url": "https://alfatah.pk/products.json",
        "cities": ["Lahore", "Karachi", "Sialkot"],
        "method": "shopify_json",
    },
    "metro": {
        "name": "Metro Online",
        "base_url": "https://www.metro-online.pk",
        "cities": ["Lahore", "Islamabad", "Karachi", "Faisalabad", "Hyderabad"],
        "method": "selenium",
    },
    "naheed": {
        "name": "Naheed.pk",
        "base_url": "https://naheed.pk",
        "cities": ["Karachi", "Lahore", "Islamabad", "Faisalabad", "Rawalpindi"],
        "method": "requests_bs4",
    },
    "imtiaz": {
        "name": "Imtiaz Super Market",
        "base_url": "https://imtiaz.com.pk",
        "cities": ["Karachi", "Lahore", "Islamabad", "Faisalabad", "Rawalpindi"],
        "method": "catalog_generator",
    },
}

# ── Categories to Scrape ──────────────────────────────────────
GROCERY_CATEGORIES = [
    "Dairy", "Beverages", "Snacks", "Breakfast", "Cooking Ingredients",
    "Personal Care", "Household", "Baby Care", "Frozen Food",
    "Oil & Ghee", "Rice & Flour", "Spices", "Tea & Coffee",
    "Biscuits", "Noodles & Pasta", "Canned Food", "Cleaning",
    "Fruits", "Vegetables", "Meat & Poultry", "Bakery",
]

# ── Matching Config ───────────────────────────────────────────
FUZZY_MATCH_THRESHOLD = 85      # token_sort_ratio minimum
MIN_MATCHED_PRODUCTS = 10000

# ── Validation Thresholds ─────────────────────────────────────
MAX_MISSING_PCT = 20.0          # max % missing values per column
PRICE_MIN = 1.0                 # PKR - minimum valid price
PRICE_MAX = 500000.0            # PKR - maximum valid price
OUTLIER_ZSCORE = 3.0            # Z-score threshold for outlier detection
