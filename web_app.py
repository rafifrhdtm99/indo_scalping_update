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
# KONFIGURASI
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Scalping IHSG by Rafif",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    "BULL","BRPT","BRMS","DEWA","BNBR","FILM","DGNS","MTDL","WIKA","WSKT",
]

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
    """Ticker tape scrolling di atas halaman"""
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
    """Widget gauge buy/sell TradingView — menampilkan 20+ indikator sekaligus"""
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
    """Mini chart candlestick untuk preview cepat"""
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
    """Load riwayat sinyal dari file JSON"""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_history(history):
    """Simpan riwayat ke file JSON"""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def record_signals(results, modal_per_saham, target_pct, sl_pct):
    """
    Simpan sinyal BELI/BSJP/JUAL saat ini ke history.
    Hanya simpan sinyal yang bukan TUNGGU.
    """
    history   = load_history()
    now       = datetime.now(WIB)
    scan_time = now.strftime("%Y-%m-%d %H:%M")
    scan_date = now.strftime("%Y-%m-%d")

    # Cek apakah scan hari ini jam ini sudah pernah disimpan (hindari duplikat)
    existing_keys = {(e["scan_date"], e["symbol"]) for e in history}

    new_count = 0
    for r in results:
        if r["sinyal"] == "TUNGGU":
            continue
        key = (scan_date, r["symbol"])
        if key in existing_keys:
            continue  # sudah tersimpan hari ini
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
            # Diisi nanti saat evaluasi
            "harga_close":    None,
            "return_pct":     None,
            "outcome":        None,   # HIT_TARGET / HIT_SL / PROFIT / LOSS / ONGOING
            "est_profit_rp":  None,
        }
        history.append(entry)
        existing_keys.add(key)
        new_count += 1

    save_history(history)
    return new_count

def evaluate_history():
    """
    Untuk setiap entri history yang belum dievaluasi,
    coba ambil harga penutupan hari berikutnya via yfinance
    dan hitung apakah sinyal akurat.
    """
    history = load_history()
    changed = 0
    today   = datetime.now(WIB).strftime("%Y-%m-%d")

    for entry in history:
        if entry.get("outcome") is not None:
            continue  # sudah dievaluasi
        if entry["scan_date"] == today:
            continue  # hari yang sama, belum bisa dievaluasi

        sym = entry["symbol"]
        try:
            # Ambil data 5 hari terakhir untuk dapat harga close setelah sinyal
            df = yf.download(f"{sym}.JK", period="5d", interval="1d",
                             auto_adjust=True, progress=False)
            if df.empty:
                continue
            df.index = pd.to_datetime(df.index)
            # Cari harga close pada hari SETELAH scan_date
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
            else:  # JUAL
                outcome = "TURUN ✅" if ret < 0 else "NAIK ❌"

            entry["outcome"]       = outcome
            entry["est_profit_rp"] = round(ret / 100 * entry["modal"]) if entry["modal"] else None
            changed += 1
        except:
            continue

    if changed:
        save_history(history)
    return history, changed

