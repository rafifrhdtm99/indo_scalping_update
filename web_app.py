import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
import ta
import json
import os
from datetime import datetime, timedelta
import pytz
import urllib.request
import urllib.parse

# ─────────────────────────────────────────────────────────────────────────────
# KONFIGURASI
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Scalping IHSG by Rafif",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

WIB          = pytz.timezone("Asia/Jakarta")
FEE_BELI     = 0.0010
FEE_JUAL     = 0.0020
HISTORY_FILE = os.path.join(os.path.dirname(__file__), "signal_history.json")
ALERTS_FILE  = os.path.join(os.path.dirname(__file__), "telegram_alerts.json")

# Telegram Bot configuration (Hardcoded & Hidden from UI)
TG_TOKEN     = "8989322838:AAHdCXYAM-jR3NYX2Y3kt5hmqpMm3UINBMo"
TG_CHAT_ID   = "6905606117"
ENABLE_TG    = True

# ── ALL_SAHAM — Watchlist Gabungan Emiten IHSG (505 Saham) ────────────────────
ALL_SAHAM = [
    # === A - B ===
    "AALI", "ABMM", "ACES", "ACST", "ADCP", "ADES", "ADHI", "ADMF", "ADMR", "ADRO",
    "AGII", "AGRO", "AGRS", "AIMS", "AISA", "AKRA", "ALAS", "ALKA", "ALTO", "AMAR",
    "AMMN", "AMRT", "ANDI", "ANTM", "APEX", "APIC", "APLI", "APLN", "ARCI", "ARKA",
    "ARTO", "ASBI", "ASGR", "ASII", "ASJT", "ASMI", "ASPI", "ASRI", "ASSA", "ATIC",
    "AUTO", "AVIA", "AWAN", "AXIO", "AYAM", "BABP", "BACA", "BAJA", "BALI", "BANK",
    "BAPA", "BATA", "BAYU", "BBCA", "BBHI", "BBKP", "BBLD", "BBRI", "BBTN", "BBYB",
    "BCAP", "BCIC", "BCIP", "BDMN", "BEBS", "BELI", "BESS", "BEST", "BFIN", "BGTG",
    "BHIT", "BIKA", "BINA", "BIPI", "BIPP", "BIRD", "BISI", "BJBR", "BJTM", "BKDP",
    "BKSL", "BMAS", "BMHS", "BMRI", "BMTR", "BNBR", "BNGA", "BNII", "BNLI", "BOLA",
    "BOLT", "BPFI", "BPII", "BPTR", "BRAM", "BREN", "BRMS", "BRPT", "BSDE", "BSIM",
    "BSML", "BTEK", "BTEL", "BTON", "BTPN", "BTPS", "BUDI", "BUKA", "BUKK", "BULL",
    "BUMI", "BWPT", "BYAN",
    # === C - F ===
    "CAMP", "CARE", "CARS", "CASA", "CASS", "CEKA", "CENT", "CFIN", "CINT", "CITA",
    "CLAY", "CLEO", "CMNP", "CNTX", "COAL", "COCO", "CPIN", "CPRO", "CSAP", "CSIS",
    "CTBN", "CTRA", "CTTH", "CUAN", "DART", "DEFI", "DEWA", "DFAM", "DGIK", "DGNS",
    "DILD", "DIVA", "DKFT", "DLTA", "DMAS", "DMMX", "DMND", "DNAR", "DNET", "DOID",
    "DPNS", "DPUM", "DRMA", "DSFI", "DSNG", "DUTI", "DVLA", "DYAN", "EAST", "EDGE",
    "EKAD", "ELSA", "ELTY", "EMTK", "ENRG", "ENVY", "ERAA", "ERTX", "ESIP", "ESSA",
    "ESTI", "ETWA", "EXCL", "FAST", "FILM", "FMII", "FORZ", "FREN",
    # === G - K ===
    "GDST", "GDYR", "GEMA", "GEMS", "GGRM", "GIAA", "GJTL", "GLOB", "GMFI", "GMTD",
    "GOLD", "GOOD", "GOTO", "GPRA", "GSMF", "GTBO", "GWSA", "HAIS", "HDFA", "HDIT",
    "HEAL", "HELI", "HERO", "HEXA", "HITS", "HMSP", "HOKI", "HOMI", "HOPE", "HOTL",
    "HRTA", "HRUM", "IATA", "IBST", "ICBP", "IKAN", "IKBI", "IMAS", "IMJS", "INAF",
    "INCF", "INCI", "INCO", "INDF", "INDS", "INDX", "INDY", "INKP", "INPC", "INPS",
    "INRU", "INTP", "IPCC", "IPCM", "IPOL", "IPTV", "IRRA", "ISAP", "ISAT", "ISSP",
    "ITMA", "ITMG", "JAWA", "JECC", "JIHD", "JKON", "JPFA", "JRPT", "JSMR", "JSPT",
    "JTPE", "KAEF", "KARW", "KAYU", "KBLI", "KBLM", "KBRI", "KDSI", "KEEN", "KEJU",
    "KIAS", "KIJA", "KIOS", "KKGI", "KLBF", "KMTR", "KOBX", "KOIN", "KOTA", "KPIG",
    "KRAH", "KRAS", "KREN",
    # === L - R ===
    "LINK", "LION", "LMAS", "LPCK", "LPKR", "LPLI", "LPPF", "LRNA", "LSIP", "LTLS",
    "LUCK", "MAIN", "MAMI", "MAPA", "MAPB", "MAPI", "MARI", "MARK", "MASB", "MAYA",
    "MBAP", "MBMA", "MBSS", "MCAS", "MCOR", "MDKA", "MDKI", "MDLN", "MEDC", "MEGA",
    "MERK", "META", "MFIN", "MFMI", "MGRO", "MIDI", "MIKA", "MITI", "MKPI", "MNCN",
    "MPPA", "MSIN", "MSKY", "MTDL", "MTFN", "MTLA", "MTPS", "MTSM", "MYOR", "MYRX",
    "MYTX", "NASA", "NELI", "NFCX", "NICL", "NIKL", "NIPS", "NISP", "NOBU", "NRCA",
    "NZIA", "OASA", "OKAS", "OMED", "OMRE", "PADI", "PALM", "PANI", "PANR", "PANS",
    "PBID", "PCAR", "PDES", "PEGE", "PEHA", "PGAS", "PGEO", "PGLI", "PICO", "PJAA",
    "PLIN", "PMMP", "PNBN", "PNBS", "PNIN", "PNLF", "PNSE", "POLA", "POLI", "PORT",
    "POWR", "PPRE", "PPRO", "PRAS", "PRDA", "PSAB", "PSDN", "PSSI", "PTBA", "PTDU",
    "PTIS", "PTPP", "PTRO", "PTSN", "PTSP", "PUDP", "PWON", "PYFA", "PZZA", "RALS",
    "RAMA", "RANC", "RATU", "RBMS", "RDTX", "RELI", "RICY", "RIGS", "RISE", "RMKE",
    "RODA", "ROTI", "RUIS",
    # === S - Z ===
    "SAFE", "SAME", "SAMF", "SCCO", "SCMA", "SCPI", "SDMU", "SDPC", "SDRA", "SGER",
    "SGRO", "SHID", "SHIP", "SIDO", "SILO", "SIMP", "SIPD", "SKYB", "SLIS", "SMBR",
    "SMCB", "SMDM", "SMDR", "SMGR", "SMKL", "SMMT", "SMRA", "SMSM", "SOCI", "SOHO",
    "SONA", "SPTO", "SRAJ", "SRIL", "SRTG", "SSIA", "SSMS", "SSTM", "SULI", "SUPR",
    "TALF", "TAPG", "TAXI", "TBIG", "TBLA", "TBMS", "TCPI", "TEBE", "TELE", "TFAS",
    "TFCO", "TGRA", "TIFA", "TINS", "TIRT", "TKIM", "TLKM", "TMAS", "TMPO", "TOBA",
    "TOTL", "TOWR", "TPIA", "TPMA", "TRIL", "TRIM", "TRIN", "TRIS", "TRJA", "TRST",
    "TRUK", "TSPC", "TURI", "UCID", "ULTJ", "UNIC", "UNSP", "UNTR", "UNVR", "URBN",
    "VALE", "VICO", "VRNA", "WAHA", "WEGE", "WEHA", "WICO", "WIFI", "WIIM", "WIKA",
    "WINS", "WIPO", "WOMF", "WOOD", "WOWS", "WSBP", "WSKT", "WTON", "YPAS", "YULE",
    "ZBRA"
]
# Hapus duplikat, jaga urutan
_seen = set()
ALL_SAHAM = [x for x in ALL_SAHAM if not (x in _seen or _seen.add(x))]

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.main-header {
    background: linear-gradient(135deg, #0a0a1a 0%, #1a1040 50%, #0d1b2a 100%);
    border: 1px solid rgba(139,92,246,0.3);
    border-radius: 20px; padding: 30px 40px; margin-bottom: 0px;
    text-align: center; box-shadow: 0 8px 40px rgba(139,92,246,0.15);
}
.main-header h1 {
    color: #fff; font-size: 2.4rem; font-weight: 900; margin: 0;
    background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.main-header p { color: #94a3b8; font-size: 0.9rem; margin: 8px 0 0 0; }

.pasar-buka    { background: linear-gradient(90deg,#064e3b,#065f46); border-left: 4px solid #10b981; border-radius: 10px; padding: 12px 20px; color: #d1fae5; font-weight: 700; margin: 12px 0; }
.pasar-tutup   { background: linear-gradient(90deg,#18181b,#27272a); border-left: 4px solid #52525b; border-radius: 10px; padding: 12px 20px; color: #a1a1aa; font-weight: 700; margin: 12px 0; }
.pasar-preopen { background: linear-gradient(90deg,#1e3a5f,#1e40af); border-left: 4px solid #60a5fa; border-radius: 10px; padding: 12px 20px; color: #bfdbfe; font-weight: 700; margin: 12px 0; }

.card-beli   { background: linear-gradient(135deg,#052e16 0%,#14532d 100%); border: 2px solid #22c55e; border-radius: 18px; padding: 20px; margin-bottom: 6px; }
.card-jual   { background: linear-gradient(135deg,#450a0a 0%,#7f1d1d 100%); border: 2px solid #ef4444; border-radius: 18px; padding: 20px; margin-bottom: 6px; }
.card-tunggu { background: linear-gradient(135deg,#111827 0%,#1f2937 100%); border: 1.5px solid #374151; border-radius: 18px; padding: 20px; margin-bottom: 6px; }
.card-bsjp   { background: linear-gradient(135deg,#1e1b4b 0%,#312e81 100%); border: 2px solid #818cf8; border-radius: 18px; padding: 20px; margin-bottom: 6px; }

.card-sym   { font-size: 1.3rem; font-weight: 900; color: #fff; }
.card-price { font-size: 2rem; font-weight: 900; color: #fff; margin: 4px 0 2px 0; }

.tag-green  { background: linear-gradient(90deg,#16a34a,#15803d); color:#fff; border-radius:8px; padding:4px 12px; font-size:0.75rem; font-weight:800; letter-spacing:0.5px; }
.tag-red    { background: linear-gradient(90deg,#dc2626,#b91c1c); color:#fff; border-radius:8px; padding:4px 12px; font-size:0.75rem; font-weight:800; }
.tag-gray   { background: linear-gradient(90deg,#374151,#4b5563); color:#e5e7eb; border-radius:8px; padding:4px 12px; font-size:0.75rem; font-weight:700; }
.tag-purple { background: linear-gradient(90deg,#6d28d9,#7c3aed); color:#fff; border-radius:8px; padding:4px 12px; font-size:0.75rem; font-weight:800; }

.ind-pill {
    display:inline-block; border-radius:20px; padding:3px 11px;
    font-size:0.76rem; margin: 3px 3px 3px 0;
    background:rgba(255,255,255,0.07); color:#cbd5e1;
}
.kalkulator {
    background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px; padding: 14px 16px; margin-top: 12px;
    font-size: 0.84rem; color: #e2e8f0; line-height: 1.8;
}
.kalkulator b { color: #fff; }
.section-header {
    font-size: 1.2rem; font-weight: 800; color: #fff;
    margin: 20px 0 12px 0; padding-left: 4px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TRADINGVIEW WIDGET BUILDERS
# ─────────────────────────────────────────────────────────────────────────────
def tv_ticker_tape(symbols_list):
    syms_js = ",\n".join([
        f'{{"proName":"IDX:{s}","title":"{s}"}}'
        for s in symbols_list
    ])
    return f"""
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript"
        src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
      {{
        "symbols": [
          {{"proName": "FOREXCOM:SPXUSD", "title": "S&P 500"}},
          {{"proName": "IDX:COMPOSITE", "title": "IHSG"}},
          {syms_js}
        ],
        "showSymbolLogo": true,
        "isTransparent": false,
        "displayMode": "adaptive",
        "colorTheme": "dark",
        "locale": "id"
      }}
      </script>
    </div>
    """

def tv_technical_analysis(symbol, interval="1D", height=380):
    mapping = {
        "1": "1m",
        "5": "5m",
        "15": "15m",
        "30": "30m",
        "60": "1h",
        "1D": "1D",
        "1W": "1W"
    }
    tv_int = mapping.get(interval, "1D")
    
    return f"""
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript"
        src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
      {{
        "interval": "{tv_int}",
        "width": "100%",
        "isTransparent": true,
        "height": {height},
        "symbol": "IDX:{symbol}",
        "showIntervalTabs": true,
        "displayMode": "multiple",
        "locale": "id",
        "colorTheme": "dark"
      }}
      </script>
    </div>
    """

def tv_advanced_chart(symbol, interval="1D", height=400):
    tv_int = interval
    if interval == "1D": tv_int = "D"
    elif interval == "1W": tv_int = "W"
    
    return f"""
    <div class="tradingview-widget-container" style="height:{height}px;">
      <div id="tv_chart_{symbol}" style="height:{height}px;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "width": "100%",
        "height": {height},
        "symbol": "IDX:{symbol}",
        "interval": "{tv_int}",
        "timezone": "Asia/Jakarta",
        "theme": "dark",
        "style": "1",
        "locale": "id",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "hide_side_toolbar": false,
        "allow_symbol_change": true,
        "container_id": "tv_chart_{symbol}"
      }});
      </script>
    </div>
    """

# ─────────────────────────────────────────────────────────────────────────────
# FUNGSI UTILITAS
# ─────────────────────────────────────────────────────────────────────────────
def get_status_pasar():
    now = datetime.now(WIB)
    if now.weekday() >= 5:
        return "tutup", "🔴 Bursa Tutup — Weekend (Senin buka 09:00 WIB)"
    h, m = now.hour, now.minute
    t = (h, m)
    if   t < (8, 55):              return "tutup",   "🔴 Bursa Belum Buka — Sesi 1 mulai 09:00 WIB"
    elif t < (9,  0):              return "preopen", "🔵 Pre-Opening — Bursa buka dalam hitungan menit! ⚡"
    elif (9,0)  <= t < (11,30):   return "buka",    "🟢 SESI 1 BUKA (09:00 – 11:30 WIB)"
    elif (11,30)<= t < (13,30):   return "tutup",   "🟡 Istirahat Siang (11:30 – 13:30 WIB)"
    elif (13,30)<= t < (15,50):   return "buka",    "🟢 SESI 2 BUKA (13:30 – 15:50 WIB)"
    else:                          return "tutup",   "🔴 Bursa Sudah Tutup — Buka besok 09:00 WIB"

def snap_fraksi(h):
    if h < 200:    return round(h)
    elif h < 500:  return round(h/2)*2
    elif h < 2000: return round(h/5)*5
    elif h < 5000: return round(h/25)*25
    else:          return round(h/50)*50

def get_ara_limit(price):
    if price < 50:
        return 10.0  # Papan Akselerasi / FCA
    elif price <= 200:
        return 35.0
    elif price <= 5000:
        return 25.0
    else:
        return 20.0

# ─────────────────────────────────────────────────────────────────────────────
# SIGNAL HISTORY — Simpan, Load, Evaluasi
# ─────────────────────────────────────────────────────────────────────────────
def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_history(history):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def record_signals(results, modal_per_saham, target_pct, sl_pct):
    history   = load_history()
    now       = datetime.now(WIB)
    scan_time = now.strftime("%Y-%m-%d %H:%M")
    scan_date = now.strftime("%Y-%m-%d")
    existing_keys = {(e["scan_date"], e["symbol"]) for e in history}
    new_count = 0
    for r in results:
        if r["sinyal"] == "TUNGGU":
            continue
        key = (scan_date, r["symbol"])
        if key in existing_keys:
            continue
        k = r["k"]
        entry = {
            "scan_date":      scan_date,
            "scan_time":      scan_time,
            "symbol":         r["symbol"],
            "sinyal":         r["sinyal"],
            "harga_signal":   round(r["harga"], 0),
            "confidence":     r["confidence"],
            "conf_label":     r["conf_label"],
            "rsi":            round(r["ind"].get("RSI", 0), 1),
            "ema_bullish":    r["ind"].get("EMA9", 0) > r["ind"].get("EMA21", 0),
            "macd_pos":       r["ind"].get("MACD_hist", 0) > 0,
            "target_harga":   snap_fraksi(k["ht"]) if k else None,
            "sl_harga":       snap_fraksi(k["hsl"]) if k else None,
            "target_pct":     target_pct,
            "sl_pct":         sl_pct,
            "lot":            r["lot"],
            "modal":          round(k["modal"]) if k else 0,
            "harga_close":    None,
            "return_pct":     None,
            "outcome":        None,
            "est_profit_rp":  None,
        }
        history.append(entry)
        existing_keys.add(key)
        new_count += 1
    save_history(history)
    return new_count

def evaluate_history():
    history = load_history()
    changed = 0
    today   = datetime.now(WIB).strftime("%Y-%m-%d")
    for entry in history:
        if entry.get("outcome") is not None:
            continue
        if entry["scan_date"] == today:
            continue
        sym = entry["symbol"]
        try:
            df = yf.download(f"{sym}.JK", period="5d", interval="1d",
                             auto_adjust=True, progress=False)
            if df.empty:
                continue
            df.index = pd.to_datetime(df.index)
            scan_dt  = pd.Timestamp(entry["scan_date"]).tz_localize(None)
            after    = df[df.index.normalize() > scan_dt]
            if after.empty:
                continue
            close_price = float(after["Close"].iloc[0])
            h_signal    = entry["harga_signal"]
            ret         = (close_price - h_signal) / h_signal * 100
            entry["harga_close"] = round(close_price, 0)
            entry["return_pct"]  = round(ret, 2)
            if entry["sinyal"] in ("BELI", "BSJP"):
                if r := entry["return_pct"]:
                    if r >= entry["target_pct"]:
                        outcome = "HIT_TARGET ✅"
                    elif r <= -entry["sl_pct"]:
                        outcome = "HIT_SL ❌"
                    elif r > 0:
                        outcome = "PROFIT 🟡"
                    else:
                        outcome = "LOSS 🔴"
                else:
                    continue
            else:
                outcome = "TURUN ✅" if ret < 0 else "NAIK ❌"
            entry["outcome"]       = outcome
            entry["est_profit_rp"] = round(ret / 100 * entry["modal"]) if entry["modal"] else None
            changed += 1
        except:
            continue
    if changed:
        save_history(history)
    return history, changed

# ─────────────────────────────────────────────────────────────────────────────
# TELEGRAM BOT LOGIC
# ─────────────────────────────────────────────────────────────────────────────
def load_sent_alerts():
    if not os.path.exists(ALERTS_FILE):
        return {}
    try:
        with open(ALERTS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_sent_alerts(alerts):
    try:
        with open(ALERTS_FILE, "w") as f:
            json.dump(alerts, f)
    except:
        pass

def send_telegram_alert(token, chat_id, r, tf, target_pct, sl_pct):
    sym = r["symbol"]
    sinyal = r["sinyal"]
    harga = r["harga"]
    lot = r["lot"]
    k = r["k"]
    confidence = r["confidence"]
    conf_label = r["conf_label"]
    
    sig_emoji = "🟢" if sinyal == "BELI" else "🟣"
    sig_name = "BELI (BPJS)" if sinyal == "BELI" else ("BELI SORE (BSJP V1)" if r.get("bsjp_metrics") else "BELI SORE (BSJP)")
    
    target_price = snap_fraksi(k["ht"]) if k else harga
    sl_price = snap_fraksi(k["hsl"]) if k else harga
    modal = k["modal"] if k else 0
    profit = k["profit"] if k else 0
    rugi = k["rugi"] if k else 0
    
    msg = (
        f"<b>{sig_emoji} SIGNAL ALERT: {sym}</b>\n"
        f"───────────────────\n"
        f"🎯 <b>Sinyal:</b> {sig_name}\n"
        f"⏱️ <b>Timeframe:</b> {tf}\n"
        f"💵 <b>Harga Masuk:</b> Rp {harga:,.0f}\n"
        f"💼 <b>Rekomendasi Lot:</b> {lot} lot\n"
        f"💰 <b>Estimasi Modal:</b> Rp {modal:,.0f}\n"
        f"📊 <b>Confidence:</b> {confidence}% ({conf_label})\n\n"
        f"🎯 <b>Target Jual:</b> Rp {target_price:,.0f} (+{target_pct:.1f}%)\n"
        f"🛑 <b>Stop Loss:</b> Rp {sl_price:,.0f} (-{sl_pct:.1f}%)\n"
        f"✅ <b>Est. Profit:</b> Rp {profit:+,.0f}\n"
        f"❌ <b>Est. Rugi:</b> Rp {rugi:+,.0f}\n"
        f"───────────────────\n"
        f"<i>Jam Scan: {datetime.now(WIB).strftime('%d/%m/%Y %H:%M:%S')} WIB</i>"
    )
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": msg, "parse_mode": "HTML"}).encode("utf-8")
    try:
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=5) as response:
            return True
    except Exception as e:
        return False

# ─────────────────────────────────────────────────────────────────────────────
# FUNGSI ANALISIS & SINYAL
# ─────────────────────────────────────────────────────────────────────────────
def hitung_confidence(ind, harga, sinyal, bsjp_metrics=None, strategi="🟢 BPJS Sesi 1 (Pagi)"):
    if ind is None:
        return 25, "❓ Data kurang", "#6b7280"
    if bsjp_metrics:
        total_criteria = len(bsjp_metrics)
        met_criteria = sum(1 for v in bsjp_metrics.values() if v)
        score = int(met_criteria / total_criteria * 100)
    else:
        score = 25
    score = max(10, min(100, score))
    if   score >= 80: label, color = "🔥 Sangat Kuat",  "#22c55e"
    elif score >= 65: label, color = "💪 Kuat",          "#84cc16"
    elif score >= 50: label, color = "✅ Cukup",          "#f59e0b"
    elif score >= 35: label, color = "⚠️ Lemah",          "#f97316"
    else:             label, color = "❌ Sangat Lemah",   "#ef4444"
    return score, label, color

def buat_analisis_singkat(ind, harga, sinyal, chg, bsjp_metrics=None, strategi="🟢 BPJS Sesi 1 (Pagi)", is_owner=False):
    if ind is None or not ind:
        return "Data historis tidak mencukupi untuk melakukan analisis teknikal."
    if bsjp_metrics:
        total_criteria = len(bsjp_metrics)
        met_criteria = sum(1 for v in bsjp_metrics.values() if v)
        if is_owner:
            met_list = [k for k, v in bsjp_metrics.items() if v]
            unmet_list = [k for k, v in bsjp_metrics.items() if not v]
            if sinyal in ("BELI", "BSJP"):
                return (
                    f"🌟 Saham memenuhi **seluruh kriteria {strategi}**! Kenaikan {chg:.1f}% sehat, "
                    f"kriteria terpenuhi: {', '.join(met_list)}."
                )
            else:
                missing_str = ", ".join(unmet_list)
                return (
                    f"⏳ Belum memenuhi syarat {strategi}. "
                    f"Kriteria terpenuhi: {', '.join(met_list)}. "
                    f"Kriteria kurang: <span style='color:#ef4444;font-weight:bold;'>{missing_str}</span>."
                )
        else:
            # Mode Privat (Public View) - Sembunyikan detail nama kriteria
            if sinyal in ("BELI", "BSJP"):
                return f"🌟 Saham memenuhi **seluruh kriteria analisis** ({met_criteria}/{total_criteria}) untuk strategi yang dipilih. Rekomendasi masuk aktif."
            else:
                return f"⏳ Saham memenuhi **{met_criteria} dari {total_criteria} kriteria** rahasia strategi ini. Menunggu konfirmasi penuh."
    return "Sedang memproses analisis..."

def hitung_lot(modal, harga):
    if harga <= 0: return 0
    return int(modal // (harga * 100))

def kalkulator(harga, lot, target_pct, sl_pct):
    if lot <= 0: return None
    modal  = harga * lot * 100 * (1 + FEE_BELI)
    ht     = harga * (1 + target_pct / 100)
    hsl    = harga * (1 - sl_pct / 100)
    profit = ht  * lot * 100 * (1 - FEE_JUAL) - modal
    rugi   = hsl * lot * 100 * (1 - FEE_JUAL) - modal
    return {"modal": modal, "ht": ht, "hsl": hsl, "profit": profit, "rugi": rugi}

# ─────────────────────────────────────────────────────────────────────────────
# FETCH DATA (yfinance only)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=120, show_spinner=False)
def fetch_batch_yfinance(syms_tuple, period="6mo", interval="1d"):
    symbols = list(syms_tuple)
    tickers = [f"{s}.JK" for s in symbols]
    result  = {}
    try:
        raw = yf.download(tickers, period=period, interval=interval,
                          auto_adjust=True, progress=False, threads=True)
        if raw.empty:
            return {}
        if len(symbols) == 1:
            df = raw.copy()
            df.columns = [c.lower() for c in df.columns]
            df = df.dropna()
            if len(df) >= 20:
                result[symbols[0]] = df
        else:
            for sym in symbols:
                try:
                    df = raw.xs(f"{sym}.JK", axis=1, level=1).copy()
                    df.columns = [c.lower() for c in df.columns]
                    df = df.dropna()
                    if len(df) >= 20:
                        result[sym] = df
                except:
                    continue
    except Exception as e:
        pass
    return result

def hitung_indikator(df):
    try:
        df = df.copy()
        c = df["close"]
        df["RSI"]       = ta.momentum.rsi(c, window=14)
        df["EMA9"]      = ta.trend.ema_indicator(c, window=9)
        df["EMA21"]     = ta.trend.ema_indicator(c, window=21)
        df["EMA50"]     = ta.trend.ema_indicator(c, window=50)
        macd_obj        = ta.trend.MACD(c)
        df["MACD"]      = macd_obj.macd()
        df["MACD_hist"] = macd_obj.macd_diff()
        df["vol_ma20"]  = df["volume"].rolling(20).mean()
        
        # Penambahan SMA untuk BSJP V1
        df["MA5"]       = c.rolling(5).mean()
        df["MA20"]      = c.rolling(20).mean()
        df["MA50"]      = c.rolling(50).mean()
        return df.iloc[-1].to_dict()
    except:
        return None

def tentukan_sinyal(ind, harga, prev, sesi_status, strategi="🟢 BPJS Sesi 1 (Pagi)"):
    if ind is None:
        return "TUNGGU", ["Data kurang"], {}
    rsi    = ind.get("RSI", 50)
    ema9   = ind.get("EMA9", harga)
    ema21  = ind.get("EMA21", harga)
    mh     = ind.get("MACD_hist", 0)
    vol    = ind.get("volume", 0)
    volma  = ind.get("vol_ma20", vol or 1)
    
    ma5    = ind.get("MA5", harga)
    ma20   = ind.get("MA20", harga)
    ma50   = ind.get("MA50", harga)

    ara_limit = get_ara_limit(prev)
    chg = (harga - prev) / prev * 100 if prev > 0 else 0
    val_today = harga * vol

    # Kriteria default
    metrics = {}
    signal_ok = False

    if strategi == "🟢 BPJS Sesi 1 (Pagi)":
        c_vol_spike   = vol >= 1.5 * volma
        c_value       = val_today >= 5_000_000_000
        c_rsi         = 30 <= rsi <= 60
        c_trend       = ema9 > ema21
        c_macd        = mh > 0
        c_chg         = 2.0 <= chg <= 15.0
        
        signal_ok = c_vol_spike and c_value and c_rsi and c_trend and c_macd and c_chg
        metrics = {
            "Lonjakan Volume (>=1.5x MA20)": c_vol_spike,
            "Nilai Transaksi Hari Ini (>=5M)": c_value,
            "RSI Sehat (30-60)": c_rsi,
            "Tren Bullish (EMA9>EMA21)": c_trend,
            "MACD Histogram > 0": c_macd,
            "Kenaikan Pagi (2%-15%)": c_chg
        }
        alasan = [k for k, v in metrics.items() if v]

    elif strategi == "🟡 BPJS Sesi 2 (Siang)":
        c_vol_spike   = vol >= 1.3 * volma
        c_value       = val_today >= 10_000_000_000
        c_rsi         = 40 <= rsi <= 65
        c_trend       = ema9 > ema21
        c_macd        = mh > 0
        c_chg         = 3.0 <= chg <= 20.0
        
        signal_ok = c_vol_spike and c_value and c_rsi and c_trend and c_macd and c_chg
        metrics = {
            "Lonjakan Volume (>=1.3x MA20)": c_vol_spike,
            "Nilai Transaksi Hari Ini (>=10M)": c_value,
            "RSI Sehat (40-65)": c_rsi,
            "Tren Bullish (EMA9>EMA21)": c_trend,
            "MACD Histogram > 0": c_macd,
            "Kenaikan Siang (3%-20%)": c_chg
        }
        alasan = [k for k, v in metrics.items() if v]

    elif strategi == "🟣 BSJP (Beli Sore)":
        c_vol_spike   = vol >= 1.2 * volma
        c_value       = val_today >= 20_000_000_000
        c_volma20     = volma >= 1_000_000
        c_trend_med   = ma20 >= ma50
        c_trend_short = ma5 >= ma20
        c_min_chg     = chg > 5.0
        c_max_chg     = chg <= (ara_limit - 1.0)
        
        signal_ok = c_vol_spike and c_value and c_volma20 and c_trend_med and c_trend_short and c_min_chg and c_max_chg
        metrics = {
            "Lonjakan Volume (>=1.2x MA20)": c_vol_spike,
            "Nilai Transaksi Hari Ini (>=20M)": c_value,
            "Rata-rata Vol MA20 >= 1 Juta": c_volma20,
            "Tren Menengah (MA20 >= MA50)": c_trend_med,
            "Momentum Pendek (MA5 >= MA20)": c_trend_short,
            "Kenaikan Sore (>5%)": c_min_chg,
            "Kenaikan <= ARA": c_max_chg
        }
        alasan = [k for k, v in metrics.items() if v]

    elif strategi == "🔥 ARA Hunter":
        # Min return dinamis untuk ARA hunter
        if prev < 50:    min_chg = 6.0
        elif prev <= 200: min_chg = 25.0
        elif prev <= 5000:min_chg = 18.0
        else:             min_chg = 15.0

        c_vol_spike   = vol >= 2.0 * volma
        c_value       = val_today >= 30_000_000_000
        c_rsi         = rsi >= 65
        c_macd        = mh > 0
        c_min_chg     = chg >= min_chg
        c_max_chg     = chg < ara_limit
        
        signal_ok = c_vol_spike and c_value and c_rsi and c_macd and c_min_chg and c_max_chg
        metrics = {
            "Volume Ekstrem (>=2.0x MA20)": c_vol_spike,
            "Nilai Transaksi Hari Ini (>=30M)": c_value,
            "RSI Sangat Kuat (>=65)": c_rsi,
            "MACD Histogram > 0": c_macd,
            "Kenaikan Tinggi": c_min_chg,
            "Di Bawah ARA": c_max_chg
        }
        alasan = [k for k, v in metrics.items() if v]

    # Kita kembalikan sinyal BPJS atau BSJP atau ARA Hunter atau TUNGGU
    if signal_ok:
        if strategi in ("🟢 BPJS Sesi 1 (Pagi)", "🟡 BPJS Sesi 2 (Siang)", "🔥 ARA Hunter"):
            return "BELI", alasan, metrics
        elif strategi == "🟣 BSJP (Beli Sore)":
            return "BSJP", alasan, metrics
    
    # Check JUAL
    js = 0
    if rsi > 75: js += 2
    if ema9 < ema21: js += 1
    if mh < 0: js += 1
    if harga < ema21: js += 1
    
    if js >= 3:
        return "JUAL", ["Tren Melemah / Jenuh Beli ⚠️"], metrics
        
    return "TUNGGU", ["Menunggu Konfirmasi Momentum"], metrics

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
# 🔄 Refresh Data (Tombol paling atas)
if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("## ⚙️ Pengaturan")

# 📊 Strategi Analisis
st.sidebar.markdown("### 📊 Strategi Analisis")
strategi = st.sidebar.radio(
    "Pilih Metode Analisis:",
    [
        "🟢 BPJS Sesi 1 (Pagi)",
        "🟡 BPJS Sesi 2 (Siang)",
        "🟣 BSJP (Beli Sore)",
        "🔥 ARA Hunter"
    ],
    index=2  # Default: BSJP
)

# Info Box Strategi (Clean & Simple)
if strategi == "🟢 BPJS Sesi 1 (Pagi)":
    st.sidebar.info("💡 **BPJS Sesi 1**: Skrining saham momentum pagi hari (09:00 - 11:30 WIB) untuk scalping cepat dengan target profit 5-10%.")
elif strategi == "🟡 BPJS Sesi 2 (Siang)":
    st.sidebar.info("💡 **BPJS Sesi 2**: Skrining setelah istirahat siang (13:30 - 15:50 WIB) untuk scalping kelanjutan tren.")
elif strategi == "🟣 BSJP (Beli Sore)":
    st.sidebar.info("💡 **BSJP**: Skrining sore hari menjelang tutup bursa untuk menangkap saham yang diakumulasi dan berpotensi naik besok pagi.")
elif strategi == "🔥 ARA Hunter":
    st.sidebar.info("💡 **ARA Hunter**: Skrining saham ber-volume masif yang sedang menuju/berpotensi mengunci kenaikan tertinggi (ARA).")

# 🔍 Filter & Sortir
st.sidebar.markdown("### 🔍 Filter & Sortir")
filter_sinyal = st.sidebar.checkbox("Hanya Sinyal BELI / BSJP", value=False)
min_confidence = st.sidebar.slider("🔥 Min. Confidence (%)", 10, 100, 30)
urut_opsi = st.sidebar.selectbox("Urutkan Berdasarkan:", [
    "Sinyal Teratas (Default)",
    "Confidence tertinggi",
    "% Change terbesar",
    "RSI terendah (Oversold)",
    "Volume transaksi"
], index=0)

# 📋 Jumlah Saham (Max 505 sesuai total ALL_SAHAM)
max_sahams = st.sidebar.slider("📋 Jumlah Saham", 5, 505, 50)

# ⏱️ Expander Timeframe (Lanjutan)
with st.sidebar.expander("⏱️ Pengaturan Lilin & Grafik (Lanjutan)", expanded=False):
    st.markdown("""
    * **Timeframe Analisis (Target):** Menentukan periode grafik lilin untuk perhitungan sinyal teknis.
    * **Timeframe TradingView:** Menentukan interval lilin default pada grafik interaktif kartu saham.
    """)
    tf_display = st.selectbox(
        "⏱️ Timeframe Analisis (Target):",
        [
            "⏱️ Harian - 1 Hari (Rekomendasi BSJP & ARA Hunter)",
            "⏱️ Menengah - 1 Jam (Rekomendasi Swing Pendek)",
            "⏱️ Scalping - 15 Menit (Rekomendasi Utama BPJS Sesi 1 & 2)",
            "⏱️ Scalping Cepat - 5 Menit (Scalping Sangat Agresif)"
        ],
        index=0
    )
    
    tf_mapping = {
        "⏱️ Harian - 1 Hari (Rekomendasi BSJP & ARA Hunter)": "1d",
        "⏱️ Menengah - 1 Jam (Rekomendasi Swing Pendek)": "1h",
        "⏱️ Scalping - 15 Menit (Rekomendasi Utama BPJS Sesi 1 & 2)": "15m",
        "⏱️ Scalping Cepat - 5 Menit (Scalping Sangat Agresif)": "5m"
    }
    tf_option = tf_mapping[tf_display]
    
    tf_config_mapping = {
        "5m":  {"period": "2d",  "interval": "5m"},
        "15m": {"period": "5d",  "interval": "15m"},
        "1h":  {"period": "1mo", "interval": "1h"},
        "1d":  {"period": "6mo", "interval": "1d"}
    }
    tf_config = tf_config_mapping[tf_option]
    
    tv_interval = st.select_slider(
        "📈 Timeframe TradingView:",
        options=["1", "5", "15", "30", "60", "1D", "1W"],
        value="1D"
    )

# 💰 Expander Keuangan (Money Management)
with st.sidebar.expander("💰 Pengaturan Keuangan", expanded=False):
    modal_per_saham = st.number_input(
        "💰 Modal per Saham (Rp):",
        min_value=100_000, max_value=20_000_000,
        value=500_000, step=50_000, format="%d"
    )
    target_pct = st.slider("🎯 Target Profit (%)", 2.0, 20.0, 5.0, 0.5)
    sl_pct     = st.slider("🛑 Stop Loss (%)",   1.0, 10.0, 3.0, 0.5)

# 🔑 Kode Akses Parameter (Private - Paling bawah)
st.sidebar.markdown("---")
access_key = st.sidebar.text_input(
    "🔑 Kode Akses Parameter (Private):",
    type="password",
    help="Masukkan kode akses Anda untuk membuka detail rumus indikator (default disembunyikan untuk umum)."
)
is_owner = (access_key == "rafifcuan")

st.sidebar.markdown("""
**📊 Sinyal:**
🟢 **BELI** = BPJS (Pagi)
🟣 **BSJP** = Beli Sore Jual Pagi
🔴 **JUAL** = Exit / Cut Loss
⏳ **TUNGGU** = Belum ada peluang

**💸 Fee Stockbit:**
Beli 0.10% + Jual 0.20%
""")

# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>📈 Scalping IHSG by Rafif</h1>
    <p>BPJS · BSJP · yfinance + TradingView · Powered by Stockbit</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# AMBIL DAFTAR SAHAM
# ─────────────────────────────────────────────────────────────────────────────
with st.spinner("📡 Menyiapkan daftar saham..."):
    symbols = ALL_SAHAM[:max_sahams]

symbols = symbols[:max_sahams]

# ── TICKER TAPE ───────────────────────────────────────────────────────────────
components.html(tv_ticker_tape(symbols[:20]), height=72)

# Status Pasar
sesi_status, sesi_label = get_status_pasar()
now_str = datetime.now(WIB).strftime("%H:%M:%S WIB — %A, %d %B %Y")
css_map = {"buka":"pasar-buka","tutup":"pasar-tutup","preopen":"pasar-preopen"}
st.markdown(f'<div class="{css_map[sesi_status]}">{sesi_label} &nbsp;|&nbsp; 🕐 {now_str}</div>',
            unsafe_allow_html=True)

# ── Download data yfinance ────────────────────────────────────────────────────
with st.spinner(f"📥 Mengunduh data {len(symbols)} saham (interval {tf_option})..."):
    all_data = fetch_batch_yfinance(tuple(symbols), period=tf_config["period"], interval=tf_config["interval"])

if not all_data:
    st.error("❌ Gagal unduh data. Cek koneksi internet.")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# HITUNG SINYAL
# ─────────────────────────────────────────────────────────────────────────────
results = []
prog = st.progress(0, text="Menghitung indikator...")
for i, sym in enumerate(symbols):
    df = all_data.get(sym)
    if df is None or df.empty:
        prog.progress((i+1)/len(symbols))
        continue
    ind   = hitung_indikator(df)
    harga = float(df["close"].iloc[-1])
    prev  = float(df["close"].iloc[-2]) if len(df) > 1 else harga
    vol   = float(df["volume"].iloc[-1]) if "volume" in df.columns else 0
    chg   = (harga - prev) / prev * 100 if prev > 0 else 0
    sinyal, alasan, bsjp_metrics = tentukan_sinyal(
        ind, harga, prev, sesi_status,
        strategi=strategi
    )
    confidence, conf_label, conf_color = hitung_confidence(ind, harga, sinyal, bsjp_metrics, strategi)
    lot = hitung_lot(modal_per_saham, harga)
    k   = kalkulator(harga, lot, target_pct, sl_pct)
    
    # Hitung rata-rata nilai transaksi harian 5 hari (Rupiah)
    df_copy = df.copy()
    df_copy["value"] = df_copy["close"] * df_copy["volume"]
    val_5d = float(df_copy["value"].tail(5).mean()) if len(df_copy) >= 5 else (harga * vol)
    
    results.append({"symbol":sym,"harga":harga,"prev":prev,"chg":chg,"vol":vol,"val_5d":val_5d,
                    "sinyal":sinyal,"alasan":alasan,"ind":ind or {},
                    "lot":lot,"k":k,
                    "confidence":confidence,"conf_label":conf_label,"conf_color":conf_color,
                    "bsjp_metrics":bsjp_metrics})
    prog.progress((i+1)/len(symbols), text=f"✅ {sym}")
prog.empty()

# ── Auto-save ke Signal History & Kirim Telegram Alerts ────────────────────────
new_signals = record_signals(results, modal_per_saham, target_pct, sl_pct)
if new_signals > 0:
    st.toast(f"✅ {new_signals} sinyal baru disimpan ke Signal History!", icon="📌")

if ENABLE_TG and TG_TOKEN and TG_CHAT_ID:
    sent_alerts = load_sent_alerts()
    today_str = datetime.now(WIB).strftime("%Y-%m-%d")
    alerts_sent_count = 0
    
    for r in results:
        if r["sinyal"] in ("BELI", "BSJP"):
            if r["confidence"] < min_confidence:
                continue
            # Alert key unik per saham, timeframe, dan tipe sinyal harian
            alert_key = f"{today_str}_{r['symbol']}_{tf_option}_{r['sinyal']}"
            if alert_key not in sent_alerts:
                success = send_telegram_alert(TG_TOKEN, TG_CHAT_ID, r, tf_option, target_pct, sl_pct)
                if success:
                    sent_alerts[alert_key] = True
                    alerts_sent_count += 1
                    
    if alerts_sent_count > 0:
        save_sent_alerts(sent_alerts)
        st.toast(f"🔔 {alerts_sent_count} alert baru dikirim ke Telegram!", icon="💬")

# Apply Sorting and UI Filtering
filtered_results = []
for r in results:
    if filter_sinyal and r["sinyal"] not in ("BELI", "BSJP"):
        continue
    if r["confidence"] < min_confidence:
        continue
    filtered_results.append(r)

# Tampilkan Status Pemindaian di Sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Status Pemindaian")
st.sidebar.write(f"• Saham di Watchlist: **{len(symbols)}**")
st.sidebar.write(f"• Berhasil Diunduh: **{len(all_data)}**")
st.sidebar.write(f"• Berhasil Dianalisis: **{len(results)}**")
st.sidebar.write(f"• Lolos Filter Tampilan: **{len(filtered_results)}**")

if urut_opsi == "Confidence tertinggi":
    filtered_results.sort(key=lambda x: x["confidence"], reverse=True)
elif urut_opsi == "% Change terbesar":
    filtered_results.sort(key=lambda x: x["chg"], reverse=True)
elif urut_opsi == "RSI terendah (Oversold)":
    filtered_results.sort(key=lambda x: x["ind"].get("RSI", 100))
elif urut_opsi == "Volume transaksi":
    filtered_results.sort(key=lambda x: x["vol"], reverse=True)
else:
    urutan = {"BELI":0,"BSJP":1,"JUAL":2,"TUNGGU":3}
    filtered_results.sort(key=lambda x: urutan.get(x["sinyal"], 9))

# ── Ringkasan Global ──────────────────────────────────────────────────────────
n_beli   = sum(1 for r in filtered_results if r["sinyal"]=="BELI")
n_bsjp   = sum(1 for r in filtered_results if r["sinyal"]=="BSJP")
n_jual   = sum(1 for r in filtered_results if r["sinyal"]=="JUAL")
n_tunggu = sum(1 for r in filtered_results if r["sinyal"]=="TUNGGU")

c1,c2,c3,c4 = st.columns(4)
c1.metric("🟢 Sinyal BELI", n_beli,
          delta="BPJS Ready!" if n_beli else "Belum ada",
          delta_color="normal" if n_beli else "off")
c2.metric("🟣 Sinyal BSJP",  n_bsjp,  delta="Overnight!" if n_bsjp else None)
c3.metric("🔴 Sinyal JUAL",  n_jual)
c4.metric("⏳ Tunggu",        n_tunggu)
st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# HELPER RENDER KARTU
# ─────────────────────────────────────────────────────────────────────────────
def render_kartu(r, strategi="🟢 BPJS Sesi 1 (Pagi)", is_owner=False):
    sym    = r["symbol"]
    harga  = r["harga"]
    chg    = r["chg"]
    sinyal = r["sinyal"]
    lot    = r["lot"]
    k      = r["k"]
    ind    = r["ind"]

    if sinyal=="BELI":   css,tag_css,tag_txt = "card-beli",  "tag-green",  "🟢 BELI / ENTRi"
    elif sinyal=="BSJP": css,tag_css,tag_txt = "card-bsjp",  "tag-purple", "🟣 BELI SORE (BSJP)"
    elif sinyal=="JUAL": css,tag_css,tag_txt = "card-jual",  "tag-red",    "🔴 JUAL / CUT LOSS"
    else:                css,tag_css,tag_txt = "card-tunggu","tag-gray",   "⏳ TUNGGU"

    chg_col  = "#22c55e" if chg>=0 else "#ef4444"
    chg_sign = "+" if chg>=0 else ""
    
    if is_owner:
        rsi      = ind.get("RSI",0)
        ema9     = ind.get("EMA9",0)
        ema21    = ind.get("EMA21",0)
        ema50    = ind.get("EMA50",0)
        mh       = ind.get("MACD_hist",0)
        rsi_col  = "#ef4444" if rsi>70 else ("#22c55e" if rsi<40 else "#f59e0b")
        pills_html = (
            f'<span class="ind-pill" style="color:{rsi_col}">RSI {rsi:.0f}</span>'
            f'<span class="ind-pill">EMA9 {ema9:,.0f}</span>'
            f'<span class="ind-pill">Val 5D: {r.get("val_5d", 0)/1_000_000_000:.1f}M</span>'
            f'<span class="ind-pill">EMA50 {ema50:,.0f}</span>'
            f'<span class="ind-pill">MACD {"▲" if mh>0 else "▼"} {mh:.2f}</span>'
        )
    else:
        pills_html = (
            f'<span class="ind-pill">Volume: Teranalisis</span>'
            f'<span class="ind-pill">Likuiditas: Teranalisis</span>'
            f'<span class="ind-pill">Tren: Teranalisis</span>'
        )
    
    analisis = buat_analisis_singkat(ind, harga, sinyal, chg, r.get("bsjp_metrics"), strategi, is_owner)
    confidence = r.get("confidence", 50)
    conf_label = r.get("conf_label", "Cukup")
    conf_color = r.get("conf_color", "#cbd5e1")

    if is_owner:
        alasan_pills = "".join([f'<span class="ind-pill">{a}</span>' for a in r["alasan"]])
    else:
        alasan_pills = f'<span class="ind-pill">🔒 Detail indikator disembunyikan</span>'

    bsjp_check_html = ""
    if r.get("bsjp_metrics"):
        metrics = r["bsjp_metrics"]
        items = []
        for name, met in metrics.items():
            color = "#22c55e" if met else "#ef4444"
            icon = "✅" if met else "❌"
            if is_owner:
                display_name = name
            else:
                display_name = name.split(" (")[0].split(" >= ")[0].split(" <=")[0]
            items.append(f'<span style="color:{color};font-size:0.75rem;margin-right:8px;white-space:nowrap;">{icon} {display_name}</span>')
        bsjp_check_html = f'<div style="margin-top:8px;display:flex;flex-wrap:wrap;background:rgba(255,255,255,0.05);padding:8px;border-radius:10px;border:1px solid rgba(255,255,255,0.1)">{"".join(items)}</div>'

    kalkulasi_html = ""
    if k:
        kalkulasi_html = (
            f'<div class="kalkulator">'
            f'💼 <b>Lot:</b> {lot} lot &nbsp;|&nbsp; '
            f'💰 <b>Modal:</b> Rp {k["modal"]:,.0f}<br>'
            f'🎯 <b>Target:</b> Rp {snap_fraksi(k["ht"]):,} &nbsp;|&nbsp; '
            f'🛑 <b>Stop Loss:</b> Rp {snap_fraksi(k["hsl"]):,}<br>'
            f'✅ <b>Est. Profit:</b> <span style="color:#22c55e">Rp {k["profit"]:+,.0f}</span> &nbsp;|&nbsp; '
            f'❌ <b>Est. Rugi:</b> <span style="color:#ef4444">Rp {k["rugi"]:+,.0f}</span>'
            f'</div>'
        )

    st.markdown(f"""
    <div class="{css}">
        <div style="display:flex;justify-content:space-between;align-items:flex-start">
            <span class="card-sym">{sym}</span>
            <span class="{tag_css}">{tag_txt}</span>
        </div>
        <p class="card-price">Rp {harga:,.0f}</p>
        <p style="font-size:0.88rem;color:{chg_col};margin:0 0 6px 0;font-weight:700">
            {chg_sign}{chg:.2f}% hari ini
        </p>
        <div>
            {pills_html}
        </div>
        <div style="margin-top:8px">{alasan_pills}</div>
        {bsjp_check_html}
        <div style="margin-top:8px;padding:10px;background:rgba(0,0,0,0.2);border-radius:10px;font-size:0.8rem;color:#cbd5e1">
            <b style="color:{conf_color}">Confidence: {confidence}% — {conf_label}</b><br>
            <span style="font-size:0.78rem">{analisis}</span>
        </div>
        {kalkulasi_html}
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📊 Dashboard Real-Time", "📋 Signal History & Evaluasi"])

with tab1:
    beli_list = [r for r in filtered_results if r["sinyal"] in ("BELI","BSJP")]
    jual_list = [r for r in filtered_results if r["sinyal"] == "JUAL"]
    tung_list = [r for r in filtered_results if r["sinyal"] == "TUNGGU"]

    if beli_list:
        st.markdown('<div class="section-header">🟢 Sinyal BELI & 🟣 BSJP</div>', unsafe_allow_html=True)
        cols = st.columns(min(len(beli_list), 3))
        for i, r in enumerate(beli_list):
            with cols[i % 3]:
                # Live Price Override
                override_key = f"override_{r['symbol']}_{tf_option}"
                if override_key in st.session_state:
                    override_price = st.session_state[override_key]
                    if override_price != float(r['harga']):
                        r['harga'] = override_price
                        r['lot'] = hitung_lot(modal_per_saham, override_price)
                        r['k'] = kalkulator(override_price, r['lot'], target_pct, sl_pct)
                
                render_kartu(r, strategi, is_owner)
                
                # Interactive Price Override Input
                st.number_input(
                    f"✏️ Sesuaikan Harga {r['symbol']}:",
                    min_value=1.0,
                    value=float(r['harga']),
                    step=1.0,
                    key=override_key
                )
                
                with st.expander(f"📈 Chart TradingView {r['symbol']}"):
                    components.html(tv_advanced_chart(r["symbol"], interval=tv_interval), height=410)
                with st.expander(f"📊 Analisis Teknis {r['symbol']}"):
                    components.html(tv_technical_analysis(r["symbol"], interval=tv_interval), height=390)

    if jual_list:
        st.markdown('<div class="section-header">🔴 Sinyal JUAL / Cut Loss</div>', unsafe_allow_html=True)
        cols = st.columns(min(len(jual_list), 3))
        for i, r in enumerate(jual_list):
            with cols[i % 3]:
                # Live Price Override
                override_key = f"override_{r['symbol']}_{tf_option}"
                if override_key in st.session_state:
                    override_price = st.session_state[override_key]
                    if override_price != float(r['harga']):
                        r['harga'] = override_price
                        r['lot'] = hitung_lot(modal_per_saham, override_price)
                        r['k'] = kalkulator(override_price, r['lot'], target_pct, sl_pct)
                
                render_kartu(r, strategi, is_owner)
                
                st.number_input(
                    f"✏️ Sesuaikan Harga {r['symbol']}:",
                    min_value=1.0,
                    value=float(r['harga']),
                    step=1.0,
                    key=override_key
                )

    if tung_list:
        with st.expander(f"⏳ TUNGGU ({len(tung_list)} saham) — klik untuk lihat"):
            cols = st.columns(3)
            for i, r in enumerate(tung_list):
                with cols[i % 3]:
                    # Live Price Override
                    override_key = f"override_{r['symbol']}_{tf_option}"
                    if override_key in st.session_state:
                        override_price = st.session_state[override_key]
                        if override_price != float(r['harga']):
                            r['harga'] = override_price
                            r['lot'] = hitung_lot(modal_per_saham, override_price)
                            r['k'] = kalkulator(override_price, r['lot'], target_pct, sl_pct)
                    
                    render_kartu(r, strategi, is_owner)
                    
                    st.number_input(
                        f"✏️ Sesuaikan Harga {r['symbol']}:",
                        min_value=1.0,
                        value=float(r['harga']),
                        step=1.0,
                        key=override_key
                    )

with tab2:
    st.markdown("### 📋 Riwayat Sinyal & Evaluasi Akurasi")
    with st.spinner("Mengevaluasi riwayat sinyal..."):
        history, changed = evaluate_history()
    if changed:
        st.success(f"✅ {changed} sinyal berhasil dievaluasi!")
    if not history:
        st.info("Belum ada riwayat sinyal. Riwayat akan tersimpan otomatis saat sinyal BELI/BSJP/JUAL muncul.")
    else:
        df_hist = pd.DataFrame(history)
        df_hist = df_hist.sort_values("scan_date", ascending=False)
        cols_show = ["scan_date","scan_time","symbol","sinyal","harga_signal",
                     "confidence","conf_label","target_harga","sl_harga",
                     "harga_close","return_pct","outcome","est_profit_rp"]
        cols_show = [c for c in cols_show if c in df_hist.columns]
        st.dataframe(df_hist[cols_show], use_container_width=True)

        done = df_hist[df_hist["outcome"].notna()]
        if not done.empty:
            st.markdown("### 📊 Statistik Akurasi")
            c1,c2,c3,c4 = st.columns(4)
            total = len(done)
            hit   = len(done[done["outcome"].str.contains("TARGET|PROFIT|TURUN", na=False)])
            winrate = hit/total*100 if total else 0
            avg_ret = done["return_pct"].mean() if "return_pct" in done.columns else 0
            tot_pnl = done["est_profit_rp"].sum() if "est_profit_rp" in done.columns else 0
            c1.metric("Total Sinyal", total)
            c2.metric("Win Rate", f"{winrate:.1f}%")
            c3.metric("Avg Return", f"{avg_ret:+.2f}%")
            c4.metric("Est. Total P&L", f"Rp {tot_pnl:+,.0f}")
