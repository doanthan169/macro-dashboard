import streamlit as st
import feedparser
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import re
from urllib.parse import urlparse

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Macro Intelligence Dashboard",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── STYLING ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

.stApp {
    background-color: #0d1117;
    color: #e6edf3;
}

section[data-testid="stSidebar"] {
    background-color: #161b22;
    border-right: 1px solid #21262d;
}

section[data-testid="stSidebar"] * {
    color: #e6edf3 !important;
}

.main-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.6rem;
    font-weight: 500;
    color: #58a6ff;
    letter-spacing: -0.02em;
    margin-bottom: 0;
    padding-bottom: 0;
}

.sub-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    color: #8b949e;
    letter-spacing: 0.08em;
    margin-top: 2px;
    margin-bottom: 24px;
}

.stat-box {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 8px;
    padding: 16px 20px;
    text-align: center;
}

.stat-number {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2rem;
    font-weight: 500;
    color: #58a6ff;
    line-height: 1;
}

.stat-label {
    font-size: 0.72rem;
    color: #8b949e;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-top: 4px;
}

.news-card {
    background: #161b22;
    border: 1px solid #21262d;
    border-left: 3px solid #21262d;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 10px;
    transition: border-color 0.2s;
}

.news-card:hover { border-left-color: #58a6ff; }

.card-us      { border-left-color: #3b82f6 !important; }
.card-china   { border-left-color: #ef4444 !important; }
.card-vietnam { border-left-color: #22c55e !important; }
.card-agri    { border-left-color: #f59e0b !important; }
.card-energy  { border-left-color: #f97316 !important; }
.card-metals  { border-left-color: #a855f7 !important; }
.card-coffee  { border-left-color: #92400e !important; }
.card-geo     { border-left-color: #ec4899 !important; }

.card-title {
    font-size: 0.92rem;
    font-weight: 500;
    color: #e6edf3;
    line-height: 1.4;
    margin-bottom: 8px;
}

.card-title a {
    color: #e6edf3;
    text-decoration: none;
}

.card-title a:hover { color: #58a6ff; }

.card-meta {
    display: flex;
    gap: 12px;
    align-items: center;
    flex-wrap: wrap;
}

.badge {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    font-weight: 500;
    padding: 2px 8px;
    border-radius: 4px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.badge-us      { background: #1d3a6e; color: #93c5fd; }
.badge-china   { background: #4c1d1d; color: #fca5a5; }
.badge-vietnam { background: #14532d; color: #86efac; }
.badge-agri    { background: #451a03; color: #fcd34d; }
.badge-energy  { background: #431407; color: #fdba74; }
.badge-metals  { background: #3b0764; color: #d8b4fe; }
.badge-coffee  { background: #292524; color: #d6b896; }
.badge-geo     { background: #500724; color: #f9a8d4; }

.meta-source {
    font-size: 0.72rem;
    color: #8b949e;
    font-family: 'IBM Plex Mono', monospace;
}

.meta-time {
    font-size: 0.72rem;
    color: #6e7681;
    font-family: 'IBM Plex Mono', monospace;
}

.divider {
    border: none;
    border-top: 1px solid #21262d;
    margin: 20px 0;
}

.section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    color: #8b949e;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 12px;
    margin-top: 20px;
}

.empty-state {
    text-align: center;
    padding: 60px 20px;
    color: #8b949e;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
}

.refresh-info {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    color: #6e7681;
}

.stButton button {
    background: #21262d !important;
    color: #e6edf3 !important;
    border: 1px solid #30363d !important;
    border-radius: 6px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.78rem !important;
    padding: 6px 16px !important;
    transition: all 0.2s !important;
}

.stButton button:hover {
    background: #30363d !important;
    border-color: #58a6ff !important;
}

div[data-testid="stTextInput"] input,
div[data-testid="stSelectbox"] select {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    color: #e6edf3 !important;
    border-radius: 6px !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}

.stMultiSelect [data-baseweb="select"] {
    background: #161b22 !important;
}

div[data-testid="stCheckbox"] label {
    color: #e6edf3 !important;
    font-size: 0.85rem !important;
}

.stSlider > div { color: #e6edf3 !important; }

h1, h2, h3 { color: #e6edf3 !important; }

.stMarkdown p { color: #c9d1d9; }
</style>
""", unsafe_allow_html=True)

# ── RSS SOURCES ───────────────────────────────────────────────────────────────
SOURCES = {
    "🇺🇸 US Macro": {
        "color_class": "us",
        "badge_class": "badge-us",
        "feeds": [
            {"name": "Federal Reserve", "url": "https://www.federalreserve.gov/feeds/press_all.xml"},
            {"name": "BLS", "url": "https://www.bls.gov/feed/ber.rss"},
            {"name": "EIA", "url": "https://www.eia.gov/rss/press_room.xml"},
            {"name": "US Treasury", "url": "https://home.treasury.gov/news/press-releases/rss.xml"},
            {"name": "MarketWatch", "url": "https://feeds.marketwatch.com/marketwatch/realtimeheadlines/"},
        ]
    },
    "🇨🇳 China Macro": {
        "color_class": "china",
        "badge_class": "badge-china",
        "feeds": [
            {"name": "Reuters China", "url": "https://feeds.reuters.com/reuters/CNTopNews"},
            {"name": "South China Morning Post", "url": "https://www.scmp.com/rss/5/feed"},
            {"name": "Nikkei Asia", "url": "https://asia.nikkei.com/rss/feed/nar"},
        ]
    },
    "🇻🇳 Vietnam": {
        "color_class": "vietnam",
        "badge_class": "badge-vietnam",
        "feeds": [
            {"name": "CafeF", "url": "https://cafef.vn/rss/thi-truong-chung-khoan.rss"},
            {"name": "VnExpress Economy", "url": "https://vnexpress.net/rss/kinh-doanh.rss"},
            {"name": "VnExpress Finance", "url": "https://vnexpress.net/rss/kinh-doanh/tai-chinh.rss"},
            {"name": "Vietnam Investment Review", "url": "https://vir.com.vn/rss/finance-banking.rss"},
        ]
    },
    "🌾 Agriculture": {
        "color_class": "agri",
        "badge_class": "badge-agri",
        "feeds": [
            {"name": "USDA", "url": "https://www.usda.gov/rss20.xml"},
            {"name": "AgriMoney", "url": "https://www.agrimoney.com/feed/"},
            {"name": "IGC Grains", "url": "https://www.igc.int/en/news/newslist.aspx"},
        ]
    },
    "🛢️ Energy": {
        "color_class": "energy",
        "badge_class": "badge-energy",
        "feeds": [
            {"name": "Reuters Energy", "url": "https://feeds.reuters.com/reuters/energy"},
            {"name": "EIA Energy", "url": "https://www.eia.gov/rss/press_room.xml"},
            {"name": "Rigzone", "url": "https://www.rigzone.com/news/rss/rigzone_latest.aspx"},
        ]
    },
    "🥇 Metals": {
        "color_class": "metals",
        "badge_class": "badge-metals",
        "feeds": [
            {"name": "World Gold Council", "url": "https://www.gold.org/goldhub/research/rss"},
            {"name": "Mining.com", "url": "https://www.mining.com/feed/"},
            {"name": "Reuters Metals", "url": "https://feeds.reuters.com/reuters/basicMaterialsSector"},
        ]
    },
    "☕ Coffee": {
        "color_class": "coffee",
        "badge_class": "badge-coffee",
        "feeds": [
            {"name": "ICO", "url": "https://icocoffee.org/news/feed/"},
            {"name": "Reuters Softs", "url": "https://feeds.reuters.com/reuters/ConsumerProductsSector"},
        ]
    },
    "🌐 Geopolitics": {
        "color_class": "geo",
        "badge_class": "badge-geo",
        "feeds": [
            {"name": "Reuters Top News", "url": "https://feeds.reuters.com/reuters/topNews"},
            {"name": "Financial Times", "url": "https://www.ft.com/rss/home/uk"},
            {"name": "Watcher.Guru", "url": "https://watcher.guru/news/feed"},
            {"name": "Bloomberg Markets", "url": "https://feeds.bloomberg.com/markets/news.rss"},
            {"name": "The Economist", "url": "https://www.economist.com/finance-and-economics/rss.xml"},
        ]
    },
}

# ── HELPERS ───────────────────────────────────────────────────────────────────
def clean_html(text):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'&quot;', '"', text)
    text = re.sub(r'&#39;', "'", text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_time(entry):
    for attr in ['published_parsed', 'updated_parsed']:
        t = getattr(entry, attr, None)
        if t:
            try:
                return datetime(*t[:6], tzinfo=timezone.utc)
            except Exception:
                pass
    return datetime.now(timezone.utc)

def time_ago(dt):
    now = datetime.now(timezone.utc)
    diff = now - dt
    secs = int(diff.total_seconds())
    if secs < 60: return f"{secs}s ago"
    if secs < 3600: return f"{secs//60}m ago"
    if secs < 86400: return f"{secs//3600}h ago"
    return f"{secs//86400}d ago"

def get_domain(url):
    try:
        return urlparse(url).netloc.replace('www.', '')
    except Exception:
        return url

@st.cache_data(ttl=900, show_spinner=False)
def fetch_feed(url, source_name):
    try:
        feed = feedparser.parse(url, request_headers={
            'User-Agent': 'Mozilla/5.0 (compatible; MacroBot/1.0)'
        })
        items = []
        for entry in feed.entries[:15]:
            title = clean_html(getattr(entry, 'title', ''))
            link = getattr(entry, 'link', '#')
            if not title:
                continue
            items.append({
                'title': title,
                'link': link,
                'source': source_name,
                'time': parse_time(entry),
            })
        return items
    except Exception:
        return []

def fetch_category(category_key):
    cat = SOURCES[category_key]
    all_items = []
    for feed_info in cat['feeds']:
        items = fetch_feed(feed_info['url'], feed_info['name'])
        all_items.extend(items)
    all_items.sort(key=lambda x: x['time'], reverse=True)
    return all_items

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📡 Macro Intelligence")
    st.markdown('<div class="refresh-info">Real-time RSS aggregator</div>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("**Categories**")
    selected_cats = []
    for cat_key in SOURCES:
        if st.checkbox(cat_key, value=True, key=f"cat_{cat_key}"):
            selected_cats.append(cat_key)

    st.markdown("---")
    st.markdown("**Filters**")
    keyword = st.text_input("🔍 Keyword search", placeholder="e.g. tariff, rate, gold...")
    max_age_hours = st.slider("Max age (hours)", 1, 168, 48)

    st.markdown("---")
    st.markdown("**Sort by**")
    sort_by = st.radio("", ["Newest first", "By category"], label_visibility="collapsed")

    st.markdown("---")
    if st.button("🔄 Refresh feeds", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    vn_time = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
    st.markdown(f'<div class="refresh-info">🕐 {vn_time.strftime("%d %b %Y, %H:%M")} ICT<br>Cache: 15 min</div>', unsafe_allow_html=True)

# ── MAIN AREA ─────────────────────────────────────────────────────────────────
st.markdown('<div class="main-header">MACRO INTELLIGENCE</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">VIETNAM FUND MANAGEMENT · COMMODITY MARKETS · REAL-TIME RSS</div>', unsafe_allow_html=True)

if not selected_cats:
    st.markdown('<div class="empty-state">No categories selected.<br>Enable at least one in the sidebar.</div>', unsafe_allow_html=True)
    st.stop()

# Fetch all data
with st.spinner("Fetching feeds..."):
    all_articles = []
    for cat_key in selected_cats:
        items = fetch_category(cat_key)
        cat_info = SOURCES[cat_key]
        for item in items:
            item['category'] = cat_key
            item['color_class'] = cat_info['color_class']
            item['badge_class'] = cat_info['badge_class']
        all_articles.extend(items)

# Filter by age
cutoff = datetime.now(timezone.utc).timestamp() - max_age_hours * 3600
all_articles = [a for a in all_articles if a['time'].timestamp() > cutoff]

# Filter by keyword
if keyword.strip():
    kw = keyword.strip().lower()
    all_articles = [a for a in all_articles if kw in a['title'].lower()]

# Sort
if sort_by == "Newest first":
    all_articles.sort(key=lambda x: x['time'], reverse=True)
else:
    all_articles.sort(key=lambda x: (x['category'], x['time'].timestamp() * -1))

# ── STATS ROW ─────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f'''
    <div class="stat-box">
        <div class="stat-number">{len(all_articles)}</div>
        <div class="stat-label">Articles</div>
    </div>''', unsafe_allow_html=True)

with col2:
    unique_sources = len(set(a['source'] for a in all_articles))
    st.markdown(f'''
    <div class="stat-box">
        <div class="stat-number">{unique_sources}</div>
        <div class="stat-label">Sources active</div>
    </div>''', unsafe_allow_html=True)

with col3:
    st.markdown(f'''
    <div class="stat-box">
        <div class="stat-number">{len(selected_cats)}</div>
        <div class="stat-label">Categories</div>
    </div>''', unsafe_allow_html=True)

with col4:
    newest = min((datetime.now(timezone.utc) - a['time']).total_seconds() for a in all_articles) if all_articles else 0
    newest_str = f"{int(newest//60)}m" if newest < 3600 else f"{int(newest//3600)}h"
    st.markdown(f'''
    <div class="stat-box">
        <div class="stat-number">{newest_str}</div>
        <div class="stat-label">Latest item</div>
    </div>''', unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── ARTICLES ──────────────────────────────────────────────────────────────────
if not all_articles:
    st.markdown('<div class="empty-state">No articles found.<br>Try expanding the time range or adding more categories.</div>', unsafe_allow_html=True)
else:
    if sort_by == "By category":
        for cat_key in selected_cats:
            cat_articles = [a for a in all_articles if a['category'] == cat_key]
            if not cat_articles:
                continue
            st.markdown(f'<div class="section-label">{cat_key} — {len(cat_articles)} items</div>', unsafe_allow_html=True)
            for art in cat_articles:
                st.markdown(f'''
                <div class="news-card card-{art["color_class"]}">
                    <div class="card-title"><a href="{art["link"]}" target="_blank">{art["title"]}</a></div>
                    <div class="card-meta">
                        <span class="badge {art["badge_class"]}">{art["category"].split()[-1]}</span>
                        <span class="meta-source">{art["source"]}</span>
                        <span class="meta-time">{time_ago(art["time"])}</span>
                    </div>
                </div>''', unsafe_allow_html=True)
            st.markdown('<hr class="divider">', unsafe_allow_html=True)
    else:
        for art in all_articles:
            st.markdown(f'''
            <div class="news-card card-{art["color_class"]}">
                <div class="card-title"><a href="{art["link"]}" target="_blank">{art["title"]}</a></div>
                <div class="card-meta">
                    <span class="badge {art["badge_class"]}">{art["category"].split()[-1]}</span>
                    <span class="meta-source">{art["source"]}</span>
                    <span class="meta-time">{time_ago(art["time"])}</span>
                </div>
            </div>''', unsafe_allow_html=True)