def hitung_confidence(ind, harga, sinyal):
    """
    Hitung confidence score 0–100 berdasarkan kekuatan indikator.
    Semakin banyak indikator yang selaras → semakin tinggi skor.
    """
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
        # RSI (max 25) — makin rendah makin kuat untuk BELI
        if   rsi < 30: score += 25
        elif rsi < 40: score += 20
        elif rsi < 50: score += 14
        elif rsi < 55: score += 7
        # EMA9 vs EMA21 (max 20)
        if ema9 > ema21:
            margin = (ema9 - ema21) / ema21 * 100
            score += min(20, int(10 + margin * 5))
        # EMA50 alignment (max 15) — harga di atas EMA50 = trend besar bullish
        if harga > ema50: score += 15
        elif harga > ema50 * 0.98: score += 7
        # MACD histogram (max 20)
        if mh > 0:
            score += 10
            if macd > 0: score += 10   # MACD line juga positif = lebih kuat
        # Volume spike (max 20)
        if volma > 0:
            ratio = vol / volma
            if   ratio >= 2.0: score += 20
            elif ratio >= 1.5: score += 15
            elif ratio >= 1.2: score += 10
            elif ratio >= 1.0: score += 5

    elif sinyal == "JUAL":
        # Untuk JUAL: confidence = seberapa yakin ini memang waktu jual
        if   rsi > 80: score += 25
        elif rsi > 70: score += 18
        elif rsi > 60: score += 8
        if ema9 < ema21:
            margin = (ema21 - ema9) / ema21 * 100
            score += min(20, int(10 + margin * 5))
        if harga < ema50: score += 15
        if mh < 0: score += 20
        if vol > volma * 1.2: score += 20  # volume konfirmasi jual

    else:  # TUNGGU
        # Confidence rendah karena sinyal campur
        score = max(20, min(45, int(50 - abs(rsi - 50))))

    score = max(10, min(100, score))

    if   score >= 80: label, color = "🔥 Sangat Kuat",   "#22c55e"
    elif score >= 65: label, color = "💪 Kuat",           "#84cc16"
    elif score >= 50: label, color = "✅ Cukup",          "#f59e0b"
    elif score >= 35: label, color = "⚠️ Lemah",         "#f97316"
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

    # 1. ANALISIS TREN (TREN BESAR & TREN PENDEK)
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

    # 2. ANALISIS MOMENTUM (RSI & MACD)
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

    # 3. ANALISIS VOLUME
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

    # 4. SARAN AKSI & KESIMPULAN
    if sinyal == "BELI":
        aksi_txt = "Ini adalah momen yang baik untuk melakukan entri <b>BELI</b> guna memanfaatkan momentum kenaikan cepat (scalping)."
    elif sinyal == "BSJP":
        aksi_txt = "Akumulasi volume di akhir sesi mendukung entri <b>BSJP</b> (Beli Sore Jual Pagi) dengan target jual di pembukaan esok hari."
    elif sinyal == "JUAL":
        if rsi < 35:
            aksi_txt = "Meskipun RSI sudah jenuh jual, tren jangka pendek masih melemah. Disarankan tetap <b>JUAL / Cut Loss</b> untuk pengamanan modal, atau tunggu konfirmasi rebound sebelum masuk kembali."
        else:
            aksi_txt = "Disarankan segera melakukan <b>JUAL / Cut Loss</b> untuk mengamankan modal dari potensi penurunan lebih lanjut."
    else: # TUNGGU
        aksi_txt = "Disarankan untuk tetap <b>Wait & See (TUNGGU)</b> terlebih dahulu sampai indikator momentum memberikan sinyal pembalikan arah yang valid."

    analisis_lengkap = f"{tren_txt} {rsi_txt} {macd_txt} {vol_txt} 🎯 {aksi_txt}"
    return analisis_lengkap

