import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
import ta
import json
import os
from datetime import datetime, timedelta
import pytz

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

# ── LQ45 + Saham Populer Multi-Sektor (130+ saham) ───────────────────────────
LQ45_POPULER = [
    # === PERBANKAN ===
    "BBCA","BBRI","BMRI","BBTN","BJBR","BJTM","BNGA","NISP","PNBN",
    "BACA","ARTO","MEGA","BSIM","AGRO","BANK","BBKP","BCAP","BMAS",
    # === TELEKOMUNIKASI ===
    "TLKM","ISAT","EXCL","FREN","TBIG","TOWR",
    # === PERTAMBANGAN & ENERGI ===
    "ANTM","MDKA","PTBA","ADRO","INCO","TINS","ESSA","HRUM","ITMG","VALE",
    "DEWA","BRMS","BULL","BNBR","BUMI","ELSA","BIPI","MEDC","COAL","DOID",
    "SMMT","GEMS","RATU","MBAP","CITA",
    # === PROPERTI & KONSTRUKSI ===
    "BSDE","CTRA","PWON","SMRA","KIJA","LPKR","BKSL","MDLN","DMAS","MTLA",
    "ASRI","JRPT","BEST","NZIA","NRCA","SSIA","BAPA","MKPI","DUTI","BIPP",
    "WIKA","WSKT","PTPP",
    # === CONSUMER GOODS & RITEL ===
    "UNVR","ICBP","INDF","GGRM","HMSP","MAPI","ACES","MIKA","HEAL","KLBF",
    "SIDO","MYOR","CLEO","GOOD","ULTJ","DLTA","ROTI","AMRT","HERO","CSAP",
    "RALS","LPPF","ERAA","MIDI",
    # === KESEHATAN & FARMASI ===
    "KAEF","SOHO","TSPC","DVLA","MERK","PYFA",
    # === INFRASTRUKTUR & UTILITAS ===
    "JSMR","PGAS","AKRA","SMGR","INTP","SMBR","WSBP","WTON","ACST",
    # === TEKNOLOGI & DIGITAL & MEDIA ===
    "GOTO","EMTK","MNCN","SCMA","DGNS","FILM","MTDL","WIFI","MCAS","AXIO","DMMX",
    # === OTOMOTIF & ALAT BERAT ===
    "ASII","AUTO","IMAS","SMSM","UNTR","HEXA","GJTL","INDS",
    # === AGRIBISNIS ===
    "AALI","LSIP","SSMS","SGRO","TAPG","BWPT","MGRO",
    # === KEUANGAN NON-BANK ===
    "ADMF","BFIN","WOMF","MFIN","IMJS","BPFI",
    # === SHIPPING & LOGISTIK ===
    "MBSS","HITS","SMDR","TMAS","PSSI",
    # === KIMIA & MATERIAL DASAR ===
    "BRPT","TPIA","MARK","BUDI","DPNS","EKAD","ETWA",
    # === HOT STOCKS & MOMENTUM ===
    "BREN","AMMN","SRTG","HRTA","BBKP","SRAJ","MSIN",
]
# Hapus duplikat, jaga urutan
_seen = set()
LQ45_POPULER = [x for x in LQ45_POPULER if not (x in _seen or _seen.add(x))]

