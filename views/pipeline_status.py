"""
Pipeline Status Page — Pipeline health, logs, row counts, and run controls.
"""
import os
import glob
import json
import subprocess
import sys
import streamlit as st
import pandas as pd
from datetime import datetime

import config
from styles.theme import PLOTLY_COLORS


def count_csv_rows(directory):
    """Count total rows across all CSVs in a directory."""
    total = 0
    files = glob.glob(os.path.join(directory, "*.csv"))
    for f in files:
        try:
            df = pd.read_csv(f, low_memory=False)
            total += len(df)
        except Exception:
            pass
    return total, len(files)


def get_log_files():
    """Get list of log files sorted by modification time."""
    logs = glob.glob(os.path.join(config.LOGS_DIR, "*.log"))
    logs.sort(key=os.path.getmtime, reverse=True)
    return logs


def render():
    st.markdown("# ⚙️ Pipeline Status")
    st.markdown("Monitor data pipeline health, view logs, and trigger runs")

    # ── Pipeline Stages ────────────────────────────────────
    st.markdown("### Pipeline Stages")

    stages = [
        {
            "name": "🔍 Raw Scraping",
            "dir": config.RAW_DIR,
            "description": "Scraped product data from all stores",
        },
        {
            "name": "🧹 Cleaned Data",
            "dir": config.PROCESSED_DIR,
            "description": "Cleaned, normalized, and deduplicated",
        },
        {
            "name": "🔗 Matched Data",
            "dir": config.MATCHED_DIR,
            "description": "Cross-store entity resolution",
        },
    ]

    cols = st.columns(3)
    for i, stage in enumerate(stages):
        rows, files = count_csv_rows(stage["dir"])
        with cols[i]:
            status_color = "#00b894" if rows > 0 else "#e17055"
            st.markdown(
                f"<div style='padding:1.2rem;background:rgba(20,20,35,0.85);"
                f"border-radius:16px;border:1px solid rgba(255,255,255,0.08);"
                f"text-align:center;'>"
                f"<h4 style='color:{PLOTLY_COLORS[i]};margin:0;'>{stage['name']}</h4>"
                f"<p style='color:#9aa0a6;font-size:0.8rem;margin:0.3rem 0;'>"
                f"{stage['description']}</p>"
                f"<p style='color:#e8eaed;font-size:2rem;font-weight:800;margin:0.5rem 0;'>"
                f"{rows:,}</p>"
                f"<p style='color:#9aa0a6;font-size:0.75rem;margin:0;'>"
                f"{files} file(s)</p>"
                f"<div style='width:12px;height:12px;border-radius:50%;"
                f"background:{status_color};margin:0.5rem auto 0;'></div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # ── Run Pipeline ───────────────────────────────────────
    st.markdown("### 🚀 Run Pipeline")
    st.markdown("Execute pipeline stages in sequence")

    run_col1, run_col2 = st.columns(2)

    with run_col1:
        if st.button("▶️ Run All Scrapers", use_container_width=True):
            with st.spinner("Running scrapers... This may take several minutes."):
                try:
                    for scraper in ["alfatah_scraper", "metro_scraper", "naheed_scraper"]:
                        st.text(f"Running {scraper}...")
                        result = subprocess.run(
                            [sys.executable, "-m", f"scrapers.{scraper}"],
                            cwd=config.PROJECT_ROOT,
                            capture_output=True, text=True, timeout=600,
                        )
                        if result.returncode == 0:
                            st.success(f"✅ {scraper} completed")
                        else:
                            st.error(f"❌ {scraper} failed: {result.stderr[:500]}")
                except Exception as e:
                    st.error(f"Error: {e}")

        if st.button("▶️ Run Cleaning Pipeline", use_container_width=True):
            with st.spinner("Cleaning data..."):
                try:
                    result = subprocess.run(
                        [sys.executable, "-m", "pipeline.cleaner"],
                        cwd=config.PROJECT_ROOT,
                        capture_output=True, text=True, timeout=300,
                    )
                    if result.returncode == 0:
                        st.success("✅ Cleaning complete")
                    else:
                        st.error(f"❌ Cleaning failed: {result.stderr[:500]}")
                except Exception as e:
                    st.error(f"Error: {e}")

    with run_col2:
        if st.button("▶️ Run Entity Matching", use_container_width=True):
            with st.spinner("Matching products across stores..."):
                try:
                    result = subprocess.run(
                        [sys.executable, "-m", "pipeline.matcher"],
                        cwd=config.PROJECT_ROOT,
                        capture_output=True, text=True, timeout=600,
                    )
                    if result.returncode == 0:
                        st.success("✅ Matching complete")
                    else:
                        st.error(f"❌ Matching failed: {result.stderr[:500]}")
                except Exception as e:
                    st.error(f"Error: {e}")

        if st.button("▶️ Run Analysis", use_container_width=True):
            with st.spinner("Computing analytics..."):
                try:
                    result = subprocess.run(
                        [sys.executable, "-m", "pipeline.analyzer"],
                        cwd=config.PROJECT_ROOT,
                        capture_output=True, text=True, timeout=300,
                    )
                    if result.returncode == 0:
                        st.success("✅ Analysis complete")
                    else:
                        st.error(f"❌ Analysis failed: {result.stderr[:500]}")
                except Exception as e:
                    st.error(f"Error: {e}")

    st.markdown("---")

    # ── Validation Report ──────────────────────────────────
    val_path = os.path.join(config.PROCESSED_DIR, "validation_report.json")
    if os.path.exists(val_path):
        st.markdown("### 📋 Validation Report")
        with open(val_path) as f:
            val = json.load(f)

        overall = val.get("overall", "N/A")
        color = "#00b894" if overall == "PASS" else "#e17055"
        st.markdown(
            f"<h3 style='color:{color};'>Overall: {overall}</h3>",
            unsafe_allow_html=True,
        )

        with st.expander("View Full Report"):
            st.json(val)

    # ── Raw Data Files ─────────────────────────────────────
    st.markdown("### 📁 Data Files")
    tabs = st.tabs(["Raw", "Processed", "Matched"])

    for tab, (label, directory) in zip(tabs, [
        ("Raw", config.RAW_DIR),
        ("Processed", config.PROCESSED_DIR),
        ("Matched", config.MATCHED_DIR),
    ]):
        with tab:
            files = glob.glob(os.path.join(directory, "*.*"))
            if files:
                file_info = []
                for f in sorted(files, key=os.path.getmtime, reverse=True):
                    size_kb = os.path.getsize(f) / 1024
                    mtime = datetime.fromtimestamp(os.path.getmtime(f))
                    rows = 0
                    if f.endswith(".csv"):
                        try:
                            rows = len(pd.read_csv(f, low_memory=False))
                        except Exception:
                            pass
                    file_info.append({
                        "File": os.path.basename(f),
                        "Size": f"{size_kb:.1f} KB",
                        "Rows": f"{rows:,}" if rows > 0 else "-",
                        "Modified": mtime.strftime("%Y-%m-%d %H:%M"),
                    })
                st.dataframe(pd.DataFrame(file_info).astype(str), use_container_width=True, hide_index=True)
            else:
                st.info(f"No files in {directory}")

    # ── Logs ───────────────────────────────────────────────
    st.markdown("### 📝 Recent Logs")
    log_files = get_log_files()
    if log_files:
        selected_log = st.selectbox(
            "Select log file",
            [os.path.basename(f) for f in log_files],
        )
        if selected_log:
            log_path = os.path.join(config.LOGS_DIR, selected_log)
            with open(log_path, "r", encoding="utf-8") as f:
                log_content = f.read()
            # Show last 100 lines
            lines = log_content.strip().split("\n")
            st.code("\n".join(lines[-100:]), language="log")
    else:
        st.info("No log files found. Run a scraper to generate logs.")
