# PhonePe Pulse — Data Analytics Project

End-to-end analysis of India's digital payments data (2018–2024) from PhonePe's public [Pulse](https://github.com/PhonePe/pulse) dataset — from raw JSON to a cleaned SQLite database, SQL analysis, and a Power BI dashboard.

## 📊 Live Dashboard

![Dashboard walkthrough](assets/dashboard_demo.gif)

Full PDF export: [`assets/dashboard.pdf`](assets/dashboard.pdf) · Editable file: [`PhonePe_Dashboard.pbix`](PhonePe_Dashboard.pbix) . Interactive Power BI Dashboard: [`Public Link`](https://app.powerbi.com/view?r=eyJrIjoiNzM4MGY0YjAtZDU0ZC00MTY5LTk2NzctMjg2ZDA3YTFkMTg5IiwidCI6IjZiOGI4Mjk2LWJkZmYtNGFkOC05M2FkLTg0YmNiZjM4NDJmNSJ9&pageName=e8aff176764522842827)

## 🏗️ Architecture

```
PhonePe/pulse (raw JSON, 9 dataset types)
        │
        ▼
extract_pipeline.py  (Python, pandas)
   • walks state/year/quarter folders
   • parses & flattens JSON
   • drops duplicates, skips corrupt files safely
        │
        ▼
SQLite (processed/phonepe.db)  +  9 clean CSVs
        │
        ├──► sql_queries.sql   (window functions, CTEs, joins)
        └──► Power BI          (star schema, DAX measures, 4-page dashboard)
```

## 🔑 Key Insights

*(All figures computed directly from the 116,403 records processed — see `full_insights.py`)*

- **Market concentration**: the top 5 states (Telangana, Karnataka, Maharashtra, Andhra Pradesh, Uttar Pradesh) account for **53.3%** of total transaction value.
- **Growth is decelerating, not slowing down**: national transaction value grew from ~₹1.6L crore (2018) to ~₹129.6L crore (2024). YoY growth fell from **287% (2019) to 37% (2024)** — a maturing market, not a shrinking one.
- **Device concentration**: Xiaomi, Samsung, and Vivo together account for **62.6%** of registered users by device brand.
- **Engagement is high and growing**: by 2024, users averaged **65.6 app opens per registered user**.
- **Insurance is the biggest untapped opportunity**: insurance transaction value grew 30–410% YoY between 2020–2024, but penetration relative to payment volume remains under **0.4%** in the very states that drive the most transactions — Andhra Pradesh, Telangana, and Odisha. Kerala and smaller UTs show 10x higher penetration, suggesting the growth strategy should target high-transaction, low-insurance states first.
- **Urban concentration at the district level**: Bengaluru Urban alone accounts for ~₹19.9L crore in transactions — more than double the next-highest district.

## 🛠️ Tech Stack

Python (pandas) · SQLite · SQL (window functions, CTEs, joins) · Power BI (DAX, Power Query)

## 📂 Repository Structure

```
phonepe-dashboard-v2/
├── extract_pipeline.py       # ETL: JSON → SQLite + CSV
├── schema.sql                # table definitions
├── sql_queries.sql           # 10 analytical queries
├── full_insights.py          # generates the insights above
├── requirements.txt
├── PhonePe_Dashboard.pbix    # Power BI file
├── assets/
│   ├── dashboard.pdf
│   └── dashboard_demo.gif
└── processed/                # generated CSVs + phonepe.db (gitignored if large)
```

## ▶️ How to Run

```bash
git clone https://github.com/<your-username>/phonepe-dashboard-v2.git
cd phonepe-dashboard-v2
git clone https://github.com/PhonePe/pulse.git

python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

python extract_pipeline.py --pulse-dir pulse/data --out-dir processed
python full_insights.py
sqlite3 processed/phonepe.db < sql_queries.sql
```

Open `PhonePe_Dashboard.pbix` in Power BI Desktop and refresh the data source to point at your local `processed/` folder.

## 📌 What I Learned

- Building a reusable ETL pattern instead of duplicating extraction logic per dataset
- Designing a normalized schema and star-schema Power BI model instead of one flat table
- Writing SQL with window functions, CTEs, and HAVING clauses to answer real business questions
- Handling security properly (SQLite over hardcoded DB credentials) for a public repo

## 👨‍💻 Author

Sriguhan K — [LinkedIn](https://www.linkedin.com/in/sri-guhan-1ba29126a) · [GitHub](https://github.com/sriguhan02-svg) . [Email](sriguhan02@gmail.com)