def buat_analisis_singkat_bpjs(ind, harga, sinyal, chg, bpjs_min_chg, bpjs_min_val):
    if ind is None or not ind:
        return "Data tidak mencukupi untuk melakukan analisis BPJS."
        
    prev_close = ind.get("prev_close", harga)
    open_today = ind.get("open_today", harga)
    prev_volume = ind.get("prev_volume", 0)
    vol_today = ind.get("volume", 0)
    ma5 = ind.get("MA5", harga)
    value_today = ind.get("value_today", 0)
    
    chg_prev = ((harga - prev_close) / prev_close * 100) if prev_close > 0 else 0
    cond_chg = chg_prev >= bpjs_min_chg
    cond_ma5 = harga >= ma5
    cond_green = harga >= open_today
    cond_vol = vol_today >= 0.2 * prev_volume if prev_volume > 0 else False
    cond_val = value_today >= bpjs_min_val * 1_000_000_000
    
    # Tren MA5
    ma_txt = f"Harga berada <b>{'di atas' if cond_ma5 else 'di bawah'}</b> garis Moving Average pendek (MA 5)."
    # Candle
    candle_txt = f"Candle saat ini berwarna <b>{'hijau' if cond_green else 'merah'}</b> (harga pembukaan: Rp {open_today:,.0f})."
    # Volume
    vol_ratio = (vol_today / prev_volume) if prev_volume > 0 else 0
    vol_txt = f"Volume pagi ini telah mencapai <b>{vol_ratio*100:.1f}%</b> dari volume penutupan kemarin (target 20%)."
    # Value
    val_txt = f"Nilai transaksi saat ini mencapai <b>Rp {value_today/1e9:.2f} Miliar</b> (target Rp {bpjs_min_val} Miliar)."
    
    if sinyal == "BELI":
        kesimpulan = f"🎯 Saham memenuhi seluruh kriteria BPJS Agresif. Sangat menarik untuk entri cepat dengan target profit +{bpjs_min_chg}% - +5%."
    else:
        kesimpulan = "⏳ Saham belum memenuhi seluruh kriteria BPJS Agresif. Tunggu konfirmasi volume dan kenaikan harga di atas MA 5."
        
    return f"{ma_txt} {candle_txt} {vol_txt} {val_txt} <br> {kesimpulan}"


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
# FETCH DATA
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=86400, show_spinner=False)
def fetch_watchlist_goapi(mode):
    try:
        if mode == "gainer":
            r = requests.get(f"{BASE_URL}/stock/idx/top_gainer",   headers=GOAPI_HEADERS, timeout=10)
        elif mode == "loser":
            r = requests.get(f"{BASE_URL}/stock/idx/top_loser",    headers=GOAPI_HEADERS, timeout=10)
        else:
            r = requests.get(f"{BASE_URL}/stock/idx/trending",     headers=GOAPI_HEADERS,
                             params={"type":"volume"}, timeout=10)
        return [d["symbol"] for d in r.json().get("data",{}).get("results",[])]
    except:
        return []

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
        
        # Tambahan untuk BPJS Agresif
        df["MA5"]       = c.rolling(5).mean()
        
        res = df.iloc[-1].to_dict()
        if len(df) >= 2:
            res["prev_close"] = float(df["close"].iloc[-2])
            res["prev_volume"] = float(df["volume"].iloc[-2])
        else:
            res["prev_close"] = float(df["close"].iloc[-1])
            res["prev_volume"] = float(df["volume"].iloc[-1])
            
        res["open_today"] = float(df["open"].iloc[-1])
        res["value_today"] = float(df["volume"].iloc[-1]) * float(df["close"].iloc[-1])
        
        return res
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

def tentukan_sinyal_bpjs_agresif(ind, harga, min_chg, min_val_miliar):
    if ind is None:
        return "TUNGGU", ["Data kurang"], 0
    
    prev_close = ind.get("prev_close", harga)
    open_today = ind.get("open_today", harga)
    prev_volume = ind.get("prev_volume", 0)
    vol_today = ind.get("volume", 0)
    ma5 = ind.get("MA5", harga)
    value_today = ind.get("value_today", 0)
    
    # 1. Kenaikan harga >= min_chg% dari close kemarin
    chg_prev = ((harga - prev_close) / prev_close * 100) if prev_close > 0 else 0
    cond_chg = chg_prev >= min_chg
    
    # 2. Harga >= MA 5
    cond_ma5 = harga >= ma5
    
    # 3. Harga >= Open Price (Candle Hijau)
    cond_green = harga >= open_today
    
    # 4. Volume >= 0.2 * Volume Kemarin
    cond_vol = vol_today >= 0.2 * prev_volume if prev_volume > 0 else False
    
    # 5. Nilai Transaksi >= min_val_miliar Rupiah
    cond_val = value_today >= min_val_miliar * 1_000_000_000
    
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
        
    # Sinyal BELI jika memenuhi seluruh kriteria (5/5)
    if bs == 5:
        return "BELI", alasan, bs
    return "TUNGGU", alasan, bs

def hitung_confidence_bpjs(bs):
    score = int(bs * 20)
    score = max(10, min(100, score))
    if   score >= 100: label, color = "🔥 Sangat Kuat",   "#22c55e"
    elif score >= 80:  label, color = "💪 Kuat",           "#84cc16"
    elif score >= 60:  label, color = "✅ Cukup",          "#f59e0b"
    elif score >= 40:  label, color = "⚠️ Lemah",         "#f97316"
    else:              label, color = "❌ Sangat Lemah",   "#ef4444"
    return score, label, color


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
st.sidebar.markdown("## ⚙️ Pengaturan")

