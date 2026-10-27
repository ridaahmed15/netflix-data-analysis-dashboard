"""Run:  python clean_data.py  -> writes data/netflix_cleaned.csv"""
from pathlib import Path
import pandas as pd
from data_processing import clean_dataset

root = Path(__file__).parent
raw = pd.read_csv(root / "data" / "netflix_titles.csv")
clean = clean_dataset(raw)
clean.to_csv(root / "data" / "netflix_cleaned.csv", index=False)
print(f"Raw: {raw.shape} -> Clean: {clean.shape}\nSaved data/netflix_cleaned.csv")
