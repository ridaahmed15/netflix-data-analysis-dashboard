"""NETFLIX Content Analysis Report - Streamlit dashboard (Red & Black theme)."""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data_processing import MONTHS, add_list_columns, clean_dataset, cleaning_report
from styles import CSS

st.set_page_config(page_title="Netflix Analysis Report", page_icon="🎬", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

RED, DARK_RED, WHITE, GREY = "#E50914", "#B20710", "#F5F5F1", "#8c8c8c"
RED_SCALE = ["#1a0003", "#6b0610", "#B20710", "#E50914", "#ff6b6b"]
TYPE_COLORS = {"Movie": RED, "TV Show": WHITE}
DATA_PATH = Path(__file__).parent / "data" / "netflix_titles.csv"


# ───────────────────────── Data ─────────────────────────
@st.cache_data(show_spinner="Cleaning data…")
def load_data(file_bytes: bytes | None = None):
    import io
    raw = pd.read_csv(io.BytesIO(file_bytes)) if file_bytes else pd.read_csv(DATA_PATH)
    clean = clean_dataset(raw)
    return raw, add_list_columns(clean)


def style(fig: go.Figure, height: int = 400, legend: bool = True) -> go.Figure:
    fig.update_layout(
        height=height, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=WHITE), margin=dict(l=10, r=10, t=50, b=10),
        title=dict(font=dict(size=16, color=WHITE), x=0.0), showlegend=legend,
        legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", y=-0.15),
        colorway=[RED, WHITE, DARK_RED, GREY, "#ff6b6b", "#5c5c5c"],
    )
    fig.update_xaxes(gridcolor="#222", zeroline=False)
    fig.update_yaxes(gridcolor="#222", zeroline=False)
    return fig


def show(fig: go.Figure) -> None:
    st.plotly_chart(fig, width="stretch")


def kpi(value, label: str) -> str:
    return f'<div class="kpi"><div class="v">{value}</div><div class="l">{label}</div></div>'


def section(title: str, caption: str = "") -> None:
    st.markdown(f'<div class="section">{title}</div>', unsafe_allow_html=True)
    if caption:
        st.markdown(f'<div class="caption">{caption}</div>', unsafe_allow_html=True)


def top_counts(df: pd.DataFrame, list_col: str, n: int = 15) -> pd.DataFrame:
    s = df[list_col].explode().dropna()
    return s.value_counts().head(n).rename_axis("name").reset_index(name="count")


def insight(text: str) -> None:
    st.markdown(f'<div class="insight">{text}</div>', unsafe_allow_html=True)


# ───────────────────────── Sidebar ─────────────────────────
st.sidebar.markdown("## 🎛️ Filters")
upload = st.sidebar.file_uploader("Use your own Netflix CSV (optional)", type="csv")
raw, df_all = load_data(upload.getvalue() if upload else None)

types = st.sidebar.multiselect("Content type", ["Movie", "TV Show"], default=["Movie", "TV Show"])
y_min, y_max = int(df_all["release_year"].min()), int(df_all["release_year"].max())
years = st.sidebar.slider("Release year", y_min, y_max, (1990, y_max))
groups = st.sidebar.multiselect("Audience group", ["Kids", "Older Kids", "Teens", "Adults", "Unrated"])
all_countries = df_all["country_list"].explode().dropna().value_counts().index.tolist()
countries = st.sidebar.multiselect("Country (any of)", all_countries)
all_genres = df_all["genre_list"].explode().dropna().value_counts().index.tolist()
genres = st.sidebar.multiselect("Genre (any of)", all_genres)

df = df_all[df_all["type"].isin(types) & df_all["release_year"].between(*years)]
if groups:
    df = df[df["rating_group"].isin(groups)]
if countries:
    df = df[df["country_list"].map(lambda l: any(c in l for c in countries))]
if genres:
    df = df[df["genre_list"].map(lambda l: any(g in l for g in genres))]

st.sidebar.markdown("---")
st.sidebar.caption(f"Showing **{len(df):,}** of **{len(df_all):,}** titles")

