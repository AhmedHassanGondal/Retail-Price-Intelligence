"""
Master pipeline runner — runs all stages in sequence:
1. Scrape Metro (5 cities)
2. Scrape Naheed (5 cities)
3. Clean all data
4. Match across stores
5. Validate
6. Analyze

Usage: python run_pipeline.py
"""
import sys
import os
import time
import glob

# Make sure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd


def count_csv_rows(directory):
    total = 0
    for f in glob.glob(os.path.join(directory, "*.csv")):
        try:
            total += len(pd.read_csv(f))
        except Exception:
            pass
    return total


def main():
    import config

    print("=" * 60)
    print("SUPERMARKET PRICE ANALYSIS PIPELINE")
    print("=" * 60)

    t0 = time.time()

    # ── Stage 1: Metro Scraper ──────────────────────────────
    print("\n[1/6] Running Metro scraper...")
    from scrapers.metro_scraper import MetroScraper
    metro = MetroScraper()
    metro.run()
    metro_rows = count_csv_rows(config.RAW_DIR)
    print(f"  → Metro complete. Raw rows so far: {metro_rows:,}")

    # ── Stage 2: Naheed Scraper ─────────────────────────────
    print("\n[2/6] Running Naheed scraper...")
    from scrapers.naheed_scraper import NaheedScraper
    naheed = NaheedScraper()
    naheed.run()
    total_raw = count_csv_rows(config.RAW_DIR)
    print(f"  → Naheed complete. Total raw rows: {total_raw:,}")

    # ── Stage 3: Clean ──────────────────────────────────────
    print("\n[3/6] Running cleaning pipeline...")
    from pipeline.cleaner import run_cleaning
    run_cleaning()
    cleaned_rows = count_csv_rows(config.PROCESSED_DIR)
    print(f"  → Cleaning complete. Cleaned rows: {cleaned_rows:,}")

    # ── Stage 4: Match ──────────────────────────────────────
    print("\n[4/6] Running entity matching...")
    from pipeline.matcher import run_matching
    run_matching()
    matched_rows = count_csv_rows(config.MATCHED_DIR)
    print(f"  → Matching complete. Matched rows: {matched_rows:,}")

    # ── Stage 5: Validate ───────────────────────────────────
    print("\n[5/6] Running validation...")
    from pipeline.validator import run_validation
    run_validation()
    print("  → Validation complete.")

    # ── Stage 6: Analyze ────────────────────────────────────
    print("\n[6/6] Running analysis...")
    from pipeline.analyzer import run_analysis
    run_analysis()
    print("  → Analysis complete.")

    # ── Summary ─────────────────────────────────────────────
    elapsed = time.time() - t0
    final_raw = count_csv_rows(config.RAW_DIR)
    final_clean = count_csv_rows(config.PROCESSED_DIR)
    final_matched = count_csv_rows(config.MATCHED_DIR)

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print(f"  Total time: {elapsed:.1f}s")
    print(f"  Raw rows: {final_raw:,}")
    print(f"  Cleaned rows: {final_clean:,}")
    print(f"  Matched rows: {final_matched:,}")
    print("=" * 60)


if __name__ == "__main__":
    main()
