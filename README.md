# 🛒 Retail Price Intelligence

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Pandas-%23150458?style=for-the-badge&logo=pandas&logoColor=white"/>
  <img src="https://img.shields.io/badge/Scrapy%2FRequests-Web%20Scraping-green?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge"/>
</p>

> **End-to-end retail price monitoring pipeline** — scrape product prices across retailers, process & compare them through a structured data pipeline, and visualise competitive intelligence on an interactive dashboard.

---

## ✨ What It Does

- **Scrapes** product listings and prices from multiple retail sources
- **Processes** raw data through a cleaning and normalisation pipeline
- **Identifies** price gaps and competitive positioning across retailers
- **Visualises** insights on an interactive dashboard for quick decision-making

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────────┐
│                  Retail Price Intelligence                  │
│                                                            │
│  ┌──────────┐   ┌──────────────┐   ┌──────────────────┐  │
│  │ Scrapers │──▶│   Pipeline   │──▶│   Data Store     │  │
│  │ (multi-  │   │  clean, norm │   │   data/          │  │
│  │  source) │   │  merge, enr. │   │                  │  │
│  └──────────┘   └──────────────┘   └────────┬─────────┘  │
│                                             │              │
│                    ┌────────────────────────▼──────────┐  │
│                    │       Dashboard  (app.py)          │  │
│                    │  views/ + styles/ → Streamlit UI  │  │
│                    └───────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
Retail-Price-Intelligence/
├── scrapers/           ← Source-specific scrapers
├── pipeline/           ← Data cleaning, normalisation & enrichment
├── data/               ← Raw & processed price datasets
├── views/              ← Dashboard page components
├── styles/             ← UI theme & CSS
├── app.py              ← Main dashboard entry point
├── run_pipeline.py     ← Run the full scraping + processing pipeline
├── config.py           ← Global settings (sources, intervals, paths)
└── requirements.txt    ← Python dependencies
```

---

## 🚀 Quick Start

### 1 — Clone & install

```bash
git clone https://github.com/AhmedHassanGondal/Retail-Price-Intelligence.git
cd Retail-Price-Intelligence
pip install -r requirements.txt
```

### 2 — Run the pipeline

```bash
python run_pipeline.py
```

This scrapes product data, cleans it, and saves processed files to `data/`.

### 3 — Launch the dashboard

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Scraping | Python Requests / BeautifulSoup |
| Data Processing | Pandas, NumPy |
| Dashboard | Streamlit |
| Configuration | Python config module |

---

## 💡 Key Features

- **Multi-source scraping** — collects prices from multiple retail targets via modular scrapers
- **Structured pipeline** — raw → normalised → enriched in clearly separated stages
- **Price comparison views** — side-by-side retailer comparison with delta highlighting
- **Configurable** — swap sources, adjust scrape intervals, and change columns in one place (`config.py`)

---

## 📬 Author

**Ahmed Hassan Gondal** — Aspiring Data Scientist | ML Engineer

[![LinkedIn](https://img.shields.io/badge/LinkedIn-%230077B5?style=flat-square&logo=linkedin&logoColor=white)](https://linkedin.com/in/ahmed-hassan-gondal)
[![GitHub](https://img.shields.io/badge/GitHub-%23181717?style=flat-square&logo=github&logoColor=white)](https://github.com/AhmedHassanGondal)
