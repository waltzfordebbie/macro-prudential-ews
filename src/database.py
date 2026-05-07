import os
import sqlite3

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(root, "data", "fred_data.db")


def init_db():
    conn = None
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS observations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    value REAL NOT NULL,
                    date TEXT NOT NULL,
                    UNIQUE(name, date)
                )   
            """)
            print(f"✅ Database initialized at: {DB_PATH}")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")


def save_data(all_results):
    rows_to_insert = []
    for json_response in all_results:
        observations_list = json_response.get("observations", [])
        if not observations_list:
            print(
                f"⚠️ No observations found for {json_response.get('indicator_name', 'unknown')}"
            )
            continue
        indicator_name = json_response.get("indicator_name", "unknown")

        for obs in observations_list:
            row = (
                indicator_name,
                obs.get("value", None),
                obs.get("date", "0000-00-00"),
            )
            rows_to_insert.append(row)

    if rows_to_insert:
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.executemany(
                    """
                    INSERT OR IGNORE INTO observations (name, value, date) VALUES (?, ?, ?)
                """,
                    rows_to_insert,
                )
                print(
                    f"✅ Data saved to database: {len(rows_to_insert)} rows inserted."
                )
        except Exception as e:
            print(f"❌ Error saving data to database: {e}")


if __name__ == "__main__":
    init_db()
