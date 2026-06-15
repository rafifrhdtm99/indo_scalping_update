import yfinance as yf
import pandas as pd
import ta
import json
import os
import urllib.request
from datetime import datetime
import pytz
import sys

# Configure stdout/stderr encoding to prevent crashes when printing emojis on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Constants
WIB           = pytz.timezone("Asia/Jakarta")
FEE_BELI      = 0.0010
FEE_JUAL      = 0.0020
HISTORY_FILE  = os.path.join(os.path.dirname(__file__), "signal_history.json")

LQ45_POPULER = [
    # --- BLUE CHIPS & LARGE CAP ---
    "BBCA", "BBRI", "BMRI", "BBNI", "TLKM", "ASII", "GOTO", "BREN", "AMMN", "ANTM",
    "UNVR", "ICBP", "INDF", "KLBF", "SIDO", "ASRI", "BSDE", "CTRA", "PWON", "SMRA",
    # --- BANKING & FINANCE (CONV & DIGITAL) ---
    "BBTN", "BRIS", "BDMN", "ARTO", "BBYB", "BBHI", "MEGA", "CFIN", "ADMF", "PNBN",
    # --- ENERGY, OIL, & GAS ---
    "ADRO", "PTBA", "ITMG", "HRUM", "MEDC", "ELSA", "ENRG", "PGAS", "AKRA", "INDY",
    "PGEO", "KEEN", "ADMR", "GEMS", "RAJA", "TOBA", "APEX",
    # --- METALS, MINERALS, & MINING ---
    "INCO", "TINS", "MDKA", "BRMS", "MBMA", "NCKL", "BUMI", "DEWA", "DOID", "KKGI",
    # --- INFRASTRUCTURE & CONSTRUCTION ---
    "JSMR", "ADHI", "PTPP", "WIKA", "WSKT", "SSIA", "META", "BALI", "TOWR", "TBIG",
    # --- RETAIL, HEALTHCARE, & TOURISM ---
    "ACES", "MAPI", "ERAA", "MAPA", "LPPF", "RALS", "MIKA", "HEAL", "SILO", "PANR",
    # --- CONSUMER STAPLES & AGRICULTURE ---
    "MYOR", "ROTI", "ULTJ", "CPIN", "JPFA", "AALI", "LSIP", "SSMS", "TAPG", "DSNG",
    # --- BASIC MATERIALS & CHEMICALS ---
    "SMGR", "INTP", "ESSA", "SRTG", "BRPT", "TPIA", "INKP", "TKIM", "UNTR", "GJTL",
    "AUTO", "SMSM", "MASA", "IMAS", "WOOD",
    # --- PROPERTIES & URBAN DEVELOPMENT ---
    "KIJA", "DILD", "DMAS", "MTLA", "PPRO",
    # --- TECHNOLOGY & DIGITAL MEDIA ---
    "EMTK", "MNCN", "SCMA", "BUKA", "WIRG", "KIOS", "VKTR",
    # --- LOGISTICS & SHIPPING ---
    "ASSA", "SMDR", "BIRD", "BULL", "TMAS", "HAIS", "PSSI", "TPMA", "WINS",
    # --- MOMENTUM & POPULAR MID-CAPS ---
    "FILM", "DGNS", "MTDL", "BNBR", "LPKR", "MPPA", "MLPL"
]

def snap_fraksi(h):
    if h < 200:    return round(h)
    elif h < 500:  return min(round(h/2)*2, 498)
    elif h < 2000: return min(round(h/5)*5, 1995)
    elif h < 5000: return min(round(h/25)*25, 4975)
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

def record_signals(results, modal_per_saham, target_pct, sl_pct, current_taktik):
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

def hitung_indikator(df):
    try:
        df = df.copy()
        c = df["close"]
        df["RSI"]       = ta.momentum.rsi(c, window=14).fillna(50)
        df["EMA9"]      = ta.trend.ema_indicator(c, window=9).fillna(c)
        df["EMA21"]     = ta.trend.ema_indicator(c, window=21).fillna(c)
        df["EMA50"]     = ta.trend.ema_indicator(c, window=50).fillna(c)
        macd_obj        = ta.trend.MACD(c)
        df["MACD"]      = macd_obj.macd().fillna(0)
        df["MACD_hist"] = macd_obj.macd_diff().fillna(0)
        df["vol_ma20"]  = df["volume"].rolling(20).mean().fillna(df["volume"])
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

def tentukan_sinyal_classic(ind, harga):
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
    if rsi < 50:   bs+=1
    if bull:       bs+=1
    if mh > 0:     bs+=1
    if vspike:     bs+=1
    if diatas:     bs+=1
    if rsi > 72:   js+=2
    if not bull:   js+=1
    if mh < 0:     js+=1
    if not diatas: js+=1
    
    if js >= 3:    return "JUAL",   alasan
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
    if cond_chg:   bs += 1
    if cond_ma5:   bs += 1
    if cond_green: bs += 1
    if cond_vol:   bs += 1
    if cond_val:   bs += 1
    
    if bs == 5:
        return "BELI", alasan, bs
    return "TUNGGU", alasan, bs

