import os
import json
import time
import random
from pathlib import Path

import requests
import pandas as pd
from dotenv import load_dotenv

# ----------------------------
# Config
# ----------------------------
load_dotenv()
API_KEY = os.getenv("MARKETCHECK_API_KEY")
if not API_KEY:
    raise RuntimeError("API key not found. Put it in .env as MARKETCHECK_API_KEY=...")

API_URL = "https://api.marketcheck.com/v2/search/car/active"

BRANDS = ["Toyota", "Honda", "Ford", "Chevrolet"]

LAT, LON = 42.3314, -83.0458   # Detroit center
RADIUS = 100

ROWS = 50                      # confirmed working
TARGET_PER_BRAND = 500         # safe default;

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

BASE_SLEEP = 0.35              # normal pause between calls
JITTER = (0.00, 0.20)          # add a tiny random delay


def polite_sleep():
    time.sleep(BASE_SLEEP + random.uniform(*JITTER))


def fetch_page(make: str, start: int, max_retries: int = 6) -> dict:
    """Fetch one page safely with retries/backoff on 429/503."""
    params = {
        "api_key": API_KEY,
        "rows": ROWS,
        "start": start,
        "car_type": "used",
        "make": make,
        "latitude": LAT,
        "longitude": LON,
        "radius": RADIUS,
    }

    for attempt in range(max_retries):
        r = requests.get(API_URL, params=params, timeout=20)

        if r.status_code == 200:
            return r.json()

        if r.status_code in (429, 503):
            wait = min(2 ** attempt, 30) + random.uniform(0, 1)
            print(f"[{make} start={start}] {r.status_code} throttled. Waiting {wait:.1f}s then retrying...")
            time.sleep(wait)
            continue

        raise RuntimeError(f"{make} start={start} failed: {r.status_code} {r.text[:300]}")

    raise RuntimeError(f"Failed after {max_retries} retries for {make} start={start}.")


def flatten_listings(listings: list) -> pd.DataFrame:
    """Flatten nested JSON to a table with the columns we care about."""
    if not listings:
        return pd.DataFrame()

    df = pd.json_normalize(listings, sep=".")

    keep = [
        "id", "vin", "heading", "price", "miles", "msrp",
        "dom", "seller_type", "inventory_type",
        "first_seen_at_date", "last_seen_at_date",
        "dealer.city", "dealer.state", "dealer.zip",
        "build.year", "build.make", "build.model", "build.trim",
        "build.body_type", "build.vehicle_type",
        "build.transmission", "build.drivetrain",
        "build.fuel_type", "build.engine", "build.cylinders",
        "dist"
    ]
    keep_existing = [c for c in keep if c in df.columns]
    return df[keep_existing].copy()


def main():
    all_frames = []

    for make in BRANDS:
        print(f"\n=== Pulling {make} (up to {TARGET_PER_BRAND}) ===")

        pulled = 0
        start = 0

        while pulled < TARGET_PER_BRAND:
            out_path = RAW_DIR / f"{make.lower()}_start{start}.json"

            # Use cache if present (saves calls)
            if out_path.exists():
                data = json.loads(out_path.read_text(encoding="utf-8"))
            else:
                data = fetch_page(make, start)
                out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
                polite_sleep()

            listings = data.get("listings", [])
            if not listings:
                print(f"{make}: no more listings at start={start}.")
                break

            df_page = flatten_listings(listings)
            all_frames.append(df_page)

            pulled += len(listings)
            print(f"{make}: start={start} | got={len(listings)} | pulled_total≈{pulled}")

            start += ROWS

            # Extra safety stop
            if start > 50000:
                print("Safety stop triggered.")
                break

    df_all = pd.concat(all_frames, ignore_index=True)

    # Basic cleaning
    df_all["price"] = pd.to_numeric(df_all.get("price"), errors="coerce")
    df_all["miles"] = pd.to_numeric(df_all.get("miles"), errors="coerce")
    df_all["build.year"] = pd.to_numeric(df_all.get("build.year"), errors="coerce")

    CURRENT_YEAR = 2026
    df_all["age"] = CURRENT_YEAR - df_all["build.year"]

    df_all = df_all.dropna(subset=["price", "miles", "build.year"])
    df_all = df_all[(df_all["price"] > 0) & (df_all["miles"] >= 0) & (df_all["build.year"] >= 1990)]
    df_all = df_all.drop_duplicates(subset=["id"])

    out_csv = PROCESSED_DIR / "used_cars_detroit_clean.csv"
    df_all.to_csv(out_csv, index=False)

    print(f"\nSaved cleaned CSV: {out_csv}")
    print("Rows:", len(df_all))
    print("Columns:", len(df_all.columns))


if __name__ == "__main__":
    main()