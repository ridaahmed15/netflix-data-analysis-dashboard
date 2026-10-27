"""Data cleaning & feature engineering for the Netflix Titles dataset."""
from __future__ import annotations

import pandas as pd

KIDS = {"TV-Y", "TV-Y7", "TV-Y7-FV", "TV-G", "G"}
OLDER_KIDS = {"TV-PG", "PG"}
TEENS = {"TV-14", "PG-13"}
ADULTS = {"TV-MA", "R", "NC-17"}

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


def _rating_group(r: str) -> str:
    if r in KIDS:
        return "Kids"
    if r in OLDER_KIDS:
        return "Older Kids"
    if r in TEENS:
        return "Teens"
    if r in ADULTS:
        return "Adults"
    return "Unrated"


def _split(value: object) -> list[str]:
    if value is None or pd.isna(value) or value == "Unknown":
        return []
    return [p.strip() for p in str(value).split(",") if p.strip()]


def clean_dataset(raw: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned copy of the raw Netflix dataframe (no list columns)."""
    df = raw.copy()
    df.columns = [c.strip().lower() for c in df.columns]

    # 1. Trim whitespace & turn blank strings into real missing values
    for c in df.columns:
        if not pd.api.types.is_numeric_dtype(df[c]):
            df[c] = df[c].astype("string").str.strip().replace("", pd.NA)

    # 2. Remove duplicates
    df = df.drop_duplicates(subset="show_id").drop_duplicates(
        subset=["title", "type", "release_year"]).reset_index(drop=True)

    # 3. Fix shifted rows (duration was stored in the rating column)
    shifted = df["rating"].str.contains("min", na=False) & df["duration"].isna()
    df.loc[shifted, "duration"] = df.loc[shifted, "rating"]
    df.loc[shifted, "rating"] = pd.NA

    # 4. Missing categorical values
    for c in ["director", "cast", "country"]:
        df[c] = df[c].fillna("Unknown")
    df["rating"] = df["rating"].fillna("NR").replace({"UR": "NR"})
    df["rating_group"] = df["rating"].map(_rating_group)

    # 5. Dates
    df["date_added"] = pd.to_datetime(df["date_added"], format="%B %d, %Y", errors="coerce")
    df["year_added"] = df["date_added"].dt.year.astype("Int64")
    df["month_num"] = df["date_added"].dt.month.astype("Int64")
    df["month_added"] = df["date_added"].dt.month_name()
    df["release_lag"] = (df["year_added"] - df["release_year"]).clip(lower=0)

    # 6. Duration -> numeric columns
    num = pd.to_numeric(df["duration"].str.extract(r"(\d+)")[0], errors="coerce")
    df["movie_minutes"] = num.where(df["type"] == "Movie")
    df["tv_seasons"] = num.where(df["type"] == "TV Show")

    # 7. Convenience columns
    df["primary_country"] = df["country"].map(lambda v: (_split(v) or ["Unknown"])[0])
    df["decade"] = (df["release_year"] // 10 * 10).astype(int)

    # Plain object dtype keeps Plotly / Streamlit happy across pandas versions
    for c in df.columns:
        if pd.api.types.is_string_dtype(df[c]):
            df[c] = df[c].astype(object)
    return df


def add_list_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add list-valued helper columns used for exploding multi-value fields."""
    out = df.copy()
    out["country_list"] = out["country"].map(_split)
    out["genre_list"] = out["listed_in"].map(_split)
    out["cast_list"] = out["cast"].map(_split)
    out["director_list"] = out["director"].map(_split)
    return out


def cleaning_report(raw: pd.DataFrame, clean: pd.DataFrame) -> pd.DataFrame:
    """Before/after missing-value summary."""
    cols = ["director", "cast", "country", "date_added", "rating", "duration"]
    before = raw[cols].isna().sum()
    after = clean[cols].isna().sum() + (clean[["director", "cast", "country", "rating"]] == "Unknown").sum().reindex(cols).fillna(0)
    return pd.DataFrame({"Missing (raw)": before, "Missing / 'Unknown' (clean)": after.astype(int)})
