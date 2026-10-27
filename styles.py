"""Red & Black Netflix-inspired theme (CSS)."""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;500;600;700;800&display=swap');

:root { --red:#E50914; --dark-red:#B20710; --black:#0B0B0B; --card:#141414; --line:#2a2a2a; --txt:#F5F5F1; --muted:#9a9a9a; }

html, body, [class*="css"], .stApp { font-family:'Inter',sans-serif; }
.stApp { background: radial-gradient(1200px 500px at 85% -10%, rgba(229,9,20,.18), transparent 60%), var(--black); }
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 1.5rem; max-width: 1400px; }

/* Hero */
.hero { padding:2.2rem 2.4rem; border-radius:18px; margin-bottom:1.4rem; position:relative; overflow:hidden;
        background: linear-gradient(120deg, #1a0003 0%, #0B0B0B 55%, #2a0004 100%); border:1px solid var(--line); border-left:6px solid var(--red); }
.hero h1 { font-family:'Bebas Neue',sans-serif; font-size:4rem; letter-spacing:4px; margin:0; line-height:1; color:var(--txt); }
.hero h1 span { color:var(--red); }
.hero p { color:var(--muted); margin:.6rem 0 0; font-size:1.05rem; max-width:760px; }
.badge { display:inline-block; background:var(--red); color:#fff; font-weight:700; font-size:.72rem; letter-spacing:2px;
         padding:.25rem .7rem; border-radius:4px; margin-bottom:.8rem; text-transform:uppercase; }

/* KPI cards */
.kpi { background:var(--card); border:1px solid var(--line); border-top:3px solid var(--red); border-radius:12px; padding:1.1rem 1.2rem;
       transition:transform .2s, box-shadow .2s; height:100%; }
.kpi:hover { transform:translateY(-4px); box-shadow:0 10px 30px rgba(229,9,20,.25); }
.kpi .v { font-family:'Bebas Neue',sans-serif; font-size:2.6rem; color:var(--txt); line-height:1; letter-spacing:1px; }
.kpi .l { color:var(--muted); font-size:.75rem; text-transform:uppercase; letter-spacing:1.5px; margin-top:.35rem; font-weight:600; }

/* Section titles */
.section { font-family:'Bebas Neue',sans-serif; font-size:1.9rem; letter-spacing:2px; margin:1.6rem 0 .2rem; color:var(--txt); }
.section::before { content:''; display:inline-block; width:8px; height:1.5rem; background:var(--red); margin-right:.7rem; vertical-align:-3px; border-radius:2px; }
.caption { color:var(--muted); font-size:.9rem; margin-bottom:.6rem; }

/* Insight boxes */
.insight { background:linear-gradient(90deg, rgba(229,9,20,.14), rgba(229,9,20,.02)); border-left:4px solid var(--red);
           padding:.8rem 1.1rem; border-radius:6px; margin:.45rem 0; color:var(--txt); }
.insight b { color:#ff4b55; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap:.4rem; border-bottom:1px solid var(--line); }
.stTabs [data-baseweb="tab"] { background:transparent; color:var(--muted); font-weight:700; letter-spacing:1px; text-transform:uppercase; font-size:.85rem; padding:.7rem 1.2rem; border-radius:8px 8px 0 0; }
.stTabs [aria-selected="true"] { color:#fff !important; background:rgba(229,9,20,.15); }
.stTabs [data-baseweb="tab-highlight"] { background-color:var(--red) !important; height:3px; }

/* Sidebar */
section[data-testid="stSidebar"] { background:#0f0f0f; border-right:1px solid var(--line); }
section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 { font-family:'Bebas Neue',sans-serif; letter-spacing:2px; color:var(--red); }
span[data-baseweb="tag"] { background-color:var(--red) !important; color:#fff !important; }

/* Buttons / inputs */
.stDownloadButton button, .stButton button { background:var(--red); color:#fff; border:none; font-weight:700; border-radius:8px; padding:.55rem 1.2rem; }
.stDownloadButton button:hover, .stButton button:hover { background:var(--dark-red); color:#fff; }
div[data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:10px; overflow:hidden; }
hr { border-color:var(--line); }
.footer { text-align:center; color:var(--muted); font-size:.8rem; padding:2rem 0 .5rem; letter-spacing:1px; }
.footer b { color:var(--red); }
</style>
"""
