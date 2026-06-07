import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import requests
import pandas as pd
import ta
import json
import os
from datetime import datetime, timedelta
import pytz

# ─────────────────────────────────────────────────────────────────────────────
# KONFIGURASI HALAMAN
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Scalping IHSG — Trader Dashboard",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants & API Keys
GOAPI_KEY     = "f6da6e9d-87b7-5276-00ca-39652df1"
GOAPI_HEADERS = {"X-API-Key": GOAPI_KEY}
BASE_URL      = "https://api.goapi.io"
WIB           = pytz.timezone("Asia/Jakarta")
FEE_BELI      = 0.0010
FEE_JUAL      = 0.0020
HISTORY_FILE  = os.path.join(os.path.dirname(__file__), "signal_history.json")

LQ45_POPULER = [
    "BBCA","BBRI","BMRI","TLKM","ASII","GOTO","BREN","AMMN","MDKA","ANTM",
    "UNVR","ICBP","INDF","KLBF","SIDO","MIKA","HEAL","ACES","MAPI","ERAA",
    "ADRO","PTBA","INCO","TINS","PGAS","AKRA","SMGR","INTP","JSMR","MEDC",
    "BSDE","CTRA","PWON","SMRA","KIJA","EMTK","MNCN","SCMA","ESSA","SRTG",
    "BULL","BRPT","BRMS","DEWA","BNBR","FILM","DGNS","MTDL","WIKA","WSKT"
]

# ─────────────────────────────────────────────────────────────────────────────
# PREMIUM & MODERN CSS SYSTEM (Sleek Dark Slate & Emerald Theme)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* Reset base typography */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    color: #f1f5f9;
}

/* Glassmorphic Main Header Banner */
.main-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    padding: 24px 32px;
    margin-bottom: 20px;
    text-align: center;
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.4);
}
.main-header h1 {
    font-size: 2.2rem;
    font-weight: 800;
    margin: 0;
    background: linear-gradient(90deg, #10b981 0%, #3b82f6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.main-header p {
    color: #94a3b8;
    font-size: 0.95rem;
    margin: 6px 0 0 0;
}

/* Bursa Status Badges */
.pasar-buka {
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.2);
    border-radius: 10px;
    padding: 10px 16px;
    color: #34d399;
    font-weight: 600;
    font-size: 0.88rem;
    margin-bottom: 20px;
    text-align: center;
}
.pasar-tutup {
    background: rgba(100, 116, 139, 0.1);
    border: 1px solid rgba(100, 116, 139, 0.2);
    border-radius: 10px;
    padding: 10px 16px;
    color: #94a3b8;
    font-weight: 600;
    font-size: 0.88rem;
    margin-bottom: 20px;
    text-align: center;
}
.pasar-preopen {
    background: rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(59, 130, 246, 0.2);
    border-radius: 10px;
    padding: 10px 16px;
    color: #60a5fa;
    font-weight: 600;
    font-size: 0.88rem;
    margin-bottom: 20px;
    text-align: center;
}

/* Glow Card Layouts */
.card-beli {
    background: #1e293b;
    border: 2px solid #10b981;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 0 0 15px rgba(16, 185, 129, 0.15);
}
.card-bsjp {
    background: #1e293b;
    border: 2px solid #a855f7;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 0 0 15px rgba(168, 85, 247, 0.15);
}
.card-jual {
    background: #1e293b;
    border: 1px solid #ef4444;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 16px;
}
.card-tunggu {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 16px;
}

/* Card Typography & Elements */
.card-sym {
    font-size: 1.4rem;
    font-weight: 800;
    color: #ffffff;
}
.card-price {
    font-size: 2.1rem;
    font-weight: 800;
    color: #ffffff;
    margin: 4px 0;
}
.tag-green {
    background: #10b981;
    color: #0f172a;
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 0.75rem;
    font-weight: 700;
}
.tag-red {
    background: #ef4444;
    color: #ffffff;
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 0.75rem;
    font-weight: 700;
}
.tag-gray {
    background: #334155;
    color: #cbd5e1;
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 0.75rem;
    font-weight: 600;
}
.tag-purple {
    background: #a855f7;
    color: #ffffff;
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 0.75rem;
    font-weight: 700;
}

/* Clean Indicator Badges (Pills) */
.ind-pill {
    display: inline-block;
    border-radius: 20px;
    padding: 4px 10px;
    font-size: 0.75rem;
    margin: 3px 3px 3px 0;
    background: rgba(255, 255, 255, 0.05);
    color: #cbd5e1;
    border: 1px solid rgba(255, 255, 255, 0.05);
}

/* Embedded Calculator Style inside Cards */
.card-kalkulator {
    background: rgba(15, 23, 42, 0.5);
    border-radius: 10px;
    padding: 12px 14px;
    margin-top: 14px;
    font-size: 0.8rem;
    color: #94a3b8;
    line-height: 1.6;
}