taktik_trading = st.sidebar.selectbox("🎯 Taktik Trading:", ["Swing & Scalping Klasik", "⚡ BPJS Agresif (Custom +2%)"])

bpjs_min_chg = 2.0
bpjs_min_val = 2.0
if taktik_trading == "⚡ BPJS Agresif (Custom +2%)":
    bpjs_min_chg = st.sidebar.slider("⚡ Minimal Kenaikan BPJS (%)", 1.0, 5.0, 2.0, 0.5)
    bpjs_min_val = st.sidebar.slider("⚡ Minimal Transaksi (Miliar Rp)", 1, 10, 2, 1)


mode_saham = st.sidebar.radio("📊 Sumber Saham:", [
    "🔥 Top Gainer (GoAPI)",
    "📉 Top Loser / Rebound (GoAPI)",
    "🌊 Trending Volume (GoAPI)",
    "💎 LQ45 + Populer (Offline)",
    "✏️ Manual"
], index=0)

modal_per_saham = st.sidebar.number_input(
    "💰 Modal per Saham (Rp):",
    min_value=100_000, max_value=20_000_000,
    value=500_000, step=50_000, format="%d"
)
target_pct = st.sidebar.slider("🎯 Target Profit (%)", 2.0, 20.0, 5.0, 0.5)
sl_pct     = st.sidebar.slider("🛑 Stop Loss (%)",    1.0, 10.0, 3.0, 0.5)
max_saham  = st.sidebar.slider("📋 Jumlah Saham",     5, 50, 20)

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
**📖 Sinyal:**
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
    <p>BPJS · BSJP · GoAPI + yfinance + TradingView · Powered by Stockbit</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# AMBIL DAFTAR SAHAM
# ─────────────────────────────────────────────────────────────────────────────
with st.spinner("📡 Mengambil daftar saham..."):
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

# ─── TICKER TAPE ─────────────────────────────────────────────────────────────
components.html(tv_ticker_tape(symbols[:20]), height=72)

# Status Pasar
sesi_status, sesi_label = get_status_pasar()
now_str = datetime.now(WIB).strftime("%H:%M:%S WIB — %A, %d %B %Y")
css_map = {"buka":"pasar-buka","tutup":"pasar-tutup","preopen":"pasar-preopen"}
st.markdown(f'<div class="{css_map[sesi_status]}">{sesi_label} &nbsp;|&nbsp; 🕐 {now_str}</div>',
            unsafe_allow_html=True)

# ─── Download data yfinance ───────────────────────────────────────────────
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
    if taktik_trading == "⚡ BPJS Agresif (Custom +2%)":
        sinyal, alasan, bs_count = tentukan_sinyal_bpjs_agresif(ind, harga, bpjs_min_chg, bpjs_min_val)
        confidence, conf_label, conf_color = hitung_confidence_bpjs(bs_count)
    else:
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

# ─── Auto-save ke Signal History ─────────────────────────────────────────
new_signals = record_signals(results, modal_per_saham, target_pct, sl_pct)
if new_signals > 0:
    st.toast(f"✅ {new_signals} sinyal baru disimpan ke Signal History!", icon="📜")