# ───────────────────────── Hero ─────────────────────────
st.markdown(
    """<div class="hero"><div class="badge">Data Analysis Report</div>
    <h1><span>NETFLIX</span> CONTENT ANALYSIS</h1>
    <p>An interactive deep-dive into the Netflix catalogue: what it streams, where it comes from,
    who it targets and how the library has grown over time.</p></div>""",
    unsafe_allow_html=True,
)

if df.empty:
    st.warning("No titles match the current filters. Adjust the sidebar and try again.")
    st.stop()

tabs = st.tabs(["Overview", "Trends", "Content", "Geography", "People", "Explorer", "Data Quality"])

# ───────────────────────── Overview ─────────────────────────
with tabs[0]:
    movies, shows = (df["type"] == "Movie").sum(), (df["type"] == "TV Show").sum()
    n_countries = df["country_list"].explode().nunique()
    n_genres = df["genre_list"].explode().nunique()
    avg_min = df["movie_minutes"].dropna().astype(float).mean()
    avg_seasons = df["tv_seasons"].dropna().astype(float).mean()

    cols = st.columns(6)
    items = [(f"{len(df):,}", "Total titles"), (f"{movies:,}", "Movies"), (f"{shows:,}", "TV shows"),
             (f"{n_countries}", "Countries"), (f"{n_genres}", "Genres"),
             (f"{avg_min:.0f} min" if pd.notna(avg_min) else "–", "Avg movie length")]
    for c, (v, l) in zip(cols, items):
        c.markdown(kpi(v, l), unsafe_allow_html=True)

    section("Catalogue at a glance")
    c1, c2 = st.columns([1, 2])
    with c1:
        t = df["type"].value_counts().reset_index()
        t.columns = ["type", "count"]
        fig = px.pie(t, names="type", values="count", hole=0.62, color="type", color_discrete_map=TYPE_COLORS,
                     title="Movies vs TV shows")
        fig.update_traces(textinfo="percent+label", marker=dict(line=dict(color="#0B0B0B", width=3)))
        show(style(fig, 380, legend=False))
    with c2:
        g = df.groupby(["year_added", "type"]).size().reset_index(name="count")
        fig = px.bar(g, x="year_added", y="count", color="type", color_discrete_map=TYPE_COLORS,
                     title="Titles added to Netflix per year", labels={"year_added": "Year added", "count": "Titles"})
        show(style(fig, 380))

    section("Key insights", "Generated automatically from the filtered data.")
    peak = df["year_added"].value_counts().idxmax()
    top_country = top_counts(df, "country_list", 1)
    top_genre = top_counts(df, "genre_list", 1)
    top_rating = df["rating"].value_counts().idxmax()
    ic1, ic2 = st.columns(2)
    with ic1:
        insight(f"🎬 <b>{movies / len(df):.0%}</b> of titles are movies, <b>{shows / len(df):.0%}</b> are TV shows.")
        insight(f"📈 Netflix added the most titles in <b>{peak}</b> ({(df['year_added'] == peak).sum():,} titles).")
        if len(top_country):
            insight(f"🌍 <b>{top_country.iloc[0]['name']}</b> is the top producing country "
                    f"with <b>{top_country.iloc[0]['count']:,}</b> titles.")
    with ic2:
        if len(top_genre):
            insight(f"🎭 The most common genre is <b>{top_genre.iloc[0]['name']}</b> "
                    f"({top_genre.iloc[0]['count']:,} titles).")
        insight(f"🔞 Most common rating: <b>{top_rating}</b> "
                f"({(df['rating'] == top_rating).mean():.0%} of the catalogue).")
        if pd.notna(avg_seasons):
            insight(f"📺 The average TV show has <b>{avg_seasons:.1f}</b> season(s); "
                    f"the average movie runs <b>{avg_min:.0f}</b> minutes." if pd.notna(avg_min) else "")

