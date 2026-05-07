import os
import requests
import time
import sqlite3
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
API_KEY = os.getenv("FRED_API_KEY")
indicators = (
    "WALCL",
    "SOFR",
    "RRPONTSYD",
    "STLFSI4",
    "T10Y3M",
    "QUSPAM770A",
    "CSUSHPINSA",
    "TDSP",
)
all_results = []

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(root, "data", "fred_data.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def get_smart_limit(db_path=DB_PATH):
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='observations'"
            )
            table_exists = cursor.fetchone()
            last_date_results = (None,)
            if table_exists:
                cursor.execute("SELECT MAX(date) FROM observations")
                last_date_results = cursor.fetchone()
            if last_date_results is None or last_date_results[0] is None:
                print("📊 No existing data found. Fetching full dataset.")
                return 500
            last_date = datetime.strptime(last_date_results[0], "%Y-%m-%d")
            days_since_update = (datetime.now() - last_date).days
            if days_since_update > 30:
                print(
                    f"📊 Data is outdated (last update: {last_date.date()}). Fetching full dataset."
                )
                return 500
            else:
                print(
                    f"📊 Data is up-to-date (last update: {last_date.date()}). Fetching latest updates only."
                )
                return 5
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return 500


def fetch_indicators():
    for indicator in indicators:
        print(f"Fetching data for {indicator}...")
        URL = "https://api.stlouisfed.org/fred/series/observations"
        PARAMS = {
            "api_key": API_KEY,
            "file_type": "json",
            "series_id": indicator,
            "limit": get_smart_limit(),
        }
        max_retries = 3
        retry_delay = 2
        for attempt in range(max_retries):
            response = requests.get(URL, params=PARAMS)

            if response.status_code == 200:
                break
            elif response.status_code == 500:
                print(
                    f"⚠️ Server error (500) for {indicator}. Attempt {attempt + 1} of {max_retries}. Retrying in {retry_delay} seconds..."
                )
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print(
                    f"❌ Failed to fetch data for {indicator}. Status code: {response.status_code}. Response: {response.text}"
                )
                break
        data = response.json()
        data["indicator_name"] = indicator
        all_results.append(data)
        print(
            f"✅ Data fetched for {indicator}. Observations count: {len(data['observations'])}"
        )
        time.sleep(1.5)  # Sleep to respect API rate limits
    return all_results


if __name__ == "__main__":
    if not API_KEY:
        print(
            "❌ FRED_API_KEY not found in environment variables. Please set it in the .env file."
        )
    else:
        fetch_indicators()