# ─── Ringkasan Global ─────────────────────────────────────────────────────
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

    if sinyal=="BELI":   css,tag_css,tag_txt = "card-beli",  "tag-green",  "🟢 BELI — BPJS"
    elif sinyal=="BSJP": css,tag_css,tag_txt = "card-bsjp",  "tag-purple", "🟣 BELI SORE JUAL PAGI"
    elif sinyal=="JUAL": css,tag_css,tag_txt = "card-jual",  "tag-red",    "🔴 JUAL / CUT LOSS"
    else:                css,tag_css,tag_txt = "card-tunggu","tag-gray",   "⏳ TUNGGU"

    chg_col  = "#22c55e" if chg>=0 else "#ef4444"
    chg_sign = "+" if chg>=0 else ""
    
    if taktik_trading == "⚡ BPJS Agresif (Custom +2%)":
        prev_close = ind.get("prev_close", harga)
        open_today = ind.get("open_today", harga)
        prev_volume = ind.get("prev_volume", 0)
        vol_today = ind.get("volume", 0)
        ma5 = ind.get("MA5", harga)
        value_today = ind.get("value_today", 0)
        
        chg_prev = ((harga - prev_close) / prev_close * 100) if prev_close > 0 else 0
        cond_chg = chg_prev >= bpjs_min_chg
        cond_ma5 = harga >= ma5
        cond_green = harga >= open_today
        cond_vol = vol_today >= 0.2 * prev_volume if prev_volume > 0 else False
        cond_val = value_today >= bpjs_min_val * 1_000_000_000
        
        pill_chg = f"Naik {chg_prev:+.1f}% {'✅' if cond_chg else '⚠️'}"
        pill_ma5 = f"MA5 {'✅' if cond_ma5 else '⚠️'}"
        pill_green = f"Candle {'Hijau ✅' if cond_green else 'Merah ⚠️'}"
        pct_prev = (vol_today / prev_volume * 100) if prev_volume > 0 else 0
        pill_vol = f"Vol Pagi {pct_prev:.0f}% {'✅' if cond_vol else '⚠️'}"
        pill_val = f"Value {value_today/1e9:.1f}B {'✅' if cond_val else '⚠️'}"
        
        pills_html = f"<div><span class='ind-pill'>{pill_chg}</span><span class='ind-pill'>{pill_ma5}</span><span class='ind-pill'>{pill_green}</span><span class='ind-pill'>{pill_vol}</span><span class='ind-pill'>{pill_val}</span></div>"
        analisis = buat_analisis_singkat_bpjs(ind, harga, sinyal, chg, bpjs_min_chg, bpjs_min_val)
    else:
        rsi      = ind.get("RSI",0)
        ema9     = ind.get("EMA9",0)
        ema21    = ind.get("EMA21",0)
        ema50    = ind.get("EMA50",0)
        mh       = ind.get("MACD_hist",0)
        rsi_col  = "#ef4444" if rsi>70 else ("#22c55e" if rsi<40 else "#f59e0b")
        
        pills_html = f"<div><span class='ind-pill'>RSI <b style='color:{rsi_col}'>{rsi:.0f}</b></span><span class='ind-pill'>{'EMA9>21 ✅' if ema9>ema21 else 'EMA9<21 ⚠️'}</span><span class='ind-pill'>{'MACD+ ✅' if mh>0 else 'MACD- ⚠️'}</span><span class='ind-pill'>EMA50 <b style='color:{\"#22c55e\" if harga>ema50 else \"#ef4444\"}'>{ema50:.0f}</b></span></div>"
        analisis = buat_analisis_singkat(ind, harga, sinyal, chg)

    confidence = r.get("confidence", 50)
    conf_label = r.get("conf_label", "Cukup")
    conf_color = r.get("conf_color", "#cbd5e1")

    st.markdown(f"""
<div class="{css}">
    <div style="display:flex;justify-content:space-between;align-items:flex-start">
        <span class="card-sym">{sym}</span>
        <span class="{tag_css}">{tag_txt}</span>
    </div>
    <p class="card-price">Rp {harga:,.0f}</p>
    <p style="font-size:0.88rem;color:{chg_col};margin:0 0 6px 0;font-weight:700">
        {chg_sign}{chg:.2f}% &nbsp;<span style="color:#475569;font-weight:400">Vol {r['vol']:,.0f}</span>
    </p>
    <!-- Progress Bar Confidence -->
    <div style="margin: 8px 0 10px 0;">
        <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:#cbd5e1; margin-bottom:3px;">
            <span>📊 Confidence Sinyal</span>
            <span style="font-weight:700; color:{conf_color}">{confidence}% · {conf_label}</span>
        </div>
        <div style="background: rgba(255,255,255,0.1); border-radius: 4px; height: 6px; width: 100%; overflow: hidden;">
            <div style="background: {conf_color}; width: {confidence}%; height: 100%; border-radius: 4px;"></div>
        </div>
    </div>
    {pills_html}
    <p style="font-size:0.78rem;color:#cbd5e1;margin:12px 0 0 0;line-height:1.5;">{analisis}</p>
</div>
""", unsafe_allow_html=True)


    # Kalkulator
    if k and lot > 0:
        pc = "#22c55e" if k["profit"]>=0 else "#ef4444"
        st.markdown(f"""
        <div class="kalkulator">
            🧮 <b>{lot} lot</b> ({lot*100:,} lbr) @ Rp {harga:,.0f}
            &nbsp;|&nbsp; Modal: <b>Rp {k['modal']:,.0f}</b><br>
            Target jual: <b>Rp {snap_fraksi(k['ht']):,}</b> (+{target_pct}%)
            &nbsp;·&nbsp; Stop loss: <b>Rp {snap_fraksi(k['hsl']):,}</b> (-{sl_pct}%)<br>
            <span style="color:{pc};font-weight:700">✅ Profit: Rp {k['profit']:,.0f}</span>
            &nbsp;|&nbsp;
            <span style="color:#ef4444;font-weight:700">❌ Rugi SL: Rp {k['rugi']:,.0f}</span><br>
            <small style="color:#475569">*Fee Stockbit beli 0.10% + jual 0.20% sudah dihitung</small>
        </div>
        """, unsafe_allow_html=True)
    elif lot == 0:
        st.markdown(f"""
        <div class="kalkulator" style="border-color:#854d0e">
            ⚠️ <b>Modal Rp {modal_per_saham:,.0f} tidak cukup untuk 1 lot</b><br>
            Minimal: <b>Rp {harga*100:,.0f}</b> (1 lot = 100 lbr × Rp {harga:,.0f})
        </div>
        """, unsafe_allow_html=True)

    # TradingView widgets dalam expander
    with st.expander(f"📊 Analisis TradingView — {sym} (klik untuk buka)"):
        tab1, tab2 = st.tabs(["🎯 Technical Analysis", "📈 Mini Chart"])
        with tab1:
            st.caption(f"Analisis 20+ indikator TradingView untuk IDX:{sym} · Timeframe: {tv_interval}")
            components.html(tv_technical_analysis(sym, tv_interval, 400), height=420)
        with tab2:
            st.caption(f"Chart 1 bulan terakhir IDX:{sym} — klik ikon untuk full chart di TradingView")
            components.html(tv_mini_chart(sym, 240), height=260)
            st.markdown(f"🔗 [Buka Full Chart TradingView → IDX:{sym}](https://www.tradingview.com/chart/?symbol=IDX:{sym})", unsafe_allow_html=False)

