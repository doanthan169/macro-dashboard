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
MAX_FEEDS_PER_CATEGORY = 6
MAX_ARTICLES_PER_FEED = 6
CACHE_TTL = 900  # seconds

# ── PAGE CONFIG ───────────────────────────────────
st.set_page_config(
    page_title="Macro Intelligence Dashboard",
    page_icon="📡",
    layout="wide",
)

# ── STYLING (kept clean & lightweight) ────────────
st.markdown("""
<style>
body { background-color: #0d1117; color: #e6edf3; }
.news { padding: 10px; border-bottom: 1px solid #222; }
.source { color: #8b949e; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

# ── SOURCES (cleaned: only valid RSS endpoints) ───
SOURCES = {
    "🇺🇸 US Macro": [
        ("Federal Reserve", "https://www.federalreserve.gov/feeds/press_all.xml"),
        ("BLS", "https://www.bls.gov/feed/ber.rss"),
        ("EIA", "https://www.eia.gov/rss/press_room.xml"),
        ("US Treasury", "https://home.treasury.gov/news/press-releases/rss.xml"),
        ("MarketWatch", "https://feeds.marketwatch.com/marketwatch/realtimeheadlines/")
    ],

    "🇨🇳 China Macro": [
        ("Reuters China", "https://feeds.reuters.com/reuters/CNTopNews"),
        ("SCMP", "https://www.scmp.com/rss/5/feed"),
        ("Nikkei Asia", "https://asia.nikkei.com/rss/feed/nar"),
        ("Caixin", "https://www.caixinglobal.com/rss/economy.xml"),
    ],

    "🇻🇳 Vietnam": [
        ("CafeF", "https://cafef.vn/rss/thi-truong-chung-khoan.rss"),
        ("VnExpress Economy", "https://vnexpress.net/rss/kinh-doanh.rss"),
        ("VnExpress Finance", "https://vnexpress.net/rss/kinh-doanh/tai-chinh.rss"),
        ("VIR", "https://vir.com.vn/rss/finance-banking.rss"),
    ],

    "🌐 Geopolitics": [
        ("Reuters", "https://feeds.reuters.com/reuters/topNews"),
        ("Bloomberg", "https://feeds.bloomberg.com/markets/news.rss"),
        ("Financial Times", "https://www.ft.com/rss/home/uk"),
        ("Politico", "https://rss.politico.com/economy.xml"),
        ("The Economist", "https://www.economist.com/finance-and-economics/rss.xml"),
    ],

    "🌾 Agriculture": [
        ("USDA", "https://www.usda.gov/rss20.xml"),
        ("AgriMoney", "https://www.agrimoney.com/feed/"),
    ],

    "🛢️ Energy": [
        ("Reuters Energy", "https://feeds.reuters.com/reuters/energy"),
        ("EIA", "https://www.eia.gov/rss/press_room.xml"),
        ("Rigzone", "https://www.rigzone.com/news/rss/rigzone_latest.aspx"),
    ],

    "⚙️ Metals": [
        ("Mining", "https://www.mining.com/feed/"),
        ("Reuters Metals", "https://feeds.reuters.com/reuters/basicMaterialsSector"),
        ("Fastmarkets", "https://www.fastmarkets.com/insights/rss/"),
    ],

    "🥇 Precious Metals": [
        ("World Gold Council", "https://www.gold.org/goldhub/research/rss"),
    ],

    "☕ Coffee": [
        ("ICO", "https://icocoffee.org/news/feed/"),
        ("Reuters Softs", "https://feeds.reuters.com/reuters/ConsumerProductsSector"),
    ],
}

# ── HELPERS ───────────────────────────────────────
def clean_html(text):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    return re.sub(r'\s+', ' ', text).strip()

def parse_time(entry):
    for attr in ['published_parsed', 'updated_parsed']:
        t = getattr(entry, attr, None)
        if t:
            try:
                return datetime(*t[:6], tzinfo=timezone.utc)
            except:
                pass
    return datetime.now(timezone.utc)

# ── FETCH SINGLE FEED ─────────────────────────────
def fetch_feed(url, source):
    try:
        r = requests.get(
            url,
            timeout=REQUEST_TIMEOUT,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        feed = feedparser.parse(r.content)

        items = []
        for e in feed.entries[:MAX_ARTICLES_PER_FEED]:
            title = clean_html(getattr(e, "title", ""))
            link = getattr(e, "link", "#")

            if not title:
                continue

            items.append({
                "title": title,
                "link": link,
                "source": source,
                "time": parse_time(e),
            })

        return items

    except Exception:
        return []

# ── PARALLEL FETCH ────────────────────────────────
@st.cache_data(ttl=CACHE_TTL)
def fetch_all(selected_categories):
    results = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []

        for cat in selected_categories:
            feeds = SOURCES[cat][:MAX_FEEDS_PER_CATEGORY]

            for source, url in feeds:
                futures.append(executor.submit(fetch_feed, url, source))

        for f in as_completed(futures):
            try:
                results.extend(f.result())
            except:
                pass

    return sorted(results, key=lambda x: x["time"], reverse=True)

# ── SIDEBAR ───────────────────────────────────────
st.sidebar.title("📡 Macro Intelligence")

selected_categories = []
for cat in SOURCES.keys():
    if st.sidebar.checkbox(cat, True):
        selected_categories.append(cat)

keyword = st.sidebar.text_input("🔍 Keyword")
max_age = st.sidebar.slider("Max age (hours)", 1, 168, 48)
debug = st.sidebar.checkbox("Debug mode", False)

if st.sidebar.button("🔄 Refresh"):
    st.cache_data.clear()

# ── MAIN ──────────────────────────────────────────
st.title("MACRO INTELLIGENCE")

vn_time = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
st.caption(f"🕐 {vn_time.strftime('%d %b %Y %H:%M')} ICT")

if not selected_categories:
    st.warning("Please select at least one category")
    st.stop()

with st.spinner("Fetching feeds..."):
    data = fetch_all(selected_categories)

# ── FILTER ────────────────────────────────────────
cutoff = datetime.now(timezone.utc).timestamp() - max_age * 3600

filtered = []
for item in data:
    if item["time"].timestamp() < cutoff:
        continue
    if keyword and keyword.lower() not in item["title"].lower():
        continue
    filtered.append(item)

# ── STATS ─────────────────────────────────────────
st.write(f"Total articles: {len(filtered)}")
st.write(f"Sources active: {len(set(i['source'] for i in filtered))}")

# ── DEBUG ─────────────────────────────────────────
if debug:
    st.write("Raw fetched:", len(data))
    st.json(data[:5])

# ── OUTPUT ────────────────────────────────────────
if not filtered:
    st.info("No articles found.")
else:
    for item in filtered:
        st.markdown(f"""
<div class="news">
<a href="{item['link']}" target="_blank"><b>{item['title']}</b></a><br>
<span class="source">{item['source']} · {item['time'].strftime('%Y-%m-%d %H:%M')}</span>
</div>
""", unsafe_allow_html=True)