# ───────────────────────── Trends ─────────────────────────
with tabs[1]:
    section("Growth over time")
    c1, c2 = st.columns(2)
    with c1:
        cum = df.dropna(subset=["year_added"]).groupby(["year_added", "type"]).size().reset_index(name="n")
        cum["cumulative"] = cum.groupby("type")["n"].cumsum()
        fig = px.area(cum, x="year_added", y="cumulative", color="type", color_discrete_map=TYPE_COLORS,
                      title="Cumulative catalogue size", labels={"year_added": "Year added", "cumulative": "Titles"})
        show(style(fig))
    with c2:
        r = df.groupby(["release_year", "type"]).size().reset_index(name="count")
        fig = px.line(r, x="release_year", y="count", color="type", color_discrete_map=TYPE_COLORS,
                      title="Titles by original release year", labels={"release_year": "Release year", "count": "Titles"})
        show(style(fig))

    section("Seasonality", "When does Netflix add new content?")
    c1, c2 = st.columns(2)
    with c1:
        m = df.dropna(subset=["month_added"])["month_added"].value_counts().reindex(MONTHS).fillna(0).reset_index()
        m.columns = ["month", "count"]
        fig = px.bar(m, x="month", y="count", title="Titles added by month", color="count",
                     color_continuous_scale=RED_SCALE)
        fig.update_coloraxes(showscale=False)
        show(style(fig, legend=False))
    with c2:
        hm = df.dropna(subset=["year_added"]).copy()
        hm = hm[hm["year_added"] >= 2014]
        pv = hm.pivot_table(index="year_added", columns="month_added", values="show_id", aggfunc="count").reindex(columns=MONTHS)
        fig = px.imshow(pv.fillna(0), aspect="auto", color_continuous_scale=RED_SCALE,
                        title="Heatmap: year × month added", labels=dict(color="Titles"))
        show(style(fig))

    section("Release lag", "Years between a title's release and its arrival on Netflix.")
    lag = df.dropna(subset=["release_lag"])
    lag = lag[lag["release_lag"] <= 30]
    fig = px.histogram(lag, x="release_lag", color="type", color_discrete_map=TYPE_COLORS, nbins=31, barmode="overlay",
                       opacity=0.8, title="Release lag distribution (≤ 30 years)", labels={"release_lag": "Years"})
    show(style(fig, 360))
    st.caption(f"Median lag: **{lag['release_lag'].astype(float).median():.0f}** year(s). "
               f"{(lag['release_lag'] <= 1).mean():.0%} of titles arrive within a year of release.")