# ─────────────────────────────────────────────────────────────────────────────
# TABS UTAMA
# ─────────────────────────────────────────────────────────────────────────────
tab_dash, tab_hist = st.tabs(["📊 Dashboard Real-Time", "📜 Signal History & Evaluasi"])

with tab_dash:
    # RENDER SAHAM: BELI & BSJP (Prioritas Utama)
    beli_results  = [r for r in results if r["sinyal"] in ("BELI","BSJP")]
    other_results = [r for r in results if r["sinyal"] not in ("BELI","BSJP")]

    if beli_results:
        st.markdown('<div class="section-header">🟢 Rekomendasi Entry — Beli Sekarang</div>', unsafe_allow_html=True)
        cols = st.columns(2)
        for i, r in enumerate(beli_results):
            with cols[i % 2]:
                render_kartu(r)
        st.markdown("---")
    else:
        st.info("⏳ Belum ada sinyal BELI saat ini. Semua saham masih dalam kondisi TUNGGU / JUAL. Refresh saat pasar buka untuk sinyal terbaru.")
        st.markdown("---")

    # RENDER SAHAM: JUAL & TUNGGU (dalam expander agar tidak ramai)
    if other_results:
        with st.expander(f"📋 Saham Lainnya — {len(other_results)} saham (TUNGGU / JUAL)"):
            cols2 = st.columns(2)
            for i, r in enumerate(other_results):
                with cols2[i % 2]:
                    render_kartu(r)

    # TABEL RINGKASAN
    st.markdown("---")
    st.markdown("### 📋 Tabel Ringkasan")

    rows = []
    for r in results:
        k = r["k"]
        rows.append({
            "Kode":        r["symbol"],
            "Harga":       f"Rp {r['harga']:,.0f}",
            "Chg%":        f"{'+' if r['chg']>=0 else ''}{r['chg']:.2f}%",
            "RSI":         f"{r['ind'].get('RSI',0):.0f}",
            "EMA":         "↑" if r["ind"].get("EMA9",0)>r["ind"].get("EMA21",0) else "↓",
            "MACD":        "+" if r["ind"].get("MACD_hist",0)>0 else "-",
            "Sinyal":      r["sinyal"],
            "Confidence":  f"{r['confidence']}% {r['conf_label']}",
            "Lot":         r["lot"] if r["lot"]>0 else "kurang modal",
            "Target":      f"Rp {snap_fraksi(k['ht']):,}" if k else "-",
            "Stop Loss":   f"Rp {snap_fraksi(k['hsl']):,}" if k else "-",
            "Est. Profit": f"Rp {k['profit']:,.0f}" if k else "-",
        })

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.markdown(
        f"<small style='color:#334155'>⏱️ {now_str} · "
        f"yfinance delay ~15 mnt · Cache 30 mnt · "
        f"Berhasil analisis {len(results)}/{len(symbols)} saham</small>",
        unsafe_allow_html=True
    )