.section-header {
    font-size: 1.15rem;
    font-weight: 700;
    color: #ffffff;
    margin: 18px 0 10px 0;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def get_status_pasar():
    now = datetime.now(WIB)
    if now.weekday() >= 5:
        return "tutup", "🔴 Bursa Tutup — Weekend (Senin buka 09:00 WIB)"
    h, m = now.hour, now.minute
    t = (h, m)
    if t < (8, 55):
        return "tutup", "🔴 Bursa Belum Buka — Sesi 1 mulai 09:00 WIB"
    elif t < (9, 0):
        return "preopen", "🔵 Sesi Pre-Opening — Pembukaan segera dimulai! ⚡"
    elif (9, 0) <= t < (11, 30):
        return "buka", "🟢 Sesi 1 Berjalan (09:00 – 11:30 WIB)"
    elif (11, 30) <= t < (13, 30):
        return "tutup", "🟡 Istirahat Sesi Siang (11:30 – 13:30 WIB)"
    elif (13, 30) <= t < (15, 50):
        return "buka", "🟢 Sesi 2 Berjalan (13:30 – 15:50 WIB)"
    else:
        return "tutup", "🔴 Bursa Sudah Tutup — Buka besok pagi 09:00 WIB"

def snap_fraksi(h):
    if h < 200:    return round(h)
    elif h < 500:  return round(h/2)*2
    elif h < 2000: return round(h/5)*5
    elif h < 5000: return round(h/25)*25
    else:          return round(h/50)*50

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
            "est_profit_rp":  None
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
            df = yf.download(f"{sym}.JK", period="5d", interval="1d", auto_adjust=True, progress=False)
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
# CORE CALCULATIONS & INDICATORS
# ─────────────────────────────────────────────────────────────────────────────
def hitung_indikator(df):
    try:
        df = df.copy()
        c = df["close"]
        
        # Fillna for indicators to avoid NaN values (e.g. for new IPO stocks)
        df["RSI"]       = ta.momentum.rsi(c, window=14).fillna(50)
        df["EMA9"]      = ta.trend.ema_indicator(c, window=9).fillna(c)
        df["EMA21"]     = ta.trend.ema_indicator(c, window=21).fillna(c)
        df["EMA50"]     = ta.trend.ema_indicator(c, window=50).fillna(c)
        macd_obj        = ta.trend.MACD(c)
        df["MACD"]      = macd_obj.macd().fillna(0)
        df["MACD_hist"] = macd_obj.macd_diff().fillna(0)
        df["vol_ma20"]  = df["volume"].rolling(20).mean().fillna(df["volume"])
        
        # Tambahan untuk Taktik BPJS & ARA Hunter
        df["MA5"]       = c.rolling(5).mean().fillna(c)
        df["MA50"]      = c.rolling(50).mean().fillna(c)
        
        res = df.iloc[-1].to_dict()
        if len(df) >= 3:
            res["prev_close"]   = float(df["close"].iloc[-2])
            res["prev_volume"]  = float(df["volume"].iloc[-2])
            p_close             = float(df["close"].iloc[-2])
            pp_close            = float(df["close"].iloc[-3])
            res["chg_kemarin"]  = (p_close - pp_close) / pp_close * 100 if pp_close > 0 else 0.0
        elif len(df) == 2:
            res["prev_close"]   = float(df["close"].iloc[-2])
            res["prev_volume"]  = float(df["volume"].iloc[-2])
            res["chg_kemarin"]  = 0.0
        else:
            res["prev_close"]   = float(df["close"].iloc[-1])
            res["prev_volume"]  = float(df["volume"].iloc[-1])
            res["chg_kemarin"]  = 0.0
            
        res["open_today"]  = float(df["open"].iloc[-1])
        res["value_today"] = float(df["volume"].iloc[-1]) * float(df["close"].iloc[-1])
        
        return res
    except:
        return None

# ─────────────────────────────────────────────────────────────────────────────
# TRADING TACTICS SIGNALS & CONFIDENCES
# ─────────────────────────────────────────────────────────────────────────────
def tentukan_sinyal_classic(ind, harga, sesi_status):
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

def tentukan_sinyal_bpjs_agresif(ind, harga, min_chg, min_val_miliar):
    if ind is None:
        return "TUNGGU", ["Data kurang"], 0
    
    prev_close  = ind.get("prev_close", harga)
    open_today  = ind.get("open_today", harga)
    prev_volume = ind.get("prev_volume", 0)
    vol_today   = ind.get("volume", 0)
    ma5         = ind.get("MA5", harga)
    value_today = ind.get("value_today", 0)
    
    chg_prev   = ((harga - prev_close) / prev_close * 100) if prev_close > 0 else 0
    cond_chg   = chg_prev >= min_chg
    cond_ma5   = harga >= ma5
    cond_green = harga >= open_today
    cond_vol   = vol_today >= 0.2 * prev_volume if prev_volume > 0 else False
    cond_val   = value_today >= min_val_miliar * 1_000_000_000
    
    alasan = []
    bs = 0
    
    if cond_chg:
        bs += 1
        alasan.append(f"Naik ≥{min_chg}% ({chg_prev:+.1f}%) ✅")
    else:
        alasan.append(f"Naik <{min_chg}% ({chg_prev:+.1f}%) ⚠️")
        
    if cond_ma5:
        bs += 1
        alasan.append("Di atas MA5 ✅")
    else:
        alasan.append("Di bawah MA5 ⚠️")
        
    if cond_green:
        bs += 1
        alasan.append("Candle Hijau ✅")
    else:
        alasan.append("Candle Merah ⚠️")
        
    if cond_vol:
        bs += 1
        pct_prev = (vol_today / prev_volume * 100) if prev_volume > 0 else 0
        alasan.append(f"Vol Pagi Cukup ({pct_prev:.0f}%) ✅")
    else:
        alasan.append("Vol Pagi Kurang ⚠️")
        
    if cond_val:
        bs += 1
        alasan.append(f"Value >{min_val_miliar}M (Rp {value_today/1e9:.1f}B) ✅")
    else:
        alasan.append(f"Value <{min_val_miliar}M (Rp {value_today/1e9:.1f}B) ⚠️")
        
    if bs == 5:
        return "BELI", alasan, bs
    return "TUNGGU", alasan, bs

def tentukan_sinyal_ara_hunter(ind, harga, min_chg_prev, min_val_miliar):
    """
    Taktik ARA Hunter:
    1. Previous Volume > 2 * Volume MA20 (Akumulasi volume kemarin)
    2. Smart Money Accumulation (Vol spike hari ini didukung momentum positif)
    3. Return harga kemarin > min_chg_prev % (Default: +3.0%)
    4. High Price Hari Ini > Price MA 5 (Sedang Breakout)
    5. Low Price Hari Ini > 0.95 * Price MA 50 (Tren besar sehat, memantul dari support)
    """
    if ind is None:
        return "TUNGGU", ["Data kurang"], 0
        
    prev_close  = ind.get("prev_close", harga)
    prev_volume = ind.get("prev_volume", 0)
    vol_today   = ind.get("volume", 0)
    vol_ma20    = ind.get("vol_ma20", 1)
    ma5         = ind.get("MA5", harga)
    ma50        = ind.get("MA50", harga)
    value_today = ind.get("value_today", 0)
    
    # Estimasi high/low hari ini (menggunakan close jika yfinance delay)
    high_today = ind.get("high", harga)
    low_today  = ind.get("low", harga)
    
    chg_prev = ind.get("chg_kemarin", 0.0)
    
    cond_vol_kemarin = prev_volume > 1.8 * vol_ma20 if vol_ma20 > 0 else False
    cond_smart_money = vol_today >= 0.15 * prev_volume if prev_volume > 0 else False
    cond_chg_prev    = chg_prev >= min_chg_prev
    cond_breakout    = high_today >= ma5
    cond_support     = low_today >= 0.95 * ma50
    cond_val         = value_today >= min_val_miliar * 1_000_000_000
    
    alasan = []
    bs = 0
    
    if cond_vol_kemarin:
        bs += 1
        alasan.append("Vol Kemarin Besar (Akumulasi) ✅")
    else:
        alasan.append("Vol Kemarin Biasa ⚠️")
        
    if cond_smart_money:
        bs += 1
        alasan.append("Smart Money Masuk ✅")
    else:
        alasan.append("Smart Money Pasif ⚠️")
        
    if cond_chg_prev:
        bs += 1
        alasan.append(f"Ret Kemarin Bullish ({chg_prev:+.1f}%) ✅")
    else:
        alasan.append(f"Ret Kemarin Lemah ({chg_prev:+.1f}%) ⚠️")
        
    if cond_breakout:
        bs += 1
        alasan.append("Breakout MA5 ✅")
    else:
        alasan.append("Gagal Breakout ⚠️")
        
    if cond_support:
        bs += 1
        alasan.append("Di atas Support MA50 ✅")
    else:
        alasan.append("Di bawah Support ⚠️")
        
    if cond_val:
        bs += 1
    
    # Dianggap sinyal BELI ARA jika minimal 4 dari 5 kriteria utama terpenuhi
    if bs >= 4 and cond_val:
        return "BELI", alasan, bs
    return "TUNGGU", alasan, bs

def tentukan_sinyal_bsjp(ind, harga, max_rsi, min_val_miliar):
    if ind is None:
        return "TUNGGU", ["Data kurang"], 0
    
    rsi    = ind.get("RSI", 50)
    ema9   = ind.get("EMA9", harga)
    ema21  = ind.get("EMA21", harga)
    mh     = ind.get("MACD_hist", 0)
    vol    = ind.get("volume", 0)
    volma  = ind.get("vol_ma20", vol or 1)
    value_today = ind.get("value_today", 0)
    
    bull   = ema9 > ema21
    diatas = harga > ema21
    vspike = vol >= volma * 1.10 if volma > 0 else False
    cond_val = value_today >= min_val_miliar * 1_000_000_000
    
    alasan = []
    bs = 0
    
    if bull:
        bs += 1
        alasan.append("EMA9 > EMA21 (Uptrend) ✅")
    else:
        alasan.append("EMA9 <= EMA21 (Downtrend) ⚠️")
        
    if mh > 0:
        bs += 1
        alasan.append("MACD Histogram Positif ✅")
    else:
        alasan.append("MACD Histogram Negatif ⚠️")
        
    if rsi < max_rsi:
        bs += 1
        alasan.append(f"RSI Aman ({rsi:.0f} < {max_rsi}) ✅")
    else:
        alasan.append(f"RSI Tinggi ({rsi:.0f} >= {max_rsi}) ⚠️")
        
    if vspike:
        bs += 1
        alasan.append("Volume Meningkat ✅")
    else:
        alasan.append("Volume Lemah ⚠️")
        
    if diatas:
        bs += 1
        alasan.append("Di atas EMA21 ✅")
    else:
        alasan.append("Di bawah EMA21 ⚠️")
        
    if cond_val:
        bs += 1
    
    # Sinyal BSJP aktif jika minimal 4 dari 5 kriteria utama terpenuhi dan likuiditas cukup
    if bs >= 4 and cond_val:
        return "BSJP", alasan, bs
    return "TUNGGU", alasan, bs

# ─────────────────────────────────────────────────────────────────────────────
# CONFIDENCE SCORING HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def hitung_confidence_classic(ind, harga, sinyal):
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
    if   score >= 80: label, color = "🔥 Sangat Kuat",   "#10b981"
    elif score >= 65: label, color = "💪 Kuat",           "#84cc16"
    elif score >= 50: label, color = "✅ Cukup",          "#f59e0b"
    elif score >= 35: label, color = "⚠️ Lemah",         "#f97316"
    else:             label, color = "❌ Sangat Lemah",   "#ef4444"
    return score, label, color

def hitung_confidence_bpjs(bs):
    score = int(bs * 20)
    score = max(10, min(100, score))
    if   score >= 100: label, color = "🔥 Sangat Kuat",   "#10b981"
    elif score >= 80:  label, color = "💪 Kuat",           "#84cc16"
    elif score >= 60:  label, color = "✅ Cukup",          "#f59e0b"
    elif score >= 40:  label, color = "⚠️ Lemah",         "#f97316"
    else:              label, color = "❌ Sangat Lemah",   "#ef4444"
    return score, label, color

def hitung_confidence_ara(bs):
    score = int(bs * 20)
    score = max(10, min(100, score))
    if   score >= 100: label, color = "🔥 Sangat Kuat",   "#10b981"
    elif score >= 80:  label, color = "💪 Kuat",           "#84cc16"
    elif score >= 60:  label, color = "✅ Cukup",          "#f59e0b"
    elif score >= 40:  label, color = "⚠️ Lemah",         "#f97316"
    else:              label, color = "❌ Sangat Lemah",   "#ef4444"
    return score, label, color

def hitung_confidence_bsjp(bs):
    score = int(bs * 20)
    score = max(10, min(100, score))
    if   score >= 100: label, color = "🔥 Sangat Kuat",   "#a855f7"
    elif score >= 80:  label, color = "💪 Kuat",           "#c084fc"
    elif score >= 60:  label, color = "✅ Cukup",          "#d8b4fe"
    elif score >= 40:  label, color = "⚠️ Lemah",         "#e9d5ff"
    else:              label, color = "❌ Sangat Lemah",   "#f3e8ff"
    return score, label, color

# ─────────────────────────────────────────────────────────────────────────────
# BEGINNER-FRIENDLY TACTICAL ANALYSES (1-2 sentences maximum)
# ─────────────────────────────────────────────────────────────────────────────
def buat_analisis_singkat_classic(ind, harga, sinyal, chg):
    if ind is None or not ind:
        return "Data historis kurang mencukupi untuk dianalisis."
    rsi = ind.get("RSI", 50)
    ema9 = ind.get("EMA9", harga)
    ema21 = ind.get("EMA21", harga)
    mh = ind.get("MACD_hist", 0)
    vol = ind.get("volume", 0)
    volma = ind.get("vol_ma20", vol or 1)
    
    if sinyal == "BELI":
        alasan = f"Saham ini terdeteksi masuk area beli karena tren jangka pendek menguat (EMA9 > EMA21)."
        if mh > 0:
            alasan += " Didukung oleh histogram MACD yang positif (+) menandakan momentum naik bertambah kuat."
        if vol >= volma * 1.15:
            alasan += f" Ada lonjakan volume transaksi harian sebesar {(vol/volma - 1)*100:.0f}% di atas rata-rata 20 hari."
        if rsi < 50:
            alasan += f" RSI di angka {rsi:.0f} menunjukkan harga belum terlalu mahal (belum jenuh beli)."
        return alasan
    elif sinyal == "BSJP":
        return f"Saham menunjukkan akumulasi beli kuat di akhir sesi dengan RSI {rsi:.0f} dan MACD positif. Sangat direkomendasikan untuk dibeli sore ini menjelang tutup pasar (15:50 WIB) lalu dijual besok pagi saat ada lonjakan pembukaan."
    elif sinyal == "JUAL":
        alasan = "Tren harga melemah tajam."
        if ema9 < ema21:
            alasan += " Garis EMA9 memotong ke bawah EMA21 (Death Cross) menandakan tren turun dimulai."
        if mh < 0:
            alasan += " MACD berada di area negatif (-)."
        if rsi > 70:
            alasan += f" RSI berada di {rsi:.0f} (jenuh beli), rawan aksi ambil untung (profit taking) oleh trader lain."
        return alasan + " Disarankan untuk segera Jual/Cut Loss untuk mengamankan modal."
    return f"Kondisi harga sedang konsolidasi sampingan (sideways). RSI berada di level netral {rsi:.0f}. Disarankan menunggu momentum breakout yang lebih jelas."

def buat_analisis_singkat_bpjs(ind, harga, sinyal, chg, bpjs_min_chg, bpjs_min_val):
    if ind is None or not ind:
        return "Data tidak mencukupi untuk menganalisis taktik BPJS."
    
    prev_close = ind.get("prev_close", harga)
    open_today = ind.get("open_today", harga)
    prev_volume = ind.get("prev_volume", 0)
    vol_today = ind.get("volume", 0)
    ma5 = ind.get("MA5", harga)
    value_today = ind.get("value_today", 0)
    
    chg_prev = ((harga - prev_close) / prev_close * 100) if prev_close > 0 else 0
    pct_prev = (vol_today / prev_volume * 100) if prev_volume > 0 else 0
    
    if sinyal == "BELI":
        return f"Saham melesat {chg_prev:+.1f}% (di atas target min {bpjs_min_chg}%) dengan volume pagi mencapai {pct_prev:.0f}% dari total volume kemarin. Didukung transaksi likuid Rp {value_today/1e9:.1f} Miliar dan harga bertahan di atas MA5, menjadikannya sangat kuat untuk taktik Beli Pagi Jual Sore."
    return f"Saham belum direkomendasikan untuk BPJS karena kenaikan hari ini ({chg_prev:+.1f}%) atau volume pagi hari ini ({pct_prev:.0f}%) belum memenuhi syarat akumulasi minimum."

def buat_analisis_singkat_ara(ind, harga, sinyal, chg, ara_min_chg, ara_min_val):
    if ind is None or not ind:
        return "Data tidak mencukupi untuk menganalisis taktik ARA."
    
    prev_volume = ind.get("prev_volume", 0)
    vol_ma20 = ind.get("vol_ma20", 1)
    chg_kemarin = ind.get("chg_kemarin", 0.0)
    value_today = ind.get("value_today", 0)
    
    if sinyal == "BELI":
        return f"Terjadi akumulasi volume raksasa kemarin ({prev_volume / vol_ma20:.1f}x lipat dari rata-rata MA20) dengan return kemarin {chg_kemarin:+.1f}%. Hari ini didukung oleh aliran uang besar (Smart Money) senilai Rp {value_today/1e9:.1f} Miliar dan harga sedang breakout di atas MA5. Potensi melesat tinggi mengejar batas ARA!"
    return f"Saham belum terdeteksi mengalami akumulasi volume bandar kemarin atau aliran dana besar hari ini (saat ini Rp {value_today/1e9:.1f} Miliar, target min {ara_min_val} Miliar)."

def buat_analisis_singkat_bsjp(ind, harga, sinyal, chg, max_rsi, min_val):
    if ind is None or not ind:
        return "Data tidak mencukupi untuk menganalisis taktik BSJP."
    rsi = ind.get("RSI", 50)
    if sinyal == "BSJP":
        return f"Saham terdeteksi mengalami akumulasi akhir sesi dengan RSI aman {rsi:.0f} (< {max_rsi}) dan MACD positif. Sangat cocok dibeli sebelum tutup pasar (15:50 WIB) untuk dijual besok pagi."
    return f"Saham belum direkomendasikan untuk BSJP karena RSI berada di {rsi:.0f} (target < {max_rsi}) atau belum memenuhi kriteria volume akumulasi sore."

def generate_outcome_narrative(entry):
    sym = entry["symbol"]
    ret = entry.get("return_pct")
    outcome = entry.get("outcome")
    taktik = entry.get("sinyal")
    t_pct = entry.get("target_pct", 5.0)
    s_pct = entry.get("sl_pct", 3.0)
    
    if outcome is None or ret is None:
        return f"⏳ **Saham {sym}** ({taktik}): Menunggu data perdagangan hari bursa berikutnya untuk dievaluasi."
        
    if "HIT_TARGET" in outcome or "PROFIT" in outcome:
        return f"🟢 **Saham {sym}** ({taktik}): Terbukti **BERHASIL** karena naik hingga **{ret:+.2f}%** (melewati target TP {t_pct}%). Jika Anda mengikuti saran scanner, Anda pasti cuan! 💰"
    elif "HIT_SL" in outcome or "LOSS" in outcome:
        return f"🔴 **Saham {sym}** ({taktik}): **MELESET** karena harga turun hingga **{ret:+.2f}%** (menembus batas SL -{s_pct}%). Tekanan jual pasar lebih kuat hari ini, disiplin cut loss menyelamatkan modal Anda dari kerugian dalam. 🛡️"
    else:
        return f"🟡 **Saham {sym}** ({taktik}): Ditutup stabil dengan return **{ret:+.2f}%**."

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
# FETCH DATA FLOW
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=86400, show_spinner=False)
def fetch_watchlist_goapi(mode):
    try:
        if mode == "gainer":
            r = requests.get(f"{BASE_URL}/stock/idx/top_gainer",   headers=GOAPI_HEADERS, timeout=10)
        elif mode == "loser":
            r = requests.get(f"{BASE_URL}/stock/idx/top_loser",    headers=GOAPI_HEADERS, timeout=10)
        else:
            r = requests.get(f"{BASE_URL}/stock/idx/trending",     headers=GOAPI_HEADERS, params={"type":"volume"}, timeout=10)
        return [d["symbol"] for d in r.json().get("data",{}).get("results",[])]
    except:
        return []

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_batch_yfinance(syms_tuple):
    symbols = list(syms_tuple)
    tickers = [f"{s}.JK" for s in symbols]
    result  = {}
    try:
        raw = yf.download(tickers, period="6mo", interval="1d", auto_adjust=True, progress=False, threads=True)
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
    except:
        pass
    return result

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR CONFIGURATION (Clean & Beginner-Focused)
# ─────────────────────────────────────────────────────────────────────────────
st.sidebar.markdown("## ⚙️ Setelan Utama")