# ───────────────────────── Content ─────────────────────────
with tabs[2]:
    section("Genres")
    c1, c2 = st.columns(2)
    with c1:
        tg = top_counts(df, "genre_list", 15).sort_values("count")
        fig = px.bar(tg, x="count", y="name", orientation="h", title="Top 15 genres", color="count",
                     color_continuous_scale=RED_SCALE, labels={"name": "", "count": "Titles"})
        fig.update_coloraxes(showscale=False)
        show(style(fig, 480, legend=False))
    with c2:
        ge = df[["genre_list", "rating_group"]].explode("genre_list").dropna().reset_index(drop=True)
        top12 = ge["genre_list"].value_counts().head(12).index
        ct = pd.crosstab(ge[ge["genre_list"].isin(top12)]["genre_list"], ge["rating_group"])
        fig = px.imshow(ct, aspect="auto", color_continuous_scale=RED_SCALE, text_auto=True,
                        title="Top genres × audience group", labels=dict(color="Titles", x="", y=""))
        show(style(fig, 480))

    section("Ratings & audience")
    c1, c2 = st.columns(2)
    with c1:
        rt = df.groupby(["rating", "type"]).size().reset_index(name="count")
        order = df["rating"].value_counts().index.tolist()
        fig = px.bar(rt, x="rating", y="count", color="type", color_discrete_map=TYPE_COLORS,
                     category_orders={"rating": order}, title="Ratings by type", labels={"count": "Titles", "rating": ""})
        show(style(fig))
    with c2:
        ag = df["rating_group"].value_counts().reset_index()
        ag.columns = ["group", "count"]
        fig = px.pie(ag, names="group", values="count", hole=0.55, title="Audience groups",
                     color_discrete_sequence=[RED, WHITE, DARK_RED, GREY, "#ff6b6b"])
        fig.update_traces(marker=dict(line=dict(color="#0B0B0B", width=3)))
        show(style(fig))

    section("Duration")
    c1, c2 = st.columns(2)
    with c1:
        mv = df.dropna(subset=["movie_minutes"]).copy()
        mv["movie_minutes"] = mv["movie_minutes"].astype(float)
        if len(mv):
            fig = px.histogram(mv, x="movie_minutes", nbins=40, title="Movie runtime (minutes)",
                               color_discrete_sequence=[RED], labels={"movie_minutes": "Minutes"})
            fig.add_vline(x=mv["movie_minutes"].median(), line_dash="dash", line_color=WHITE,
                          annotation_text=f"median {mv['movie_minutes'].median():.0f}")
            show(style(fig, legend=False))
        else:
            st.info("No movies in the current selection.")
    with c2:
        tv = df.dropna(subset=["tv_seasons"]).copy()
        if len(tv):
            s = tv["tv_seasons"].astype(int).clip(upper=10).value_counts().sort_index().reset_index()
            s.columns = ["seasons", "count"]
            s["seasons"] = s["seasons"].astype(str).replace({"10": "10+"})
            fig = px.bar(s, x="seasons", y="count", title="TV shows by number of seasons",
                         color_discrete_sequence=[RED], labels={"seasons": "Seasons", "count": "Shows"})
            show(style(fig, legend=False))
        else:
            st.info("No TV shows in the current selection.")

    section("Description keywords", "Most frequent meaningful words in title descriptions.")
    STOP = set("""the a an and or of to in on for with his her their its is are was were be by as at from he she they it this that
    who whom after when while into out up down over under about than then them has have had not but what which will can one two new
    more most all other some only also just his hers him i you we our your me my so if no""".split())
    words = Counter(w for d in df["description"].dropna() for w in re.findall(r"[a-z]{4,}", d.lower()) if w not in STOP)
    kw = pd.DataFrame(words.most_common(20), columns=["word", "count"]).sort_values("count")
    fig = px.bar(kw, x="count", y="word", orientation="h", color="count", color_continuous_scale=RED_SCALE,
                 title="Top 20 description keywords", labels={"word": ""})
    fig.update_coloraxes(showscale=False)
    show(style(fig, 520, legend=False))

# ───────────────────────── Geography ─────────────────────────
with tabs[3]:
    section("Where does the content come from?")
    cc = df["country_list"].explode().dropna().value_counts().rename_axis("country").reset_index(name="count")
    fig = px.choropleth(cc, locations="country", locationmode="country names", color="count",
                        color_continuous_scale=RED_SCALE, title="Titles by country (co-productions counted for each country)")
    fig.update_geos(bgcolor="rgba(0,0,0,0)", showframe=False, showcoastlines=False, showland=True,
                    landcolor="#1a1a1a", showcountries=True, countrycolor="#333", projection_type="natural earth")
    show(style(fig, 520))

    c1, c2 = st.columns(2)
    with c1:
        top = cc.head(12).sort_values("count")
        fig = px.bar(top, x="count", y="country", orientation="h", title="Top 12 countries", color="count",
                     color_continuous_scale=RED_SCALE, labels={"country": ""})
        fig.update_coloraxes(showscale=False)
        show(style(fig, 440, legend=False))
    with c2:
        tc = df[["country_list", "type"]].explode("country_list").dropna()
        t10 = cc.head(10)["country"].tolist()
        tc = tc[tc["country_list"].isin(t10)].groupby(["country_list", "type"]).size().reset_index(name="count")
        fig = px.bar(tc, x="country_list", y="count", color="type", color_discrete_map=TYPE_COLORS, barmode="stack",
                     category_orders={"country_list": t10}, title="Movies vs TV shows – top 10 countries",
                     labels={"country_list": "", "count": "Titles"})
        show(style(fig, 440))

    section("Top countries over time")
    ct5 = cc.head(5)["country"].tolist()
    tt = df[["country_list", "year_added"]].explode("country_list").dropna()
    tt = tt[tt["country_list"].isin(ct5) & (tt["year_added"] >= 2012)].groupby(["year_added", "country_list"]).size().reset_index(name="count")
    fig = px.line(tt, x="year_added", y="count", color="country_list", markers=True,
                  title="Titles added per year – top 5 countries",
                  color_discrete_sequence=[RED, WHITE, "#ff6b6b", GREY, DARK_RED], labels={"year_added": "Year added", "country_list": "Country"})
    show(style(fig, 400))