# ── BSJP WATCHLIST — Saham aktif Sesi 2 & cocok overnight BSJP ───────────────
BSJP_WATCHLIST = [
    # === PERBANKAN — likuid & banyak gerak sesi 2 ===
    "BBCA","BBRI","BMRI","BBTN","BJBR","BJTM","BNGA","NISP","PNBN",
    "BACA","ARTO","MEGA","BCAP","BBKP",
    # === TELEKOMUNIKASI ===
    "TLKM","ISAT","EXCL","FREN","TBIG","TOWR",
    # === PERTAMBANGAN & ENERGI — volatilitas tinggi, favorit BSJP ===
    "ANTM","MDKA","PTBA","ADRO","INCO","TINS","ESSA","HRUM","ITMG","VALE",
    "DEWA","BRMS","BULL","BNBR","BUMI","ELSA","BIPI","MEDC","COAL","DOID",
    "SMMT","GEMS","RATU","MBAP","CITA",
    # === PROPERTI — seringkali pump sesi 2 & BSJP favorit ===
    "BSDE","CTRA","PWON","SMRA","KIJA","LPKR","BKSL","MDLN","DMAS","MTLA",
    "ASRI","JRPT","BEST","NZIA","NRCA","SSIA","DUTI","BIPP","BAPA",
    # === CONSUMER GOODS & RITEL ===
    "ICBP","INDF","GGRM","HMSP","MAPI","ACES","MIKA","HEAL","UNVR","KLBF",
    "SIDO","MYOR","CLEO","GOOD","ULTJ","AMRT","RALS","ERAA",
    # === INFRASTRUKTUR & KONSTRUKSI ===
    "JSMR","WIKA","WSKT","PTPP","PGAS","AKRA","SMGR","INTP","WTON","ACST",
    # === TEKNOLOGI & DIGITAL & MEDIA ===
    "GOTO","EMTK","MNCN","SCMA","DGNS","FILM","MTDL","ERAA","MCAS","WIFI",
    "AXIO","DMMX",
    # === OTOMOTIF ===
    "ASII","AUTO","UNTR","SMSM","HEXA",
    # === AGRIBISNIS ===
    "AALI","LSIP","SSMS","SGRO","TAPG","MGRO",
    # === KESEHATAN ===
    "KAEF","SOHO","TSPC","DVLA","HEAL","MIKA","KLBF",
    # === KIMIA & MATERIAL ===
    "BRPT","TPIA","MARK","DPNS",
    # === SHIPPING ===
    "MBSS","HITS","SMDR","TMAS",
    # === HOT STOCKS & MOMENTUM — NZIA ★ ===
    "NZIA","BREN","AMMN","SRTG","HRTA","GOTO","MDKA","BBKP",
    "SRAJ","MSIN","COAL","ESSA","BIPI",
]
_seen2 = set()
BSJP_WATCHLIST = [x for x in BSJP_WATCHLIST if not (x in _seen2 or _seen2.add(x))]

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
    return f"""
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript"
        src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
      {{
        "interval": "{interval}",
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

def tv_mini_chart(symbol, height=220):
    return f"""
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript"
        src="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js" async>
      {{
        "symbol": "IDX:{symbol}",
        "width": "100%",
        "height": {height},
        "locale": "id",
        "dateRange": "1M",
        "colorTheme": "dark",
        "isTransparent": true,
        "autosize": false,
        "largeChartUrl": "https://www.tradingview.com/chart/?symbol=IDX:{symbol}"
      }}
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
                if ret >= entry["target_pct"]:
                    outcome = "HIT_TARGET ✅"
                elif ret <= -entry["sl_pct"]:
                    outcome = "HIT_SL ❌"
                elif ret > 0:
                    outcome = "PROFIT 🟡"
                else:
                    outcome = "LOSS 🔴"
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
# FUNGSI ANALISIS & SINYAL
# ─────────────────────────────────────────────────────────────────────────────
def hitung_confidence(ind, harga, sinyal):
    if ind is None:
        return 25, "❓ Data kurang", "#6b7280"
    rsi    = ind.get("RSI", 50)
    ema9   = ind.get("EMA9", harga)
    ema21  = ind.get("EMA21", harga)
    ema50  = ind.get("EMA50", harga)
    mh     = ind.get("MACD_hist", 0)
    macd   = ind.get("MACD", 0)
    vol    = ind.get("volume", 0)
    volma  = ind.get("vol_ma20", vol or 1)
    score  = 0
    if sinyal in ("BELI", "BSJP"):
        if   rsi < 30: score += 25
        elif rsi < 40: score += 20
        elif rsi < 50: score += 14
        elif rsi < 55: score += 7
        if ema9 > ema21:
            margin = (ema9 - ema21) / ema21 * 100
            score += min(20, int(10 + margin * 5))
        if harga > ema50: score += 15
        elif harga > ema50 * 0.98: score += 7
        if mh > 0:
            score += 10
            if macd > 0: score += 10
        if volma > 0:
            ratio = vol / volma
            if   ratio >= 2.0: score += 20
            elif ratio >= 1.5: score += 15
            elif ratio >= 1.2: score += 10
            elif ratio >= 1.0: score += 5
    elif sinyal == "JUAL":
        if   rsi > 80: score += 25
        elif rsi > 70: score += 18
        elif rsi > 60: score += 8
        if ema9 < ema21:
            margin = (ema21 - ema9) / ema21 * 100
            score += min(20, int(10 + margin * 5))
        if harga < ema50: score += 15
        if mh < 0: score += 20
        if vol > volma * 1.2: score += 20
    else:
        score = max(20, min(45, int(50 - abs(rsi - 50))))
    score = max(10, min(100, score))
    if   score >= 80: label, color = "🔥 Sangat Kuat",  "#22c55e"
    elif score >= 65: label, color = "💪 Kuat",          "#84cc16"
    elif score >= 50: label, color = "✅ Cukup",          "#f59e0b"
    elif score >= 35: label, color = "⚠️ Lemah",          "#f97316"
    else:             label, color = "❌ Sangat Lemah",   "#ef4444"
    return score, label, color