taktik_trading = st.sidebar.selectbox(
    "🎯 Taktik Trading:",
    ["Swing & Scalping Klasik", "⚡ BPJS Agresif (Custom +2%)", "🎯 ARA Hunter (High Momentum)", "🟣 BSJP (Beli Sore Jual Pagi)"]
)

modal_per_saham = st.sidebar.number_input(
    "💰 Modal per Saham (Rp):",
    min_value=50_000, max_value=50_000_000,
    value=1_000_000, step=100_000, format="%d"
)

# Advanced parameters collapsed to keep it beginner-friendly
with st.sidebar.expander("⚙️ Setelan Lanjutan", expanded=False):
    mode_saham = st.radio("📊 Sumber Saham:", [
        "🔥 Top Gainer (GoAPI)",
        "📉 Top Loser / Rebound (GoAPI)",
        "🌊 Trending Volume (GoAPI)",
        "💎 LQ45 + Populer (Offline)",
        "✏️ Manual"
    ], index=0)
    
    max_saham = st.slider("📋 Jumlah Saham", 5, 50, 20)
    
    target_pct = st.slider("🎯 Target Profit (%)", 1.0, 20.0, 5.0, 0.5)
    sl_pct     = st.slider("🛑 Stop Loss (%)", 1.0, 10.0, 3.0, 0.5)
    
    bpjs_min_chg = st.slider("⚡ Min Kenaikan BPJS (%)", 1.0, 5.0, 2.0, 0.5)
    bpjs_min_val = st.slider("⚡ Min Transaksi BPJS (Miliar Rp)", 1, 10, 2, 1)
    
    ara_min_chg = st.slider("🎯 Min Ret Kemarin ARA (%)", 1.0, 8.0, 3.0, 0.5)
    ara_min_val = st.slider("🎯 Min Transaksi ARA (Miliar Rp)", 1, 20, 5, 1)
    
    bsjp_max_rsi = st.slider("🟣 Max RSI BSJP", 45, 65, 58, 1)
    bsjp_min_val = st.slider("🟣 Min Transaksi BSJP (Miliar Rp)", 1, 10, 2, 1)
    
    manual_input = ""
    if "Manual" in mode_saham:
        manual_input = st.text_area(
            "Kode saham (pisahkan koma):",
            "BBCA,BBRI,TLKM,GOTO,BREN,ASII,MDKA,AMMN,ANTM,BMRI"
        )

