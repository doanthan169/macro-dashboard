import streamlit as st
import feedparser
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import re

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

html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
.stApp { background-color: #0d1117; color: #e6edf3; }

section[data-testid="stSidebar"] {
    background-color: #161b22;
    border-right: 1px solid #21262d;
}
section[data-testid="stSidebar"] * { color: #e6edf3 !important; }

.main-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.6rem; font-weight: 500;
    color: #58a6ff; letter-spacing: -0.02em;
    margin-bottom: 0; padding-bottom: 0;
}
.sub-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem; color: #8b949e;
    letter-spacing: 0.08em; margin-top: 2px; margin-bottom: 24px;
}
.stat-box {
    background: #161b22; border: 1px solid #21262d;
    border-radius: 8px; padding: 16px 20px; text-align: center;
}
.stat-number {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2rem; font-weight: 500; color: #58a6ff; line-height: 1;
}
.stat-label {
    font-size: 0.72rem; color: #8b949e;
    letter-spacing: 0.06em; text-transform: uppercase; margin-top: 4px;
}
.news-card {
    background: #161b22; border: 1px solid #21262d;
    border-left: 3px solid #21262d; border-radius: 8px;
    padding: 14px 18px; margin-bottom: 10px;
}
.card-us       { border-left-color: #3b82f6 !important; }
.card-china    { border-left-color: #ef4444 !important; }
.card-vietnam  { border-left-color: #22c55e !important; }
.card-geo      { border-left-color: #ec4899 !important; }
.card-agri     { border-left-color: #f59e0b !important; }
.card-energy   { border-left-color: #f97316 !important; }
.card-metals   { border-left-color: #a855f7 !important; }
.card-precious { border-left-color: #eab308 !important; }
.card-coffee   { border-left-color: #92400e !important; }

.card-title {
    font-size: 0.92rem; font-weight: 500;
    color: #e6edf3; line-height: 1.4; margin-bottom: 8px;
}
.card-title a { color: #e6edf3; text-decoration: none; }
.card-title a:hover { color: #58a6ff; }
.card-meta { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }

.badge {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem; font-weight: 500;
    padding: 2px 8px; border-radius: 4px;
    letter-spacing: 0.04em; text-transform: uppercase;
}
.badge-us       { background: #1d3a6e; color: #93c5fd; }
.badge-china    { background: #4c1d1d; color: #fca5a5; }
.badge-vietnam  { background: #14532d; color: #86efac; }
.badge-geo      { background: #500724; color: #f9a8d4; }
.badge-agri     { background: #451a03; color: #fcd34d; }
.badge-energy   { background: #431407; color: #fdba74; }
.badge-metals   { background: #3b0764; color: #d8b4fe; }
.badge-precious { background: #422006; color: #fde68a; }
.badge-coffee   { background: #292524; color: #d6b896; }

.meta-source { font-size: 0.72rem; color: #8b949e; font-family: 'IBM Plex Mono', monospace; }
.meta-time   { font-size: 0.72rem; color: #6e7681;  font-family: 'IBM Plex Mono', monospace; }
.divider     { border: none; border-top: 1px solid #21262d; margin: 20px 0; }
.section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem; color: #8b949e;
    letter-spacing: 0.1em; text-transform: uppercase;
    margin-bottom: 12px; margin-top: 20px;
}
.empty-state {
    text-align: center; padding: 60px 20px;
    color: #8b949e; font-family: 'IBM Plex Mono', monospace; font-size: 0.85rem;
}
.refresh-info { font-family: 'IBM Plex Mono', monospace; font-size: 0.68rem; color: #6e7681; }
.stButton button {
    background: #21262d !important; color: #e6edf3 !important;
    border: 1px solid #30363d !important; border-radius: 6px !important;
    font-family: 'IBM Plex Mono', monospace !important; font-size: 0.78rem !important;
}
.stButton button:hover { background: #30363d !important; border-color: #58a6ff !important; }
div[data-testid="stTextInput"] input {
    background: #161b22 !important; border: 1px solid #30363d !important;
    color: #e6edf3 !important; border-radius: 6px !important;
}
div[data-testid="stCheckbox"] label { color: #e6edf3 !important; font-size: 0.85rem !important; }
h1, h2, h3 { color: #e6edf3 !important; }
.stMarkdown p { color: #c9d1d9; }
</style>
""", unsafe_allow_html=True)

# ── RSS SOURCES — full 58-source master list ──────────────────────────────────
#
# TO ADD A NEW FEED: copy any {"name": ..., "url": ...} line inside the right
# category and replace name + url. That's it — no other changes needed.
#
SOURCES = {

    # ── MODULE A: VN FUND MANAGEMENT ─────────────────────────────────────────

    "🇺🇸 US Macro": {
        "module": "A",
        "color_class": "us", "badge_class": "badge-us",
        "feeds": [
            {"name": "Federal Reserve",  "url": "https://www.federalreserve.gov/feeds/press_all.xml"},
            {"name": "BLS",              "url": "https://www.bls.gov/feed/ber.rss"},
            {"name": "EIA",              "url": "https://www.eia.gov/rss/press_room.xml"},
            {"name": "US Treasury",      "url": "https://home.treasury.gov/news/press-releases/rss.xml"},
            {"name": "CME Group",        "url": "https://www.cmegroup.com/rss/cme-group-news.xml"},
            {"name": "USDA",             "url": "https://www.usda.gov/rss20.xml"},
            {"name": "MarketWatch",      "url": "https://feeds.marketwatch.com/marketwatch/realtimeheadlines/"},
        ]
    },

    "🇨🇳 China Macro": {
        "module": "A",
        "color_class": "china", "badge_class": "badge-china",
        "feeds": [
            {"name": "Reuters China",    "url": "https://feeds.reuters.com/reuters/CNTopNews"},
            {"name": "SCMP",             "url": "https://www.scmp.com/rss/5/feed"},
            {"name": "Nikkei Asia",      "url": "https://asia.nikkei.com/rss/feed/nar"},
            {"name": "Xinhua Finance",   "url": "https://english.news.cn/rss/finance.xml"},
            {"name": "Caixin Global",    "url": "https://www.caixinglobal.com/rss/economy.xml"},
        ]
    },

    "🇻🇳 Vietnam": {
        "module": "A",
        "color_class": "vietnam", "badge_class": "badge-vietnam",
        "feeds": [
            {"name": "CafeF Markets",        "url": "https://cafef.vn/rss/thi-truong-chung-khoan.rss"},
            {"name": "VnExpress Economy",    "url": "https://vnexpress.net/rss/kinh-doanh.rss"},
            {"name": "VnExpress Finance",    "url": "https://vnexpress.net/rss/kinh-doanh/tai-chinh.rss"},
            {"name": "Vietnam Invest Review","url": "https://vir.com.vn/rss/finance-banking.rss"},
            {"name": "MoF Vietnam",          "url": "https://www.mof.gov.vn/webcenter/feed/rss"},
            {"name": "HOSE",                 "url": "https://www.hsx.vn/Modules/Cms/Web/NewsRSS.aspx"},
        ]
    },

    "🌐 Geopolitics": {
        "module": "A",
        "color_class": "geo", "badge_class": "badge-geo",
        "feeds": [
            {"name": "Reuters Top News",     "url": "https://feeds.reuters.com/reuters/topNews"},
            {"name": "Financial Times",      "url": "https://www.ft.com/rss/home/uk"},
            {"name": "Nikkei Asia Global",   "url": "https://asia.nikkei.com/rss/feed/china"},
            {"name": "AP Economics",         "url": "https://rsshub.app/apnews/topics/economy"},
            {"name": "Politico Economy",     "url": "https://rss.politico.com/economy.xml"},
            {"name": "Watcher.Guru",         "url": "https://watcher.guru/news/feed"},
            {"name": "Bloomberg Markets",    "url": "https://feeds.bloomberg.com/markets/news.rss"},
            {"name": "The Economist",        "url": "https://www.economist.com/finance-and-economics/rss.xml"},
            {"name": "Kobeissi Letter",      "url": "https://thekobeissiletter.substack.com/feed"},
            {"name": "Unusual Whales",       "url": "https://unusualwhales.com/rss/news"},
        ]
    },

    # ── MODULE B: COMMODITY MARKETS ───────────────────────────────────────────

    "🌾 Agriculture": {
        "module": "B",
        "color_class": "agri", "badge_class": "badge-agri",
        "feeds": [
            {"name": "USDA",             "url": "https://www.usda.gov/rss20.xml"},
            {"name": "AgriMoney",        "url": "https://www.agrimoney.com/feed/"},
            {"name": "IGC Grains",       "url": "https://www.igc.int/en/news/newslist.aspx"},
            {"name": "CONAB Brazil",     "url": "https://www.conab.gov.br/info-agro/analises-do-mercado-agropecuario-e-extrativista/analises-do-mercado/rss-historico"},
            {"name": "Bolsa Rosario AR", "url": "https://www.bcr.com.ar/es/rss.xml"},
            {"name": "Ukraine Grain",    "url": "https://uga.ua/en/rss/"},
        ]
    },

    "🛢️ Energy": {
        "module": "B",
        "color_class": "energy", "badge_class": "badge-energy",
        "feeds": [
            {"name": "EIA Petroleum",    "url": "https://www.eia.gov/rss/press_room.xml"},
            {"name": "Reuters Energy",   "url": "https://feeds.reuters.com/reuters/energy"},
            {"name": "Rigzone",          "url": "https://www.rigzone.com/news/rss/rigzone_latest.aspx"},
            {"name": "S&P Commodity",    "url": "https://www.spglobal.com/commodityinsights/en/rss-feed/oil"},
        ]
    },

    "⚙️ Base Metals": {
        "module": "B",
        "color_class": "metals", "badge_class": "badge-metals",
        "feeds": [
            {"name": "LME",              "url": "https://www.lme.com/en/news-and-insights/news/rss"},
            {"name": "Reuters Metals",   "url": "https://feeds.reuters.com/reuters/basicMaterialsSector"},
            {"name": "Mining.com",       "url": "https://www.mining.com/feed/"},
            {"name": "Fastmarkets",      "url": "https://www.fastmarkets.com/insights/rss/"},
            {"name": "Cochilco Chile",   "url": "https://www.cochilco.cl/Paginas/english.aspx"},
        ]
    },

    "🥇 Precious Metals": {
        "module": "B",
        "color_class": "precious", "badge_class": "badge-precious",
        "feeds": [
            {"name": "World Gold Council","url": "https://www.gold.org/goldhub/research/rss"},
            {"name": "Reuters Metals",   "url": "https://feeds.reuters.com/reuters/basicMaterialsSector"},
            {"name": "Mining.com",       "url": "https://www.mining.com/feed/"},
        ]
    },

    "☕ Coffee": {
        "module": "B",
        "color_class": "coffee", "badge_class": "badge-coffee",
        "feeds": [
            {"name": "ICO",              "url": "https://icocoffee.org/news/feed/"},
            {"name": "Brazil CECAFE",    "url": "https://www.cecafe.com.br/en/feed/"},
            {"name": "Colombia FNC",     "url": "https://federaciondecafeteros.org/wp/feed/"},
            {"name": "Reuters Softs",    "url": "https://feeds.reuters.com/reuters/ConsumerProductsSector"},
        ]
    },

}

MODULE_A = [k for k, v in SOURCES.items() if v["module"] == "A"]
MODULE_B = [k for k, v in SOURCES.items() if v["module"] == "B"]

# ── HELPERS ───────────────────────────────────────────────────────────────────
def clean_html(text):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    for ent, rep in [('&amp;','&'),('&lt;','<'),('&gt;','>'),('&quot;','"'),('&#39;',"'")]:
        text = text.replace(ent, rep)
    return re.sub(r'\s+', ' ', text).strip()

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
    secs = int((datetime.now(timezone.utc) - dt).total_seconds())
    if secs < 60:    return f"{secs}s ago"
    if secs < 3600:  return f"{secs//60}m ago"
    if secs < 86400: return f"{secs//3600}h ago"
    return f"{secs//86400}d ago"

@st.cache_data(ttl=900, show_spinner=False)
def fetch_feed(url, source_name):
    try:
        feed = feedparser.parse(url, request_headers={
            'User-Agent': 'Mozilla/5.0 (compatible; MacroBot/1.0)'
        })
        items = []
        for entry in feed.entries[:15]:
            title = clean_html(getattr(entry, 'title', ''))
            link  = getattr(entry, 'link', '#')
            if not title:
                continue
            items.append({
                'title':  title,
                'link':   link,
                'source': source_name,
                'time':   parse_time(entry),
            })
        return items
    except Exception:
        return []

def fetch_category(cat_key):
    items = []
    for f in SOURCES[cat_key]['feeds']:
        items.extend(fetch_feed(f['url'], f['name']))
    items.sort(key=lambda x: x['time'], reverse=True)
    return items

def render_card(art):
    label = art['category'].split(' ', 1)[-1]
    st.markdown(f'''
    <div class="news-card card-{art["color_class"]}">
        <div class="card-title"><a href="{art["link"]}" target="_blank">{art["title"]}</a></div>
        <div class="card-meta">
            <span class="badge {art["badge_class"]}">{label}</span>
            <span class="meta-source">{art["source"]}</span>
            <span class="meta-time">{time_ago(art["time"])}</span>
        </div>
    </div>''', unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📡 Macro Intelligence")
    st.markdown('<div class="refresh-info">Real-time RSS · 58 sources · 9 categories</div>',
                unsafe_allow_html=True)
    st.markdown("---")

    selected_cats = []

    st.markdown("**Module A — VN Fund Management**")
    for cat_key in MODULE_A:
        if st.checkbox(cat_key, value=True, key=f"cat_{cat_key}"):
            selected_cats.append(cat_key)

    st.markdown("")
    st.markdown("**Module B — Commodity Markets**")
    for cat_key in MODULE_B:
        if st.checkbox(cat_key, value=True, key=f"cat_{cat_key}"):
            selected_cats.append(cat_key)

    st.markdown("---")
    st.markdown("**Filters**")
    keyword       = st.text_input("🔍 Keyword", placeholder="tariff, rate, gold, coffee...")
    max_age_hours = st.slider("Max age (hours)", 1, 168, 48)

    st.markdown("---")
    sort_by = st.radio("**Sort by**", ["Newest first", "By category"])

    st.markdown("---")
    if st.button("🔄 Refresh all feeds", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    vn_time = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
    st.markdown(
        f'<div class="refresh-info">🕐 {vn_time.strftime("%d %b %Y, %H:%M")} ICT'
        f'<br>Cache: 15 min</div>',
        unsafe_allow_html=True
    )

# ── MAIN ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-header">MACRO INTELLIGENCE</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">'
    'VIETNAM FUND MANAGEMENT · COMMODITY MARKETS · REAL-TIME RSS AGGREGATOR'
    '</div>',
    unsafe_allow_html=True
)

if not selected_cats:
    st.markdown(
        '<div class="empty-state">No categories selected.<br>'
        'Enable at least one in the sidebar.</div>',
        unsafe_allow_html=True
    )
    st.stop()

# Fetch all
with st.spinner("Fetching feeds..."):
    all_articles = []
    for cat_key in selected_cats:
        cat_info = SOURCES[cat_key]
        for item in fetch_category(cat_key):
            item['category']    = cat_key
            item['color_class'] = cat_info['color_class']
            item['badge_class'] = cat_info['badge_class']
            item['module']      = cat_info['module']
            all_articles.append(item)

# Filters
cutoff       = datetime.now(timezone.utc).timestamp() - max_age_hours * 3600
all_articles = [a for a in all_articles if a['time'].timestamp() > cutoff]
if keyword.strip():
    kw           = keyword.strip().lower()
    all_articles = [a for a in all_articles if kw in a['title'].lower()]

# Sort
if sort_by == "Newest first":
    all_articles.sort(key=lambda x: x['time'], reverse=True)
else:
    all_articles.sort(key=lambda x: (x['category'], -x['time'].timestamp()))

# ── STATS ─────────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
mod_a_count = sum(1 for a in all_articles if a['module'] == 'A')
mod_b_count = sum(1 for a in all_articles if a['module'] == 'B')

for col, (num, label) in zip(
    [c1, c2, c3, c4, c5],
    [
        (len(all_articles),                             "Total articles"),
        (len(set(a['source'] for a in all_articles)),   "Sources active"),
        (len(selected_cats),                            "Categories on"),
        (mod_a_count,                                   "Mod A — VN fund"),
        (mod_b_count,                                   "Mod B — Commodity"),
    ]
):
    with col:
        st.markdown(
            f'<div class="stat-box">'
            f'<div class="stat-number">{num}</div>'
            f'<div class="stat-label">{label}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── FEED ─────────────────────────────────────────────────────────────────────
if not all_articles:
    st.markdown(
        '<div class="empty-state">No articles found.<br>'
        'Try expanding the time range or selecting more categories.</div>',
        unsafe_allow_html=True
    )
elif sort_by == "By category":
    for cat_key in selected_cats:
        cat_articles = [a for a in all_articles if a['category'] == cat_key]
        if not cat_articles:
            continue
        st.markdown(
            f'<div class="section-label">{cat_key} — {len(cat_articles)} items</div>',
            unsafe_allow_html=True
        )
        for art in cat_articles:
            render_card(art)
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
else:
    for art in all_articles:
        render_card(art)