def tentukan_sinyal_ara_hunter(ind, harga, min_chg_prev, min_val_miliar):
    if ind is None:
        return "TUNGGU", ["Data kurang"], 0
    prev_volume = ind.get("prev_volume", 0)
    vol_today   = ind.get("volume", 0)
    vol_ma20    = ind.get("vol_ma20", 1)
    ma5         = ind.get("MA5", harga)
    ma50        = ind.get("MA50", harga)
    value_today = ind.get("value_today", 0)
    high_today  = ind.get("high", harga)
    low_today   = ind.get("low", harga)
    chg_prev    = ind.get("chg_kemarin", 0.0)
    
    cond_vol_kemarin = prev_volume > 1.8 * vol_ma20 if vol_ma20 > 0 else False
    cond_smart_money = vol_today >= 0.15 * prev_volume if prev_volume > 0 else False
    cond_chg_prev    = chg_prev >= min_chg_prev
    cond_breakout    = high_today >= ma5
    cond_support     = low_today >= 0.95 * ma50
    cond_val         = value_today >= min_val_miliar * 1_000_000_000
    
    alasan = []
    bs = 0
    if cond_vol_kemarin: bs += 1
    if cond_smart_money: bs += 1
    if cond_chg_prev:    bs += 1
    if cond_breakout:    bs += 1
    if cond_support:     bs += 1
    if cond_val:         bs += 1
    
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
    if bull:     bs += 1
    if mh > 0:   bs += 1
    if rsi < max_rsi: bs += 1
    if vspike:   bs += 1
    if diatas:   bs += 1
    if cond_val: bs += 1
    
    if bs >= 4 and cond_val:
        return "BSJP", alasan, bs
    return "TUNGGU", alasan, bs

def hitung_confidence_classic(ind, harga, sinyal):
    if ind is None: return 25, "❓ Data kurang", "#6b7280"
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
    return hitung_confidence_bpjs(bs)

def hitung_confidence_bsjp(bs):
    score = int(bs * 20)
    score = max(10, min(100, score))
    if   score >= 100: label, color = "🔥 Sangat Kuat",   "#a855f7"
    elif score >= 80:  label, color = "💪 Kuat",           "#c084fc"
    elif score >= 60:  label, color = "✅ Cukup",          "#d8b4fe"
    elif score >= 40:  label, color = "⚠️ Lemah",         "#e9d5ff"
    else:              label, color = "❌ Sangat Lemah",   "#f3e8ff"
    return score, label, color

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

def fetch_batch_yfinance(symbols):
    tickers = [f"{s}.JK" for s in symbols]
    result  = {}
    try:
        raw = yf.download(tickers, period="6mo", interval="1d", auto_adjust=True, progress=False, threads=True)
        if raw.empty:
            return {}
            
        is_multi = isinstance(raw.columns, pd.MultiIndex)
        
        for sym in symbols:
            try:
                ticker_key = f"{sym}.JK"
                if is_multi:
                    if ticker_key in raw.columns.levels[1]:
                        df = raw.xs(ticker_key, axis=1, level=1).copy()
                    else:
                        continue
                else:
                    df = raw.copy()
                
                df.columns = [c.lower() for c in df.columns]
                df = df.dropna()
                if len(df) >= 20:
                    result[sym] = df
            except:
                continue
    except Exception as e:
        print(f"Error fetching data: {e}")
    return result

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Memulai Pemindaian Latar Belakang...")
    
    # Ambil list saham teraktif / LQ45
    symbols = LQ45_POPULER
    print(f"Mengunduh data untuk {len(symbols)} saham...")
    all_data = fetch_batch_yfinance(symbols)
    
    if not all_data:
        print("Gagal mengambil data dari Yahoo Finance.")
        return
        
    tactics_to_run = [
        "Swing & Scalping Klasik",
        "⚡ BPJS Agresif (Custom +2%)",
        "🎯 ARA Hunter (High Momentum)",
        "🟣 BSJP (Beli Sore Jual Pagi)"
    ]
    
    total_new = 0
    for tactic in tactics_to_run:
        results = []
        for sym in symbols:
            df = all_data.get(sym)
            if df is None or df.empty:
                continue
            ind = hitung_indikator(df)
            if ind is None:
                continue
            harga = float(df["close"].iloc[-1])
            prev = float(df["close"].iloc[-2]) if len(df) > 1 else harga
            vol = float(df["volume"].iloc[-1]) if "volume" in df.columns else 0
            chg = (harga - prev) / prev * 100 if prev > 0 else 0
            
            if tactic == "⚡ BPJS Agresif (Custom +2%)":
                sinyal, alasan, bs_count = tentukan_sinyal_bpjs_agresif(ind, harga, 2.0, 2)
                confidence, conf_label, conf_color = hitung_confidence_bpjs(bs_count)
            elif tactic == "🎯 ARA Hunter (High Momentum)":
                sinyal, alasan, bs_count = tentukan_sinyal_ara_hunter(ind, harga, 3.0, 5)
                confidence, conf_label, conf_color = hitung_confidence_ara(bs_count)
            elif tactic == "🟣 BSJP (Beli Sore Jual Pagi)":
                sinyal, alasan, bs_count = tentukan_sinyal_bsjp(ind, harga, 58, 2)
                confidence, conf_label, conf_color = hitung_confidence_bsjp(bs_count)
            else:
                sinyal, alasan = tentukan_sinyal_classic(ind, harga)
                confidence, conf_label, conf_color = hitung_confidence_classic(ind, harga, sinyal)
                
            lot = hitung_lot(500_000, harga)
            k = kalkulator(harga, lot, 5.0, 3.0)
            
            results.append({
                "symbol": sym, "harga": harga, "chg": chg, "vol": vol,
                "sinyal": sinyal, "alasan": alasan, "ind": ind or {},
                "lot": lot, "k": k, "confidence": confidence,
                "conf_label": conf_label, "conf_color": conf_color
            })
            
        new_count = record_signals(results, 500_000, 5.0, 3.0, tactic)
        total_new += new_count
        print(f"Taktik '{tactic}': {new_count} sinyal baru dicatat.")
        
    print(f"Pemindaian selesai. Total {total_new} sinyal baru dideteksi.")

if __name__ == "__main__":
    main()
