# 🎬 Netflix Content Analysis Report (Streamlit)

Interactive, cleaned data-analysis dashboard for `netflix_titles.csv` with a bold **Red & Black** theme.

## Project structure
```
netflix_dashboard/
├── app.py                 # Streamlit dashboard (7 tabs)
├── data_processing.py     # Cleaning + feature engineering
├── styles.py              # Custom CSS (red & black theme)
├── clean_data.py          # CLI: writes data/netflix_cleaned.csv
├── requirements.txt
├── run.bat / run.sh       # One-click launchers
├── .streamlit/config.toml # Dark theme config
└── data/
    ├── netflix_titles.csv   # raw
    └── netflix_cleaned.csv  # cleaned output
```

## Run
```bash
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
streamlit run app.py
```
Opens at http://localhost:8501. Or just double-click `run.bat` (Windows) / run `./run.sh`.

**Roman Urdu:** Zip extract karein → terminal folder mein kholein → upar wali commands chalayein (ya `run.bat` double-click karein) → browser mein `localhost:8501` khul jayega.

## Dashboard tabs
Overview · Trends · Content · Geography · People · Explorer · Data Quality

Sidebar filters: type, release year, audience group, country, genre (+ optional upload of your own CSV).

## Cleaning steps
1. Trim whitespace, blank → missing  2. Drop duplicates  3. Fix 3 rows where runtime sat in `rating`
4. Fill missing director/cast/country → `Unknown`; missing/`UR` rating → `NR`
5. Parse `date_added` → `year_added`, `month_added`, `release_lag`
6. Split `duration` → `movie_minutes`, `tv_seasons`
7. Add `rating_group`, `primary_country`, `decade`; multi-value fields split into lists for correct counts
"# netflix-data-analysis-dashboard" 
