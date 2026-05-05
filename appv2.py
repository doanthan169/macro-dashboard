import streamlit as st
import feedparser
import requests
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

# ── CONFIG ─────────────────────────────────────────
MAX_WORKERS = 8
REQUEST_TIMEOUT = 8
MAX_FEEDS_PER_CATEGORY = 5
MAX_ARTICLES_PER_FEED = 6

# ── PAGE CONFIG ───────────────────────────────────
st.set_page_config(
    page_title="Macro Intelligence Dashboard",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── ORIGINAL STRUCTURE PRESERVED ───────────────────
SOURCES = {
    "🇺🇸 US Macro": {"module": "A", "feeds": [
        ("Federal Reserve","https://www.federalreserve.gov/feeds/press_all.xml"),
        ("BLS","https://www.bls.gov/feed/ber.rss"),
        ("EIA","https://www.eia.gov/rss/press_room.xml"),
        ("MarketWatch","https://feeds.marketwatch.com/marketwatch/realtimeheadlines/")
    ]},
    "🇨🇳 China Macro": {"module": "A", "feeds": [
        ("Reuters China","https://feeds.reuters.com/reuters/CNTopNews"),
        ("SCMP","https://www.scmp.com/rss/5/feed"),
        ("Caixin","https://www.caixinglobal.com/rss/economy.xml"),
    ]},
    "🇻🇳 Vietnam": {"module": "A", "feeds": [
        ("CafeF","https://cafef.vn/rss/thi-truong-chung-khoan.rss"),
        ("VnExpress","https://vnexpress.net/rss/kinh-doanh.rss"),
        ("VIR","https://vir.com.vn/rss/finance-banking.rss"),
    ]},
    "🌐 Geopolitics": {"module": "A", "feeds": [
        ("Reuters","https://feeds.reuters.com/reuters/topNews"),
        ("Bloomberg","https://feeds.bloomberg.com/markets/news.rss"),
        ("FT","https://www.ft.com/rss/home/uk"),
    ]},

    "🌾 Agriculture": {"module": "B", "feeds": [
        ("USDA","https://www.usda.gov/rss20.xml"),
        ("AgriMoney","https://www.agrimoney.com/feed/")
    ]},
    "🛢️ Energy": {"module": "B", "feeds": [
        ("Reuters Energy","https://feeds.reuters.com/reuters/energy"),
        ("EIA","https://www.eia.gov/rss/press_room.xml"),
    ]},
    "⚙️ Metals": {"module": "B", "feeds": [
        ("Mining","https://www.mining.com/feed/"),
        ("Reuters Metals","https://feeds.reuters.com/reuters/basicMaterialsSector"),
    ]},
    "☕ Coffee": {"module": "B", "feeds": [
        ("ICO","https://icocoffee.org/news/feed/"),
        ("Reuters Softs","https://feeds.reuters.com/reuters/ConsumerProductsSector"),
    ]},
}

MODULE_A = [k for k,v in SOURCES.items() if v["module"]=="A"]
MODULE_B = [k for k,v in SOURCES.items() if v["module"]=="B"]

# ── HELPERS ───────────────────────────────────────
def clean_html(text):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    return re.sub(r'\s+', ' ', text).strip()

def parse_time(entry):
    for attr in ['published_parsed','updated_parsed']:
        t = getattr(entry, attr, None)
        if t:
            try:
                return datetime(*t[:6], tzinfo=timezone.utc)
            except:
                pass
    return datetime.now(timezone.utc)

# ── SAFE FETCH ────────────────────────────────────
def fetch_feed(url, name, category):
    try:
        r = requests.get(url, timeout=REQUEST_TIMEOUT,
                         headers={"User-Agent":"Mozilla/5.0"})
        feed = feedparser.parse(r.content)

        out = []
        for e in feed.entries[:MAX_ARTICLES_PER_FEED]:
            title = clean_html(getattr(e,"title",""))
            link = getattr(e,"link","#")
            if not title:
                continue
            out.append({
                "title":title,
                "link":link,
                "source":name,
                "time":parse_time(e),
                "category":category
            })
        return out
    except:
        return []

# ── PARALLEL CATEGORY FETCH ───────────────────────
@st.cache_data(ttl=900)
def fetch_all(selected_cats):
    results = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []

        for cat in selected_cats:
            feeds = SOURCES[cat]["feeds"][:MAX_FEEDS_PER_CATEGORY]
            for name,url in feeds:
                futures.append(executor.submit(fetch_feed,url,name,cat))

        for f in as_completed(futures):
            try:
                results.extend(f.result())
            except:
                pass

    return sorted(results, key=lambda x:x["time"], reverse=True)

# ── SIDEBAR ───────────────────────────────────────
with st.sidebar:
    st.markdown("### 📡 Macro Intelligence")

    selected = []

    st.markdown("**Module A — VN Fund**")
    for c in MODULE_A:
        if st.checkbox(c, True):
            selected.append(c)

    st.markdown("**Module B — Commodity**")
    for c in MODULE_B:
        if st.checkbox(c, True):
            selected.append(c)

    keyword = st.text_input("Keyword")
    hours = st.slider("Max age (hours)",1,168,48)

    if st.button("Refresh"):
        st.cache_data.clear()

# ── MAIN ──────────────────────────────────────────
st.title("MACRO INTELLIGENCE")

if not selected:
    st.stop()

with st.spinner("Fetching feeds..."):
    data = fetch_all(selected)

# ── FILTER ────────────────────────────────────────
cutoff = datetime.now(timezone.utc).timestamp() - hours*3600

filtered = []
for d in data:
    if d["time"].timestamp() < cutoff:
        continue
    if keyword and keyword.lower() not in d["title"].lower():
        continue
    filtered.append(d)

# ── RENDER (CATEGORY LAYER PRESERVED) ─────────────
for cat in selected:
    cat_items = [x for x in filtered if x["category"]==cat]

    if not cat_items:
        continue

    st.subheader(f"{cat} ({len(cat_items)})")

    for item in cat_items:
        st.markdown(f"""
**[{item['title']}]({item['link']})**  
{item['source']} · {item['time'].strftime('%Y-%m-%d %H:%M')}
""")