# ───────────────────────── People ─────────────────────────
with tabs[4]:
    c1, c2 = st.columns(2)
    with c1:
        section("Top directors")
        d = top_counts(df, "director_list", 15).sort_values("count")
        fig = px.bar(d, x="count", y="name", orientation="h", color="count", color_continuous_scale=RED_SCALE,
                     title="Most prolific directors", labels={"name": "", "count": "Titles"})
        fig.update_coloraxes(showscale=False)
        show(style(fig, 520, legend=False))
    with c2:
        section("Top actors")
        a = top_counts(df, "cast_list", 15).sort_values("count")
        fig = px.bar(a, x="count", y="name", orientation="h", color="count", color_continuous_scale=RED_SCALE,
                     title="Most frequently cast actors", labels={"name": "", "count": "Titles"})
        fig.update_coloraxes(showscale=False)
        show(style(fig, 520, legend=False))
    known = (df["director"] != "Unknown").mean()
    st.caption(f"Director is known for **{known:.0%}** of titles in this selection – TV shows often have no listed director.")

# ───────────────────────── Explorer ─────────────────────────
with tabs[5]:
    section("Title explorer", "Search the filtered catalogue and download the result.")
    q = st.text_input("🔎 Search title, cast, director or description")
    view = df
    if q:
        mask = pd.Series(False, index=df.index)
        for col in ["title", "cast", "director", "description"]:
            mask |= df[col].str.contains(q, case=False, na=False, regex=False)
        view = df[mask]
    cols = ["title", "type", "release_year", "year_added", "rating", "duration", "country", "listed_in", "director", "cast", "description"]
    st.write(f"**{len(view):,}** titles")
    st.dataframe(view[cols].reset_index(drop=True), width="stretch", height=480)
    st.download_button("⬇ Download filtered data (CSV)", view[cols].to_csv(index=False).encode("utf-8"),
                       "netflix_filtered.csv", "text/csv")

# ───────────────────────── Data quality ─────────────────────────
with tabs[6]:
    section("Data cleaning summary")
    clean_only = df_all.drop(columns=[c for c in df_all.columns if c.endswith("_list")])
    c1, c2, c3 = st.columns(3)
    c1.markdown(kpi(f"{len(raw):,}", "Raw rows"), unsafe_allow_html=True)
    c2.markdown(kpi(f"{len(clean_only):,}", "Rows after cleaning"), unsafe_allow_html=True)
    c3.markdown(kpi(f"{clean_only.shape[1]}", "Columns (raw: " + str(raw.shape[1]) + ")"), unsafe_allow_html=True)
    st.markdown("&nbsp;")
    st.dataframe(cleaning_report(raw, clean_only), width="stretch")
    st.markdown("""
**Cleaning steps applied**
1. Stripped whitespace and converted blank strings to missing values.
2. Removed duplicate rows (by `show_id` and by title + type + release year).
3. Repaired rows where the runtime had been stored in the `rating` column.
4. Filled missing `director`, `cast`, `country` with **Unknown**; missing / `UR` ratings → **NR**.
5. Parsed `date_added` to a real date; derived `year_added`, `month_added`, `release_lag`.
6. Split `duration` into numeric `movie_minutes` and `tv_seasons`.
7. Added `rating_group` (Kids / Older Kids / Teens / Adults / Unrated), `primary_country`, `decade`.
8. Multi-value fields (country, genres, cast, directors) are split into lists for accurate counting.
""")
    st.download_button("⬇ Download cleaned dataset (CSV)", clean_only.to_csv(index=False).encode("utf-8"),
                       "netflix_cleaned.csv", "text/csv")

st.markdown('<div class="footer">BUILT WITH <b>STREAMLIT</b> · <b>PLOTLY</b> · <b>PANDAS</b></div>', unsafe_allow_html=True)