if st.sidebar.button("🔄 Refresh & Pindai Ulang", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("""
---
**📚 Panduan Singkat:**
* 🟢 **BELI** = Saham siap dieksekusi hari ini.
* 🟣 **BSJP** = Beli sore menjelang tutup, jual besok pagi.
* 🔴 **JUAL** = Keluar / Potong Rugi (Cut Loss).
* ⏳ **TUNGGU** = Belum ada momentum aman.
""")

# ─────────────────────────────────────────────────────────────────────────────
# HEADER & BURSA STATUS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
<h1>📈 Scalping IHSG — Dashboard Pemula</h1>
<p>Scanner Saham Otomatis & Sederhana untuk Keputusan Cepat Tanpa Bingung</p>
</div>
""", unsafe_allow_html=True)

# Sesi Status
sesi_status, sesi_label = get_status_pasar()
now_str = datetime.now(WIB).strftime("%H:%M:%S WIB — %A, %d %B %Y")
css_map = {"buka": "pasar-buka", "tutup": "pasar-tutup", "preopen": "pasar-preopen"}
st.markdown(f'<div class="{css_map[sesi_status]}">{sesi_label} &nbsp;|&nbsp; 🕐 {now_str}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DATA PIPELINE EXECUTION
# ─────────────────────────────────────────────────────────────────────────────
with st.spinner("📡 Mengambil daftar saham teraktif..."):
    if "Manual" in mode_saham:
        symbols = [s.strip().upper() for s in manual_input.split(",") if s.strip()]
    elif "LQ45" in mode_saham:
        symbols = LQ45_POPULER[:max_saham]
    elif "Gainer" in mode_saham:
        raw = fetch_watchlist_goapi("gainer")
        symbols = (raw or LQ45_POPULER)[:max_saham]
    elif "Loser" in mode_saham:
        raw = fetch_watchlist_goapi("loser")
        symbols = (raw or LQ45_POPULER)[:max_saham]
    else:
        raw = fetch_watchlist_goapi("trending")
        symbols = (raw or LQ45_POPULER)[:max_saham]

symbols = symbols[:max_saham]

with st.spinner(f"📥 Mengunduh data pasar untuk {len(symbols)} saham..."):
    all_data = fetch_batch_yfinance(tuple(symbols))

if not all_data:
    st.error("❌ Gagal terhubung ke server data. Silakan klik 'Refresh & Pindai Ulang' di sidebar.")
    st.stop()

# Evaluate signals
results = []
for sym in symbols:
    df = all_data.get(sym)
    if df is None or df.empty:
        continue
    ind   = hitung_indikator(df)
    harga = float(df["close"].iloc[-1])
    prev  = float(df["close"].iloc[-2]) if len(df) > 1 else harga
    vol   = float(df["volume"].iloc[-1]) if "volume" in df.columns else 0
    chg   = (harga - prev) / prev * 100 if prev > 0 else 0
    
    if taktik_trading == "⚡ BPJS Agresif (Custom +2%)":
        sinyal, alasan, bs_count = tentukan_sinyal_bpjs_agresif(ind, harga, bpjs_min_chg, bpjs_min_val)
        confidence, conf_label, conf_color = hitung_confidence_bpjs(bs_count)
    elif taktik_trading == "🎯 ARA Hunter (High Momentum)":
        sinyal, alasan, bs_count = tentukan_sinyal_ara_hunter(ind, harga, ara_min_chg, ara_min_val)
        confidence, conf_label, conf_color = hitung_confidence_ara(bs_count)
    elif taktik_trading == "🟣 BSJP (Beli Sore Jual Pagi)":
        sinyal, alasan, bs_count = tentukan_sinyal_bsjp(ind, harga, bsjp_max_rsi, bsjp_min_val)
        confidence, conf_label, conf_color = hitung_confidence_bsjp(bs_count)
    else:
        sinyal, alasan = tentukan_sinyal_classic(ind, harga, sesi_status)
        confidence, conf_label, conf_color = hitung_confidence_classic(ind, harga, sinyal)
        
    lot = hitung_lot(modal_per_saham, harga)
    k   = kalkulator(harga, lot, target_pct, sl_pct)
    
    results.append({
        "symbol": sym, "harga": harga, "chg": chg, "vol": vol,
        "sinyal": sinyal, "alasan": alasan, "ind": ind or {},
        "lot": lot, "k": k, "confidence": confidence,
        "conf_label": conf_label, "conf_color": conf_color
    })

# Sort results (BUY signals first, then by highest confidence score)
urutan = {"BELI": 0, "BSJP": 1, "JUAL": 2, "TUNGGU": 3}
results.sort(key=lambda x: (urutan.get(x["sinyal"], 9), -x["confidence"]))

# Auto-save signal history
new_signals = record_signals(results, modal_per_saham, target_pct, sl_pct)
if new_signals > 0:
    st.toast(f"📜 {new_signals} sinyal trading baru dicatat!", icon="✅")

# ─────────────────────────────────────────────────────────────────────────────
# UI LAYOUT COMPONENT
# ─────────────────────────────────────────────────────────────────────────────
def render_kartu_pemula(r, is_top=False):
    sym    = r["symbol"]
    harga  = r["harga"]
    chg    = r["chg"]
    sinyal = r["sinyal"]
    lot    = r["lot"]
    k      = r["k"]
    ind    = r["ind"]

    if sinyal == "BELI":
        css, tag_css, tag_txt = "card-beli", "tag-green", "🟢 BELI"
    elif sinyal == "BSJP":
        css, tag_css, tag_txt = "card-bsjp", "tag-purple", "🟣 BSJP (Beli Sore)"
    elif sinyal == "JUAL":
        css, tag_css, tag_txt = "card-jual", "tag-red", "🔴 JUAL / CUT LOSS"
    else:
        css, tag_css, tag_txt = "card-tunggu", "tag-gray", "⏳ TUNGGU"

    if is_top and sinyal in ("BELI", "BSJP"):
        tag_txt = "🏆 PILIHAN UTAMA · " + tag_txt

    chg_col  = "#10b981" if chg >= 0 else "#ef4444"
    chg_sign = "+" if chg >= 0 else ""
    
    # 1. Custom indicator pills based on Tactic
    if taktik_trading == "⚡ BPJS Agresif (Custom +2%)":
        prev_close  = ind.get("prev_close", harga)
        open_today  = ind.get("open_today", harga)
        prev_volume = ind.get("prev_volume", 0)
        vol_today   = ind.get("volume", 0)
        ma5         = ind.get("MA5", harga)
        value_today = ind.get("value_today", 0)
        
        chg_prev   = ((harga - prev_close) / prev_close * 100) if prev_close > 0 else 0
        cond_chg   = chg_prev >= bpjs_min_chg
        cond_ma5   = harga >= ma5
        cond_green = harga >= open_today
        cond_vol   = vol_today >= 0.2 * prev_volume if prev_volume > 0 else False
        cond_val   = value_today >= bpjs_min_val * 1_000_000_000
        
        pill_chg   = f"Naik {chg_prev:+.1f}% {'✅' if cond_chg else '⚠️'}"
        pill_ma5   = f"MA5 {'✅' if cond_ma5 else '⚠️'}"
        pill_green = f"Candle {'Hijau ✅' if cond_green else 'Merah ⚠️'}"
        pct_prev   = (vol_today / prev_volume * 100) if prev_volume > 0 else 0
        pill_vol   = f"Vol Pagi {pct_prev:.0f}% {'✅' if cond_vol else '⚠️'}"
        pill_val   = f"Value {value_today/1e9:.1f}B {'✅' if cond_val else '⚠️'}"
        
        pills_html = f"<div><span class='ind-pill'>{pill_chg}</span><span class='ind-pill'>{pill_ma5}</span><span class='ind-pill'>{pill_green}</span><span class='ind-pill'>{pill_vol}</span><span class='ind-pill'>{pill_val}</span></div>"
        analisis   = buat_analisis_singkat_bpjs(ind, harga, sinyal, chg, bpjs_min_chg, bpjs_min_val)
        
    elif taktik_trading == "🎯 ARA Hunter (High Momentum)":
        prev_close  = ind.get("prev_close", harga)
        prev_volume = ind.get("prev_volume", 0)
        vol_today   = ind.get("volume", 0)
        vol_ma20    = ind.get("vol_ma20", 1)
        ma5         = ind.get("MA5", harga)
        ma50        = ind.get("MA50", harga)
        value_today = ind.get("value_today", 0)
        high_today  = ind.get("high", harga)
        low_today   = ind.get("low", harga)
        
        chg_prev = ind.get("chg_kemarin", 0.0)
        
        cond_vol_kemarin = prev_volume > 1.8 * vol_ma20 if vol_ma20 > 0 else False
        cond_smart_money = vol_today >= 0.15 * prev_volume if prev_volume > 0 else False
        cond_chg_prev    = chg_prev >= ara_min_chg
        cond_breakout    = high_today >= ma5
        cond_support     = low_today >= 0.95 * ma50
        cond_val         = value_today >= ara_min_val * 1_000_000_000
        
        pill_vol_k   = f"Akumulasi Kemarin {'✅' if cond_vol_kemarin else '⚠️'}"
        pill_smart   = f"Smart Money {'✅' if cond_smart_money else '⚠️'}"
        pill_chg_k   = f"Kemarin {chg_prev:+.1f}% {'✅' if cond_chg_prev else '⚠️'}"
        pill_break   = f"Breakout MA5 {'✅' if cond_breakout else '⚠️'}"
        pill_support = f"Support MA50 {'✅' if cond_support else '⚠️'}"
        
        pills_html = f"<div><span class='ind-pill'>{pill_vol_k}</span><span class='ind-pill'>{pill_smart}</span><span class='ind-pill'>{pill_chg_k}</span><span class='ind-pill'>{pill_break}</span><span class='ind-pill'>{pill_support}</span></div>"
        analisis   = buat_analisis_singkat_ara(ind, harga, sinyal, chg, ara_min_chg, ara_min_val)
        
    elif taktik_trading == "🟣 BSJP (Beli Sore Jual Pagi)":
        rsi    = ind.get("RSI", 50)
        ema9   = ind.get("EMA9", harga)
        ema21  = ind.get("EMA21", harga)
        mh     = ind.get("MACD_hist", 0)
        vol    = ind.get("volume", 0)
        volma  = ind.get("vol_ma20", vol or 1)
        value_today = ind.get("value_today", 0)
        
        cond_rsi = rsi < bsjp_max_rsi
        cond_bull = ema9 > ema21
        cond_macd = mh > 0
        cond_vol = vol >= volma * 1.10 if volma > 0 else False
        cond_val = value_today >= bsjp_min_val * 1_000_000_000
        
        pill_rsi   = f"RSI {rsi:.0f} {'✅' if cond_rsi else '⚠️'}"
        pill_bull  = f"EMA9>21 {'✅' if cond_bull else '⚠️'}"
        pill_macd  = f"MACD+ {'✅' if cond_macd else '⚠️'}"
        pill_vol   = f"Vol Spike {'✅' if cond_vol else '⚠️'}"
        pill_val   = f"Value {value_today/1e9:.1f}B {'✅' if cond_val else '⚠️'}"
        
        pills_html = f"<div><span class='ind-pill'>{pill_rsi}</span><span class='ind-pill'>{pill_bull}</span><span class='ind-pill'>{pill_macd}</span><span class='ind-pill'>{pill_vol}</span><span class='ind-pill'>{pill_val}</span></div>"
        analisis   = buat_analisis_singkat_bsjp(ind, harga, sinyal, chg, bsjp_max_rsi, bsjp_min_val)
    else:
        rsi      = ind.get("RSI", 50)
        ema9     = ind.get("EMA9", harga)
        ema21    = ind.get("EMA21", harga)
        ema50    = ind.get("EMA50", harga)
        mh       = ind.get("MACD_hist", 0)
        rsi_col  = "#ef4444" if rsi > 70 else ("#10b981" if rsi < 40 else "#f59e0b")
        ema50_col = "#10b981" if harga > ema50 else "#ef4444"
        
        pills_html = f"<div><span class='ind-pill'>RSI <b style='color:{rsi_col}'>{rsi:.0f}</b></span><span class='ind-pill'>{'EMA9>21 ✅' if ema9>ema21 else 'EMA9<21 ⚠️'}</span><span class='ind-pill'>{'MACD+ ✅' if mh>0 else 'MACD- ⚠️'}</span><span class='ind-pill'>EMA50 <b style='color:{ema50_col}'>{ema50:.0f}</b></span></div>"
        analisis   = buat_analisis_singkat_classic(ind, harga, sinyal, chg)

    confidence = r.get("confidence", 50)
    conf_label = r.get("conf_label", "Cukup")
    conf_color = r.get("conf_color", "#cbd5e1")

    # 2. Integrated Calculator inside Card
    calc_html = ""
    if k and lot > 0:
        profit_color = "#10b981" if k["profit"] >= 0 else "#ef4444"
        calc_html = f"""<div class="card-kalkulator">
🧮 <b>Rencana Eksekusi:</b><br>
• Jumlah Beli: <b>{lot} lot</b> ({lot*100:,} lbr) | Modal: <b>Rp {k['modal']:,.0f}</b><br>
• Target Jual (TP): <b style="color:#10b981">Rp {snap_fraksi(k['ht']):,}</b> (+{target_pct}%)<br>
• Batas Rugi (SL): <b style="color:#ef4444">Rp {snap_fraksi(k['hsl']):,}</b> (-{sl_pct}%)<br>
• Estimasi Bersih: <span style="color:{profit_color}; font-weight:700">Untung Rp {k['profit']:,.0f}</span> / <span style="color:#ef4444; font-weight:700">Rugi Rp {abs(k['rugi']):,.0f}</span>
</div>"""
    elif lot == 0:
        calc_html = f"""<div class="card-kalkulator" style="border-left: 3px solid #f59e0b; background: rgba(245, 158, 11, 0.05)">
⚠️ <b>Modal Tidak Cukup:</b><br>
Minimal modal untuk 1 lot ({sym}) adalah <b>Rp {harga*100:,.0f}</b>.
</div>"""

    card_html = f"""<div class="{css}">
<div style="display:flex;justify-content:space-between;align-items:flex-start">
<span class="card-sym">{sym}</span>
<span class="{tag_css}">{tag_txt}</span>
</div>
<p class="card-price">Rp {harga:,.0f}</p>
<p style="font-size:0.88rem;color:{chg_col};margin:0 0 6px 0;font-weight:700">
{chg_sign}{chg:.2f}% &nbsp;<span style="color:#94a3b8;font-weight:400">Vol {r['vol']:,.0f}</span>
</p>
<div style="margin: 8px 0 10px 0;">
<div style="display:flex; justify-content:space-between; font-size:0.75rem; color:#cbd5e1; margin-bottom:3px;">
<span>📊 Kekuatan Sinyal</span>
<span style="font-weight:700; color:{conf_color}">{confidence}% · {conf_label}</span>
</div>
<div style="background: rgba(255,255,255,0.1); border-radius: 4px; height: 6px; width: 100%; overflow: hidden;">
<div style="background: {conf_color}; width: {confidence}%; height: 100%; border-radius: 4px;"></div>
</div>
</div>
{pills_html}
<p style="font-size:0.83rem;color:#e2e8f0;margin:12px 0 0 0;line-height:1.5;">{analisis}</p>
{calc_html}
</div>"""

    st.markdown(card_html, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# VIEW TABS & RENDER
# ─────────────────────────────────────────────────────────────────────────────
tab_dash, tab_hist = st.tabs(["📊 Hasil Pindai Saham", "📜 Riwayat Sinyal & Win-Rate"])

with tab_dash:
    # Split into Beli/BSJP vs Wait/Sell
    beli_results  = [r for r in results if r["sinyal"] in ("BELI", "BSJP")]
    other_results = [r for r in results if r["sinyal"] not in ("BELI", "BSJP")]

    # Dynamic Trade Plan Execution Guide based on Tactic
    guide_html = ""
    if taktik_trading == "Swing & Scalping Klasik":
        guide_html = """<div style="background: rgba(59, 130, 246, 0.05); border-left: 4px solid #3b82f6; border-radius: 8px; padding: 16px; margin-bottom: 20px;">
💡 <b>Panduan Eksekusi - Swing & Scalping Klasik:</b><br>
• <b>Jam Eksekusi:</b> Beli pagi (09:00 - 09:30 WIB) or sore (14:30 - 15:30 WIB).<br>
• <b>Caranya:</b> Entry beli saat sinyal 🟢 <b>BELI</b> muncul. Pasang target TP 5% dan SL 3% otomatis di sekuritas Anda. Hold santai 1-5 hari sampai target kena.
</div>"""
    elif taktik_trading == "⚡ BPJS Agresif (Custom +2%)":
        guide_html = """<div style="background: rgba(16, 185, 129, 0.05); border-left: 4px solid #10b981; border-radius: 8px; padding: 16px; margin-bottom: 20px;">
💡 <b>Panduan Eksekusi - BPJS Agresif (Beli Pagi Jual Sore):</b><br>
• <b>Jam Eksekusi:</b> <b>09:00 - 09:10 WIB</b> (10 menit pertama saat pembukaan bursa).<br>
• <b>Caranya:</b> Cari saham berstatus 🟢 <b>BELI</b> yang bergerak naik cepat (volume tinggi + bid tebal). HAKA cepat, langsung antrekan jual otomatis di target <b>+2% s.d +3%</b>. Jual sore hari sebelum tutup jika belum tersentuh. Jangan di-hold menginap!
</div>"""
    elif taktik_trading == "🎯 ARA Hunter (High Momentum)":
        guide_html = """<div style="background: rgba(245, 158, 11, 0.05); border-left: 4px solid #f59e0b; border-radius: 8px; padding: 16px; margin-bottom: 20px;">
💡 <b>Panduan Eksekusi - ARA Hunter (High Momentum):</b><br>
• <b>Jam Eksekusi:</b> Buka pagi (09:01 - 09:15 WIB) atau konfirmasi siang (11:15 / 13:30 WIB).<br>
• <b>Caranya:</b> Cari saham breakout MA5 dengan akumulasi kemarin & smart money masuk hari ini. Batasi pembelian jika harga sudah terbang >20%. Jika saham berhasil mengunci ARA (Auto Reject Atas) di akhir hari, simpan/hold untuk dijual besok pagi saat gap up.
</div>"""
    elif taktik_trading == "🟣 BSJP (Beli Sore Jual Pagi)":
        guide_html = """<div style="background: rgba(168, 85, 247, 0.05); border-left: 4px solid #a855f7; border-radius: 8px; padding: 16px; margin-bottom: 20px;">
💡 <b>Panduan Eksekusi - BSJP (Beli Sore Jual Pagi):</b><br>
• <b>Jam Eksekusi:</b> <b>15:50 - 16:00 WIB</b> (Pre-closing / beberapa menit menjelang bursa tutup).<br>
• <b>Caranya:</b> Beli saham bersinyal 🟣 <b>BSJP</b> di sore hari saat harga closing terbentuk. Simpan semalam, lalu langsung jual di keesokan paginya pukul <b>09:00 - 09:05 WIB</b> saat terjadi lonjakan pembukaan (gap up).
</div>"""

    if guide_html:
        st.markdown(guide_html, unsafe_allow_html=True)

    if beli_results:
        st.markdown('<div class="section-header">🟢 Saham Rekomendasi (Siap Beli)</div>', unsafe_allow_html=True)
        cols = st.columns(2)
        for i, r in enumerate(beli_results):
            with cols[i % 2]:
                render_kartu_pemula(r, is_top=(i == 0))
        st.markdown("---")
    else:
        st.info("⏳ Belum ada saham yang masuk kriteria beli saat ini. Pasar sedang lesu atau konsolidasi. Silakan perbarui data di sidebar beberapa saat lagi.")
        st.markdown("---")

    if other_results:
        with st.expander(f"📋 Pantau Saham Lainnya — {len(other_results)} Saham (Belum Aman / Jual)"):
            cols2 = st.columns(2)
            for i, r in enumerate(other_results):
                with cols2[i % 2]:
                    render_kartu_pemula(r, is_top=False)

    # Simplified summary table
    st.markdown("---")
    st.markdown("### 📋 Tabel Ringkasan Keputusan")
    
    rows = []
    for r in results:
        k = r["k"]
        rows.append({
            "Kode Saham":  r["symbol"],
            "Harga":       f"Rp {r['harga']:,.0f}",
            "Perubahan":   f"{'+' if r['chg']>=0 else ''}{r['chg']:.2f}%",
            "Taktik Sinyal": r["sinyal"],
            "Kekuatan":    f"{r['confidence']}% {r['conf_label']}",
            "Rekomendasi Lot": r["lot"] if r["lot"] > 0 else "Modal Kurang",
            "Harga Beli":  f"Rp {r['harga']:,.0f}",
            "Target Jual": f"Rp {snap_fraksi(k['ht']):,}" if k else "-",
            "Batas Rugi":  f"Rp {snap_fraksi(k['hsl']):,}" if k else "-"
        })

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.markdown(
        f"<small style='color:#64748b'>⏱️ Pemindaian terakhir: {now_str} · "
        f"Data IHSG delay harian yfinance ~15 menit · Berhasil menganalisis {len(results)}/{len(symbols)} saham</small>",
        unsafe_allow_html=True
    )

with tab_hist:
    st.markdown("### 📜 Evaluasi Akurasi Sinyal")
    
    col_eval_btn, col_eval_status = st.columns([1, 3])
    with col_eval_btn:
        if st.button("🔄 Hitung Akurasi Sinyal", use_container_width=True):
            with st.spinner("Mengevaluasi..."):
                hist, changed = evaluate_history()
                if changed > 0:
                    st.success(f"Akurasi {changed} sinyal baru berhasil dihitung!")
                else:
                    st.info("Seluruh sinyal historis sudah dihitung.")
                st.rerun()

    history = load_history()
    
    if not history:
        st.info("Belum ada riwayat sinyal tersimpan. Sistem akan mencatat sinyal secara otomatis setelah Anda melakukan pemindaian.")
    else:
        buy_signals = [h for h in history if h["sinyal"] in ("BELI", "BSJP")]
        eval_buys = [h for h in buy_signals if h.get("outcome") is not None]
        
        if eval_buys:
            wins = sum(1 for h in eval_buys if "✅" in h["outcome"] or "PROFIT" in h["outcome"])
            win_rate = (wins / len(eval_buys)) * 100
            returns = [h["return_pct"] for h in eval_buys if h["return_pct"] is not None]
            avg_return = sum(returns) / len(returns) if returns else 0.0
            total_profit = sum(h["est_profit_rp"] for h in eval_buys if h.get("est_profit_rp") is not None)
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("📊 Total Sinyal", len(history))
            c2.metric("🎯 Win Rate (BELI)", f"{win_rate:.1f}%", f"{wins}/{len(eval_buys)} Saham")
            c3.metric("📈 Rata-rata Return", f"{avg_return:+.2f}%")
            
            prof_color = "normal" if total_profit >= 0 else "inverse"
            c4.metric("💰 Estimasi Keuntungan Realisasi", 
                      f"Rp {total_profit:,.0f}" if total_profit >= 0 else f"-Rp {abs(total_profit):,.0f}",
                      delta_color=prof_color)
        else:
            c1, c2, c3 = st.columns(3)
            c1.metric("📊 Total Sinyal", len(history))
            c2.metric("🎯 Win Rate (BELI)", "0.0%", "0/0 Saham")
            c3.metric("📈 Rata-rata Return", "0.00%")
            st.warning("⚠️ Metrik akurasi belum muncul karena seluruh sinyal di bawah masih berjalan (running) dan belum ditutup di hari berikutnya.")
            
        st.markdown("---")
        
        # Friendly Narrative Outcomes - Always Visible
        st.markdown("#### 📝 Rapor Kinerja Sinyal Terbaru")
        sorted_history = sorted(history, key=lambda x: x["scan_time"], reverse=True)
        for entry in sorted_history[:5]:
            st.info(generate_outcome_narrative(entry))
        st.markdown("---")
            
        df_hist = pd.DataFrame(history)
        df_display = df_hist.sort_values(by="scan_time", ascending=False)
        
        show_cols = ["scan_time", "symbol", "sinyal", "harga_signal", "confidence", "target_harga", "sl_harga", "harga_close", "return_pct", "outcome"]
        show_cols = [c for c in show_cols if c in df_display.columns]
        df_display = df_display[show_cols]
        
        df_display.columns = [
            "Waktu Scan", "Kode", "Sinyal", "Harga Masuk", "Kekuatan", "Target TP", "Batas SL", "Harga Close", "Return %", "Hasil Evaluasi"
        ]
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