with tab_hist:
    st.markdown("### 📜 Riwayat Sinyal & Evaluasi Akurasi")
    
    # Tombol evaluasi & Status
    col_eval_btn, col_eval_status = st.columns([1, 3])
    with col_eval_btn:
        if st.button("🔄 Evaluasi Akurasi Sinyal", use_container_width=True):
            with st.spinner("Mengevaluasi..."):
                hist, changed = evaluate_history()
                if changed > 0:
                    st.success(f"Berhasil mengevaluasi {changed} sinyal baru!")
                else:
                    st.info("Semua sinyal sudah dievaluasi atau belum ada data hari berikutnya.")
                st.rerun()

    history = load_history()
    
    if not history:
        st.info("Belum ada riwayat sinyal yang disimpan. Sinyal BELI/BSJP/JUAL akan disimpan otomatis saat Anda melakukan scan.")
    else:
        # Filter sinyal BELI/BSJP
        buy_signals = [h for h in history if h["sinyal"] in ("BELI", "BSJP")]
        eval_buys = [h for h in buy_signals if h.get("outcome") is not None]
        
        if eval_buys:
            wins = sum(1 for h in eval_buys if "✅" in h["outcome"] or "PROFIT" in h["outcome"])
            win_rate = (wins / len(eval_buys)) * 100
            
            # Hitung avg return
            returns = [h["return_pct"] for h in eval_buys if h["return_pct"] is not None]
            avg_return = sum(returns) / len(returns) if returns else 0.0
            
            # Total profit
            total_profit = sum(h["est_profit_rp"] for h in eval_buys if h.get("est_profit_rp") is not None)
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("📊 Total Sinyal Scan", len(history))
            c2.metric("🎯 Win Rate (BELI/BSJP)", f"{win_rate:.1f}%", f"{wins}/{len(eval_buys)} Saham")
            c3.metric("📈 Rata-rata Return", f"{avg_return:+.2f}%")
            
            prof_color = "normal" if total_profit >= 0 else "inverse"
            c4.metric("💰 Estimasi Profit Realisasi", 
                      f"Rp {total_profit:,.0f}" if total_profit >= 0 else f"-Rp {abs(total_profit):,.0f}",
                      delta_color=prof_color)
        else:
            st.warning("Belum ada sinyal BELI/BSJP yang dapat dievaluasi (memerlukan data penutupan minimal 1 hari bursa setelah scan).")
            
        # Tampilkan tabel riwayat
        df_hist = pd.DataFrame(history)
        
        # Sort history: scan_time descending (terbaru di atas)
        df_display = df_hist.sort_values(by="scan_time", ascending=False)
        
        # Select columns to display
        show_cols = ["scan_time", "symbol", "sinyal", "harga_signal", "confidence", "target_harga", "sl_harga", "harga_close", "return_pct", "outcome"]
        show_cols = [c for c in show_cols if c in df_display.columns]
        df_display = df_display[show_cols]
        
        # Rename columns for clarity
        df_display.columns = [
            "Waktu Scan", "Kode", "Sinyal", "Harga Masuk", "Confidence", "Target TP", "Stop Loss", "Harga Close", "Return %", "Hasil Evaluasi"
        ]
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