def buat_analisis_singkat(ind, harga, sinyal, chg):
    if ind is None or not ind:
        return "Data historis tidak mencukupi untuk melakukan analisis teknikal."
    rsi    = ind.get("RSI", 50)
    ema9   = ind.get("EMA9", harga)
    ema21  = ind.get("EMA21", harga)
    ema50  = ind.get("EMA50", harga)
    mh     = ind.get("MACD_hist", 0)
    vol    = ind.get("volume", 0)
    volma  = ind.get("vol_ma20", vol or 1)
    if harga > ema50:
        if ema9 > ema21:
            tren_txt = "Saham sedang bergerak dalam fase <b>uptrend yang sangat kuat</b> (Bullish kokoh)."
        else:
            tren_txt = "Meskipun tren jangka panjang masih <b>Bullish</b>, saat ini sedang terjadi koreksi/konsolidasi jangka pendek."
    else:
        if ema9 > ema21:
            tren_txt = "Saham berada dalam tren turun jangka panjang (<b>Bearish</b>), namun mulai menunjukkan indikasi <b>rebound jangka pendek</b>."
        else:
            tren_txt = "Saham berada dalam fase <b>downtrend dominan</b> (Bearish kuat) baik jangka panjang maupun jangka pendek."
    if rsi < 30:
        rsi_txt = "Momentum RSI menunjukkan kondisi <b>jenuh jual ekstrem (oversold)</b> yang berpotensi memicu technical rebound cepat."
    elif rsi < 40:
        rsi_txt = "Indikator RSI berada di area <b>hampir jenuh jual (oversold)</b>, menandakan harga sudah mulai murah."
    elif rsi > 70:
        rsi_txt = "RSI sudah memasuki area <b>jenuh beli (overbought)</b>, sehingga rawan terkena aksi ambil untung (profit taking)."
    else:
        rsi_txt = "Indikator RSI berada di area netral (konsolidasi)."
    if mh > 0:
        macd_txt = "Hal ini dikonfirmasi oleh MACD histogram yang <b>positif</b>, menandakan momentum beli sedang bertambah kuat."
    else:
        macd_txt = "Tekanan ini didukung oleh MACD histogram yang <b>negatif</b>, menunjukkan dominasi penjual masih kuat."
    ratio = vol / volma if volma > 0 else 1.0
    if ratio >= 1.5:
        if sinyal in ("BELI", "BSJP"):
            vol_txt = "Lonjakan volume transaksi yang <b>sangat tinggi</b> mengindikasikan adanya <b>akumulasi besar-besaran</b> oleh pasar."
        else:
            vol_txt = "Lonjakan volume transaksi yang <b>sangat tinggi</b> mendampingi penurunan harga, menandakan adanya <b>tekanan jual yang masif</b>."
    elif ratio >= 1.2:
        vol_txt = "Volume transaksi terpantau meningkat di atas rata-rata harian, menandakan partisipasi pasar cukup aktif."
    else:
        vol_txt = "Volume transaksi terpantau stabil di bawah rata-rata harian."
    if sinyal == "BELI":
        aksi_txt = "Ini adalah momen yang baik untuk melakukan entri <b>BELI</b> guna memanfaatkan momentum kenaikan cepat (scalping)."
    elif sinyal == "BSJP":
        aksi_txt = "Akumulasi volume di akhir sesi mendukung entri <b>BSJP</b> (Beli Sore Jual Pagi) dengan target jual di pembukaan esok hari."
    elif sinyal == "JUAL":
        if rsi < 35:
            aksi_txt = "Meskipun RSI sudah jenuh jual, tren jangka pendek masih melemah. Disarankan tetap <b>JUAL / Cut Loss</b> untuk pengamanan modal, atau tunggu konfirmasi rebound sebelum masuk kembali."
        else:
            aksi_txt = "Disarankan segera melakukan <b>JUAL / Cut Loss</b> untuk mengamankan modal dari potensi penurunan lebih lanjut."
    else:
        aksi_txt = "Disarankan untuk tetap <b>Wait & See (TUNGGU)</b> terlebih dahulu sampai indikator momentum memberikan sinyal pembalikan arah yang valid."
    return f"{tren_txt} {rsi_txt} {macd_txt} {vol_txt} 👉 {aksi_txt}"

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
@st.cache_data(ttl=1800, show_spinner=False)
def fetch_batch_yfinance(syms_tuple):
    symbols = list(syms_tuple)
    tickers = [f"{s}.JK" for s in symbols]
    result  = {}
    try:
        raw = yf.download(tickers, period="6mo", interval="1d",
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
        return df.iloc[-1].to_dict()
    except:
        return None

def tentukan_sinyal(ind, harga, sesi_status):
    if ind is None:
        return "TUNGGU", ["Data kurang"]
    rsi    = ind.get("RSI", 50)
    ema9   = ind.get("EMA9", harga)
    ema21  = ind.get("EMA21", harga)
    mh     = ind.get("MACD_hist", 0)
    vol    = ind.get("volume", 0)
    volma  = ind.get("vol_ma20", vol or 1)
    bull   = ema9 > ema21
    diatas = harga > ema21
    vspike = vol >= volma * 1.15 if volma > 0 else False
    alasan = []; bs = 0; js = 0
    if rsi < 50:   bs+=1; alasan.append(f"RSI {rsi:.0f} ✅")
    if bull:       bs+=1; alasan.append("EMA9>21 ✅")
    if mh > 0:     bs+=1; alasan.append("MACD+ ✅")
    if vspike:     bs+=1; alasan.append("Vol Spike ✅")
    if diatas:     bs+=1; alasan.append("Di atas EMA21 ✅")
    if rsi > 72:   js+=2; alasan.append(f"RSI {rsi:.0f} ⚠️")
    if not bull:   js+=1; alasan.append("EMA9<21 ⚠️")
    if mh < 0:     js+=1; alasan.append("MACD- ⚠️")
    if not diatas: js+=1; alasan.append("Di bawah EMA21 ⚠️")
    now = datetime.now(WIB)
    h2, m2 = now.hour, now.minute
    bsjp_ok = (14,30)<=(h2,m2)<=(15,50) and sesi_status=="buka" and bs>=4 and rsi<58 and mh>0
    if js >= 3:    return "JUAL",   alasan
    if bsjp_ok:    return "BSJP",   alasan
    if bs >= 3:    return "BELI",   alasan
    return "TUNGGU", alasan

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
st.sidebar.markdown("## ⚙️ Pengaturan")

mode_saham = st.sidebar.radio("📊 Sumber Saham:", [
    "📊 LQ45 + Populer (130 saham)",
    "🎯 BSJP Watchlist Sesi 2 ★",
    "✏️ Manual"
], index=0)

modal_per_saham = st.sidebar.number_input(
    "💰 Modal per Saham (Rp):",
    min_value=100_000, max_value=20_000_000,
    value=500_000, step=50_000, format="%d"
)
target_pct = st.sidebar.slider("🎯 Target Profit (%)", 2.0, 20.0, 5.0, 0.5)
sl_pct     = st.sidebar.slider("🛑 Stop Loss (%)",   1.0, 10.0, 3.0, 0.5)
max_sahams  = st.sidebar.slider("📋 Jumlah Saham",     5,   150,  50)

tv_interval = st.sidebar.select_slider(
    "📈 Timeframe TradingView:",
    options=["1", "5", "15", "30", "60", "1D", "1W"],
    value="1D"
)

manual_input = ""
if "Manual" in mode_saham:
    manual_input = st.sidebar.text_area(
        "Kode saham (pisahkan koma):",
        "BBCA,BBRI,TLKM,GOTO,BREN,ASII,MDKA,AMMN,ANTM,BMRI"
    )

if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

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
    if "Manual" in mode_saham:
        symbols = [s.strip().upper() for s in manual_input.split(",") if s.strip()]
    elif "BSJP" in mode_saham:
        symbols = BSJP_WATCHLIST[:max_sahams]
    else:
        symbols = LQ45_POPULER[:max_sahams]

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
with st.spinner(f"📥 Mengunduh data historis {len(symbols)} saham (yfinance batch)..."):
    all_data = fetch_batch_yfinance(tuple(symbols))

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
    sinyal, alasan = tentukan_sinyal(ind, harga, sesi_status)
    confidence, conf_label, conf_color = hitung_confidence(ind, harga, sinyal)
    lot = hitung_lot(modal_per_saham, harga)
    k   = kalkulator(harga, lot, target_pct, sl_pct)
    results.append({"symbol":sym,"harga":harga,"chg":chg,"vol":vol,
                    "sinyal":sinyal,"alasan":alasan,"ind":ind or {},
                    "lot":lot,"k":k,
                    "confidence":confidence,"conf_label":conf_label,"conf_color":conf_color})
    prog.progress((i+1)/len(symbols), text=f"✅ {sym}")
prog.empty()

urutan = {"BELI":0,"BSJP":1,"JUAL":2,"TUNGGU":3}
results.sort(key=lambda x: urutan.get(x["sinyal"],9))

# ── Auto-save ke Signal History ───────────────────────────────────────────────
new_signals = record_signals(results, modal_per_saham, target_pct, sl_pct)
if new_signals > 0:
    st.toast(f"✅ {new_signals} sinyal baru disimpan ke Signal History!", icon="📌")

# ── Ringkasan Global ──────────────────────────────────────────────────────────
n_beli   = sum(1 for r in results if r["sinyal"]=="BELI")
n_bsjp   = sum(1 for r in results if r["sinyal"]=="BSJP")
n_jual   = sum(1 for r in results if r["sinyal"]=="JUAL")
n_tunggu = sum(1 for r in results if r["sinyal"]=="TUNGGU")

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
def render_kartu(r):
    sym    = r["symbol"]
    harga  = r["harga"]
    chg    = r["chg"]
    sinyal = r["sinyal"]
    lot    = r["lot"]
    k      = r["k"]
    ind    = r["ind"]

    if sinyal=="BELI":   css,tag_css,tag_txt = "card-beli",  "tag-green",  "🟢 BELI – BPJS"
    elif sinyal=="BSJP": css,tag_css,tag_txt = "card-bsjp",  "tag-purple", "🟣 BELI SORE JUAL PAGI"
    elif sinyal=="JUAL": css,tag_css,tag_txt = "card-jual",  "tag-red",    "🔴 JUAL / CUT LOSS"
    else:                css,tag_css,tag_txt = "card-tunggu","tag-gray",   "⏳ TUNGGU"

    chg_col  = "#22c55e" if chg>=0 else "#ef4444"
    chg_sign = "+" if chg>=0 else ""
    rsi      = ind.get("RSI",0)
    ema9     = ind.get("EMA9",0)
    ema21    = ind.get("EMA21",0)
    ema50    = ind.get("EMA50",0)
    mh       = ind.get("MACD_hist",0)
    rsi_col  = "#ef4444" if rsi>70 else ("#22c55e" if rsi<40 else "#f59e0b")
    
    analisis = buat_analisis_singkat(ind, harga, sinyal, chg)
    confidence = r.get("confidence", 50)
    conf_label = r.get("conf_label", "Cukup")
    conf_color = r.get("conf_color", "#cbd5e1")

    alasan_pills = "".join([f'<span class="ind-pill">{a}</span>' for a in r["alasan"]])

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
            <span class="ind-pill" style="color:{rsi_col}">RSI {rsi:.0f}</span>
            <span class="ind-pill">EMA9 {ema9:,.0f}</span>
            <span class="ind-pill">EMA21 {ema21:,.0f}</span>
            <span class="ind-pill">EMA50 {ema50:,.0f}</span>
            <span class="ind-pill">MACD {'▲' if mh>0 else '▼'} {mh:.2f}</span>
        </div>
        <div style="margin-top:8px">{alasan_pills}</div>
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
    # BELI & BSJP
    beli_list = [r for r in results if r["sinyal"] in ("BELI","BSJP")]
    jual_list = [r for r in results if r["sinyal"] == "JUAL"]
    tung_list = [r for r in results if r["sinyal"] == "TUNGGU"]

    if beli_list:
        st.markdown('<div class="section-header">🟢 Sinyal BELI & 🟣 BSJP</div>', unsafe_allow_html=True)
        cols = st.columns(min(len(beli_list), 3))
        for i, r in enumerate(beli_list):
            with cols[i % 3]:
                render_kartu(r)
                with st.expander(f"📈 Chart {r['symbol']}"):
                    components.html(tv_mini_chart(r["symbol"]), height=230)
                with st.expander(f"📊 Analisis TradingView {r['symbol']}"):
                    components.html(tv_technical_analysis(r["symbol"], interval=tv_interval), height=390)

    if jual_list:
        st.markdown('<div class="section-header">🔴 Sinyal JUAL / Cut Loss</div>', unsafe_allow_html=True)
        cols = st.columns(min(len(jual_list), 3))
        for i, r in enumerate(jual_list):
            with cols[i % 3]:
                render_kartu(r)

    if tung_list:
        with st.expander(f"⏳ TUNGGU ({len(tung_list)} saham) — klik untuk lihat"):
            cols = st.columns(3)
            for i, r in enumerate(tung_list):
                with cols[i % 3]:
                    render_kartu(r)

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
