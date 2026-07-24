"""
Dashboard Rekomendasi Trading Saham IDX
=========================================
Jalankan dengan: streamlit run app.py

Dependency:
    pip install streamlit yfinance pandas numpy plotly
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ==========================================================
# KONFIGURASI
# ==========================================================
st.set_page_config(page_title="Dashboard Rekomendasi Saham IDX", layout="wide")

WATCHLIST = ["ADRO", "PTBA", "BMRI", "CDIA", "CUAN", "BRPT", "CPRO", "ANTM", "BBRM"]

# Saham likuid/blue chip IDX (LQ45 & sejenis) biar pengguna lain bisa pilih saham sendiri,
# bukan cuma watchlist personal di atas.
ALL_TICKERS = sorted(set(WATCHLIST + [
    "BBCA", "BBRI", "BBNI", "TLKM", "ASII", "UNVR", "ICBP", "INDF", "KLBF", "UNTR",
    "PGAS", "MDKA", "INCO", "TINS", "SMGR", "INTP", "SIDO", "CPIN", "JPFA", "AALI",
    "LSIP", "GGRM", "HMSP", "WIKA", "WSKT", "PTPP", "ADHI", "JSMR", "EXCL", "ISAT",
    "TOWR", "TBIG", "MNCN", "SCMA", "MAPI", "ACES", "ERAA", "MYOR", "ULTJ", "TSPC",
    "ROTI", "BSDE", "CTRA", "PWON", "SMRA", "AMRT", "BUKA", "GOTO", "EMTK", "MEDC",
    "ELSA", "ITMG", "HRUM", "BRIS", "BBTN", "ARTO", "TPIA", "AKRA", "INKP", "TKIM",
]))

# ==========================================================
# DESIGN TOKENS
# ==========================================================
COLOR_BG = "#FFFFFF"
COLOR_SURFACE = "#F7F5FC"
COLOR_BORDER = "#EBE7F7"
COLOR_TEXT = "#26203A"
COLOR_MUTED = "#8B84A0"
COLOR_ACCENT = "#7C5CFC"
COLOR_ACCENT_2 = "#D946EF"
COLOR_ACCENT_SOFT = "#F1EDFB"
COLOR_BUY = "#16A34A"
COLOR_BUY_SOFT = "#DCFCE7"
COLOR_SELL = "#DC2626"
COLOR_SELL_SOFT = "#FEE2E2"
COLOR_HOLD = "#B45309"
COLOR_HOLD_SOFT = "#FEF3C7"

SIGNAL_COLORS = {
    "BUY": (COLOR_BUY, COLOR_BUY_SOFT),
    "SELL": (COLOR_SELL, COLOR_SELL_SOFT),
    "HOLD": (COLOR_HOLD, COLOR_HOLD_SOFT),
    "DATA KURANG": (COLOR_MUTED, COLOR_SURFACE),
}

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, sans-serif;
    }}
    h1, h2, h3 {{
        font-family: 'Sora', 'Inter', sans-serif !important;
        letter-spacing: -0.01em;
    }}
    .stApp {{
        background:
            radial-gradient(circle at 12% 8%, rgba(124, 92, 252, 0.05), transparent 42%),
            radial-gradient(circle at 88% 15%, rgba(217, 70, 239, 0.045), transparent 40%),
            radial-gradient(circle at 20% 92%, rgba(217, 70, 239, 0.035), transparent 38%),
            radial-gradient(circle at 85% 85%, rgba(124, 92, 252, 0.04), transparent 42%),
            {COLOR_BG};
    }}

    /* sidebar */
    section[data-testid="stSidebar"] {{
        background-color: #FFFFFF;
        border-right: 1px solid {COLOR_BORDER};
    }}
    section[data-testid="stSidebar"] div[role="radiogroup"] label {{
        border-radius: 8px;
        padding: 0.4rem 0.6rem;
        margin-bottom: 0.15rem;
    }}
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {{
        background: linear-gradient(90deg, {COLOR_ACCENT_SOFT}, #FCEEFB);
    }}

    /* metric cards */
    div[data-testid="stMetric"] {{
        background-color: #FFFFFF;
        border: 1px solid {COLOR_BORDER};
        border-radius: 14px;
        padding: 1.1rem 1.2rem;
        box-shadow: 0 4px 16px rgba(124, 92, 252, 0.08);
    }}
    div[data-testid="stMetricValue"] {{
        font-family: 'IBM Plex Mono', monospace;
        font-variant-numeric: tabular-nums;
    }}

    /* tabular numbers wherever data shows */
    div[data-testid="stDataFrame"] * {{
        font-variant-numeric: tabular-nums;
    }}
    div[data-testid="stDataFrame"] {{
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 16px rgba(124, 92, 252, 0.06);
    }}

    /* tabs */
    button[data-baseweb="tab"] {{
        font-family: 'Sora', 'Inter', sans-serif;
        color: {COLOR_MUTED};
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: {COLOR_ACCENT};
        border-bottom-color: {COLOR_ACCENT} !important;
    }}

    /* primary buttons -> purple-to-pink gradient */
    button[kind="primary"], .stButton > button[kind="primary"] {{
        background: linear-gradient(90deg, {COLOR_ACCENT}, {COLOR_ACCENT_2}) !important;
        border: none !important;
        color: #FFFFFF !important;
    }}

    /* signal pill badge */
    .signal-pill {{
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.3rem 0.75rem;
        border-radius: 999px;
        font-family: 'Sora', 'Inter', sans-serif;
        font-weight: 600;
        font-size: 0.95rem;
    }}

    hr {{
        border-color: {COLOR_BORDER} !important;
    }}

    /* komponen bersama (dipakai di Selamat Datang & Panduan) */
    .hero-badge {{
        display: inline-block;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: .04em;
        color: {COLOR_ACCENT};
        background: {COLOR_ACCENT_SOFT};
        border: 1px solid {COLOR_BORDER};
        padding: 0.3rem 0.9rem;
        border-radius: 999px;
    }}
    .sig-pill {{
        display: inline-block;
        font-weight: 700;
        font-size: 0.82rem;
        padding: 0.12rem 0.55rem;
        border-radius: 999px;
        margin: 0 0.1rem;
    }}
    .disclaimer-box {{
        background: {COLOR_HOLD_SOFT};
        border: 1px solid #FDE68A;
        border-radius: 14px;
        padding: 0.9rem 1.2rem;
        color: {COLOR_HOLD};
        font-size: 0.9rem;
        line-height: 1.55;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


def style_chart(fig):
    """Terapkan tema terang konsisten ke semua chart Plotly."""
    fig.update_layout(
        paper_bgcolor=COLOR_SURFACE,
        plot_bgcolor=COLOR_SURFACE,
        font=dict(family="Inter, sans-serif", color=COLOR_TEXT, size=12),
        title_font=dict(family="Sora, Inter, sans-serif", size=14),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(gridcolor=COLOR_BORDER, zerolinecolor=COLOR_BORDER),
        yaxis=dict(gridcolor=COLOR_BORDER, zerolinecolor=COLOR_BORDER),
        dragmode="pan",
    )
    return fig


@st.dialog("Chart", width="large")
def _chart_dialog():
    fig = st.session_state.get("_dialog_fig")
    title = st.session_state.get("_dialog_title", "")
    if fig is None:
        return
    if title:
        st.subheader(title)
    big_fig = go.Figure(fig)
    big_fig.update_layout(height=650)
    st.plotly_chart(big_fig, use_container_width=True, config={"scrollZoom": True})


def chart_with_zoom(fig, title="", key="", height=None):
    """Render chart + tombol perbesar (buka pop up dialog dengan versi lebih besar)."""
    st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True}, key=f"chart_{key}")
    if st.button("🔍 Perbesar", key=f"expand_{key}", use_container_width=True):
        st.session_state["_dialog_fig"] = fig
        st.session_state["_dialog_title"] = title
        _chart_dialog()


def _hex_to_rgba(hex_color, alpha=0.12):
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


def mini_sparkline(values, color):
    """Sparkline kecil tanpa axis, buat kartu KPI (gaya area-fill tipis)."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=values, mode="lines", line=dict(width=1.6, color=color),
        fill="tozeroy", fillcolor=_hex_to_rgba(color),
    ))
    fig.update_layout(
        height=44, margin=dict(l=0, r=0, t=2, b=2),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        showlegend=False,
    )
    return fig


def kpi_card(col, label, value, badge_text, badge_color, spark_values, spark_color):
    with col:
        with st.container(border=True):
            st.markdown(
                f"<div style='display:flex;justify-content:space-between;align-items:center;'>"
                f"<span style='font-family:Sora,Inter,sans-serif;font-weight:600;font-size:0.95rem;'>{label}</span>"
                f"<span style='background-color:{badge_color}22;color:{badge_color};"
                f"font-size:0.72rem;font-weight:600;padding:0.15rem 0.5rem;border-radius:999px;'>{badge_text}</span>"
                f"</div>"
                f"<div style='font-family:\"IBM Plex Mono\",monospace;font-size:1.6rem;font-weight:600;"
                f"margin-top:0.35rem;'>{value}</div>",
                unsafe_allow_html=True,
            )
            if spark_values:
                st.plotly_chart(
                    mini_sparkline(spark_values, spark_color),
                    use_container_width=True,
                    config={"displayModeBar": False},
                )


def signal_pill_html(signal, score=None):
    fg, bg = SIGNAL_COLORS.get(signal, (COLOR_MUTED, COLOR_SURFACE))
    icon = {"BUY": "▲", "SELL": "▼", "HOLD": "■", "DATA KURANG": "?"}.get(signal, "")
    strength = ""
    if score is not None and signal != "DATA KURANG":
        strength = f" <span style='opacity:.7'>{strength_dots(score)}</span>"
    return (
        f"<span class='signal-pill' style='color:{fg};background-color:{bg};'>"
        f"{icon} {signal}{strength}</span>"
    )

# ==========================================================
# FUNGSI AMBIL DATA
# ==========================================================
@st.cache_data(ttl=3600)  # cache 1 jam biar ga spam request ke yfinance
def get_data(ticker, period="6mo", interval="1d"):
    kode = ticker + ".JK"
    df = yf.download(kode, period=period, interval=interval, progress=False)
    if df.empty:
        return None
    # Kalau kolom multi-index (kadang terjadi di yfinance versi baru)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.dropna()
    return df


# ==========================================================
# FUNGSI HITUNG INDIKATOR
# ==========================================================
def calc_indicators(df):
    df = df.copy()

    # Moving Averages
    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA50"] = df["Close"].rolling(50).mean()

    # RSI (14)
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    # MACD
    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = ema12 - ema26
    df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_Hist"] = df["MACD"] - df["Signal"]

    return df


# ==========================================================
# LOGIC REKOMENDASI SEDERHANA
# ==========================================================
def generate_signal(df):
    """
    Aturan sederhana (rule-based), bukan ML.
    - BUY  : MA20 > MA50 (uptrend) & RSI < 60 (belum overbought) & MACD > Signal
    - SELL : MA20 < MA50 (downtrend) & RSI > 40 & MACD < Signal
    - HOLD : selain itu
    """
    if len(df) < 50 or df[["MA20", "MA50", "RSI", "MACD", "Signal"]].iloc[-1].isna().any():
        return "DATA KURANG", "gray", []

    last = df.iloc[-1]
    reasons = []
    score = 0

    # Trend
    if last["MA20"] > last["MA50"]:
        score += 1
        reasons.append("MA20 di atas MA50 (uptrend)")
    else:
        score -= 1
        reasons.append("MA20 di bawah MA50 (downtrend)")

    # RSI
    if last["RSI"] < 30:
        score += 1
        reasons.append(f"RSI {last['RSI']:.1f} (oversold, potensi rebound)")
    elif last["RSI"] > 70:
        score -= 1
        reasons.append(f"RSI {last['RSI']:.1f} (overbought, waspada koreksi)")
    else:
        reasons.append(f"RSI {last['RSI']:.1f} (netral)")

    # MACD
    if last["MACD"] > last["Signal"]:
        score += 1
        reasons.append("MACD di atas signal line (momentum positif)")
    else:
        score -= 1
        reasons.append("MACD di bawah signal line (momentum negatif)")

    if score >= 2:
        return "BUY", "green", reasons, score
    elif score <= -2:
        return "SELL", "red", reasons, score
    else:
        return "HOLD", "orange", reasons, score


SIGNAL_ICON = {"BUY": "▲", "SELL": "▼", "HOLD": "■", "DATA KURANG": "?"}
SIGNAL_ORDER = {"BUY": 0, "HOLD": 1, "SELL": 2, "DATA KURANG": 3}


def strength_dots(score):
    """Skor -3..+3 -> 0..5 dot, dot terisi sebanding |score|."""
    filled = round(abs(score) / 3 * 5)
    return "●" * filled + "○" * (5 - filled)


# ==========================================================
# MODUL BACKTESTING
# ==========================================================
def calc_signal_series(df):
    """Hitung skor & sinyal untuk SETIAP baris histori (bukan cuma baris terakhir),
    pakai aturan yang sama persis dengan generate_signal()."""
    trend = np.where(df["MA20"] > df["MA50"], 1, -1)
    rsi_score = np.select([df["RSI"] < 30, df["RSI"] > 70], [1, -1], default=0)
    macd = np.where(df["MACD"] > df["Signal"], 1, -1)
    score = trend + rsi_score + macd

    signal = np.select([score >= 2, score <= -2], ["BUY", "SELL"], default="HOLD")

    valid = df[["MA20", "MA50", "RSI", "MACD", "Signal"]].notna().all(axis=1)
    score = pd.Series(score, index=df.index).where(valid)
    signal = pd.Series(signal, index=df.index).where(valid)
    return score, signal


def backtest_signals(df, hold_days=10):
    """
    Backtest naif: untuk tiap hari histori bersinyal BUY/SELL, cek return
    N hari ke depan. BUY dianggap 'menang' kalau harga naik; SELL dianggap
    'menang' kalau harga turun (berhasil menghindari kerugian).

    Keterbatasan (bukan validasi ilmiah):
    - Tanpa biaya transaksi/slippage
    - In-sample saja (data yang sama dipakai untuk sinyal & evaluasi)
    - Sinyal yang overlap (holding period saling tumpang tindih) dihitung independen
    """
    score, signal = calc_signal_series(df)
    forward_return = df["Close"].shift(-hold_days) / df["Close"] - 1

    results = {}
    for sig, is_win in [("BUY", lambda r: r > 0), ("SELL", lambda r: r < 0)]:
        mask = (signal == sig) & forward_return.notna()
        n = int(mask.sum())
        if n == 0:
            results[sig] = {"jumlah": 0, "win_rate": None, "avg_return": None}
            continue
        rets = forward_return[mask]
        results[sig] = {
            "jumlah": n,
            "win_rate": float(is_win(rets).mean() * 100),
            "avg_return": float(rets.mean() * 100),
        }
    return results


# ==========================================================
# UI - WELCOME (layar pertama, tanpa sidebar)
# ==========================================================
if "started" not in st.session_state:
    st.session_state.started = False

if not st.session_state.started:
    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        .stApp {{
            background:
                radial-gradient(circle at 12% 8%, rgba(124, 92, 252, 0.18), transparent 42%),
                radial-gradient(circle at 88% 15%, rgba(217, 70, 239, 0.16), transparent 40%),
                radial-gradient(circle at 20% 92%, rgba(217, 70, 239, 0.12), transparent 38%),
                radial-gradient(circle at 85% 85%, rgba(124, 92, 252, 0.14), transparent 42%),
                {COLOR_BG} !important;
        }}
        .hero-wrap {{
            padding: 3rem 1rem 1rem 1rem;
            text-align: center;
        }}
        .hero-badge {{
            display: inline-block;
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: .04em;
            color: {COLOR_ACCENT};
            background: {COLOR_ACCENT_SOFT};
            border: 1px solid {COLOR_BORDER};
            padding: 0.3rem 0.9rem;
            border-radius: 999px;
            margin-bottom: 1.2rem;
        }}
        .hero-title {{
            font-family: "Sora", "Inter", sans-serif;
            font-size: 2.6rem;
            font-weight: 800;
            line-height: 1.15;
            margin: 0 0 0.9rem 0;
            background: linear-gradient(90deg, {COLOR_ACCENT}, {COLOR_ACCENT_2});
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }}
        .hero-sub {{
            max-width: 700px;
            margin: 0 auto;
            color: {COLOR_MUTED};
            font-size: 1.08rem;
            line-height: 1.65;
        }}
        .hero-sub b {{ color: {COLOR_TEXT}; }}
        .story-row {{
            display: flex;
            justify-content: center;
            align-items: stretch;
            gap: 1.1rem;
            max-width: 920px;
            margin: 1.8rem auto 0 auto;
            flex-wrap: wrap;
        }}
        .story-card {{
            flex: 1;
            min-width: 280px;
            background: rgba(255, 255, 255, 0.75);
            backdrop-filter: blur(6px);
            border: 1px solid rgba(124, 92, 252, 0.16);
            border-radius: 18px;
            padding: 1.4rem 1.5rem;
            text-align: left;
        }}
        .story-kicker {{
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            color: {COLOR_MUTED};
            text-transform: uppercase;
            margin-bottom: 0.5rem;
        }}
        .story-text {{
            font-size: 0.97rem;
            color: {COLOR_TEXT};
            line-height: 1.55;
        }}
        .story-arrow {{
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            color: {COLOR_ACCENT};
            padding: 0 0.2rem;
        }}
        .sig-pill {{
            display: inline-block;
            font-weight: 700;
            font-size: 0.82rem;
            padding: 0.12rem 0.55rem;
            border-radius: 999px;
            margin: 0 0.1rem;
        }}
        .stat-strip {{
            display: flex;
            justify-content: center;
            gap: 2.5rem;
            flex-wrap: wrap;
            margin: 2.2rem 0 2.5rem 0;
            padding: 1.1rem 0;
            border-top: 1px solid rgba(124, 92, 252, 0.15);
            border-bottom: 1px solid rgba(124, 92, 252, 0.15);
        }}
        .stat-item {{
            text-align: center;
            min-width: 110px;
        }}
        .stat-number {{
            font-family: "Sora", "Inter", sans-serif;
            font-size: 1.6rem;
            font-weight: 800;
            background: linear-gradient(90deg, {COLOR_ACCENT}, {COLOR_ACCENT_2});
            -webkit-background-clip: text;
            background-clip: text;
            color: {COLOR_ACCENT};
        }}
        .stat-label {{
            font-size: 0.78rem;
            color: {COLOR_MUTED};
            margin-top: 0.15rem;
        }}
        .feature-card {{
            background: rgba(255, 255, 255, 0.72);
            backdrop-filter: blur(6px);
            border: 1px solid rgba(124, 92, 252, 0.18);
            border-radius: 16px;
            padding: 1.3rem 1.2rem;
            height: 100%;
            box-shadow: 0 4px 16px rgba(124, 92, 252, 0.06);
            transition: transform .15s ease, box-shadow .15s ease;
        }}
        .feature-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 10px 24px rgba(124, 92, 252, 0.16);
        }}
        .feature-icon {{
            font-size: 1.6rem;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 42px; height: 42px;
            border-radius: 12px;
            background: linear-gradient(135deg, {COLOR_ACCENT_SOFT}, #FCEEFB);
            margin-bottom: 0.7rem;
        }}
        .feature-title {{
            font-weight: 700;
            font-size: 1rem;
            color: {COLOR_TEXT};
            margin-bottom: 0.35rem;
        }}
        .feature-desc {{
            font-size: 0.88rem;
            color: {COLOR_TEXT};
            opacity: 0.85;
            line-height: 1.5;
        }}
        .disclaimer-box {{
            background: {COLOR_HOLD_SOFT};
            border: 1px solid #FDE68A;
            border-radius: 14px;
            padding: 0.9rem 1.2rem;
            color: {COLOR_HOLD};
            font-size: 0.9rem;
            line-height: 1.55;
        }}
        div[data-testid="stButton"] > button {{
            background: linear-gradient(90deg, {COLOR_ACCENT}, {COLOR_ACCENT_2});
            color: white;
            border: none;
            font-weight: 600;
            padding: 0.7rem 0;
            border-radius: 12px;
            box-shadow: 0 8px 20px rgba(124, 92, 252, 0.3);
        }}
        div[data-testid="stButton"] > button:hover {{
            filter: brightness(1.05);
            box-shadow: 0 10px 26px rgba(124, 92, 252, 0.4);
        }}
        </style>

        <div class="hero-wrap">
            <span class="hero-badge">📊 PERSONAL STOCK ASSISTANT &nbsp;·&nbsp; IDX</span>
            <div class="hero-title">Dashboard Rekomendasi<br>Trading Saham IDX</div>
            <div class="hero-sub">
                Dibuat untuk jawab pertanyaan yang paling sering bikin bingung tiap megang saham.
            </div>
            <div class="story-row">
                <div class="story-card">
                    <div class="story-kicker">😵‍💫 MASALAHNYA</div>
                    <div class="story-text">
                        Harga naik-turun tiap hari, dan tiap kali itu muncul pertanyaan yang sama:
                        <b>beli lagi, tahan, atau jual?</b> Nebak-nebak doang bikin keputusan jadi
                        gampang kebawa emosi.
                    </div>
                </div>
                <div class="story-arrow">→</div>
                <div class="story-card">
                    <div class="story-kicker">🎯 SOLUSINYA</div>
                    <div class="story-text">
                        Tiap saham di watchlist otomatis dikasih sinyal
                        <span class="sig-pill" style="color:{COLOR_BUY};background:{COLOR_BUY_SOFT}">▲ BUY</span>
                        <span class="sig-pill" style="color:{COLOR_HOLD};background:{COLOR_HOLD_SOFT}">■ HOLD</span>
                        <span class="sig-pill" style="color:{COLOR_SELL};background:{COLOR_SELL_SOFT}">▼ SELL</span>
                        berdasarkan MA20/MA50, RSI(14), dan MACD — lengkap dengan histori seberapa
                        akurat sinyal itu kalau dites ke data masa lalu.
                    </div>
                </div>
            </div>
            <div class="stat-strip">
                <div class="stat-item">
                    <div class="stat-number">{len(WATCHLIST)}</div>
                    <div class="stat-label">Saham diawasi</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">3</div>
                    <div class="stat-label">Indikator teknikal</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">BUY/SELL/HOLD</div>
                    <div class="stat-label">Sinyal otomatis</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">Harian</div>
                    <div class="stat-label">Update data</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    features = [
        ("📋", "Ringkasan Watchlist", "Semua saham + sinyal terkini dalam satu tabel, diurutkan BUY → HOLD → SELL."),
        ("📈", "Tren 30 Hari", "Grafik harga 30 hari terakhir tiap saham, bisa di-zoom & digeser."),
        ("🔁", "Backtest Sinyal", "Cek win rate sinyal BUY/SELL kalau dipakai di histori harga."),
        ("🔍", "Detail per Saham", "Candlestick, RSI, MACD, dan volume lengkap per saham."),
    ]
    cols = st.columns(4)
    for col, (icon, title, desc) in zip(cols, features):
        with col:
            st.markdown(
                f"""
                <div class="feature-card">
                    <div class="feature-icon">{icon}</div>
                    <div class="feature-title">{title}</div>
                    <div class="feature-desc">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")
    st.write("")
    d1, d2 = st.columns([5, 1.2])
    with d1:
        st.markdown(
            """
            <div class="disclaimer-box">
                ⚠️ Semua sinyal di sini berbasis aturan teknikal sederhana (rule-based),
                <b>bukan saran finansial</b>. Tetap cek data & pertimbangan sendiri sebelum
                ambil keputusan trading.
            </div>
            """,
            unsafe_allow_html=True,
        )
    with d2:
        if st.button("Lanjut ke Panduan →", use_container_width=True, type="primary"):
            st.session_state.started = True
            st.rerun()
    st.stop()

# ==========================================================
# UI - SIDEBAR
# ==========================================================
st.sidebar.title("📊 Dashboard Saham IDX")
PAGES = ["Panduan", "Ringkasan Watchlist", "Tren 30 Hari", "Backtest Sinyal", "Detail per Saham"]
page = st.sidebar.selectbox("Halaman", PAGES, index=0, label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Pengaturan")

INTERVAL_LABELS = {"1h": "1 Jam", "1d": "Harian", "1wk": "Mingguan"}
interval_label = st.sidebar.selectbox(
    "Interval candle",
    list(INTERVAL_LABELS.values()),
    index=1,
    help="1 Jam = tiap candle 1 jam bursa (data terbatas maks ~60 hari terakhir, "
    "sesuai batas Yahoo Finance). Harian = tiap candle 1 hari bursa. Mingguan = tiap "
    "candle 1 minggu (candle lebih sedikit, cocok untuk lihat tren jangka panjang).",
)
interval = {v: k for k, v in INTERVAL_LABELS.items()}[interval_label]

if interval == "1h":
    PERIOD_LABELS = {
        "5d": "5 Hari Terakhir",
        "1mo": "1 Bulan Terakhir",
        "2mo": "2 Bulan Terakhir",
    }
    default_period_idx = 2
    st.sidebar.caption(
        "ℹ️ Interval 1 Jam cuma nyediain data maks ~60 hari terakhir (limitasi Yahoo Finance)."
    )
else:
    PERIOD_LABELS = {
        "3mo": "3 Bulan Terakhir",
        "6mo": "6 Bulan Terakhir",
        "1y": "1 Tahun Terakhir",
        "2y": "2 Tahun Terakhir",
    }
    default_period_idx = 1

period_label = st.sidebar.selectbox(
    "Periode data",
    list(PERIOD_LABELS.values()),
    index=default_period_idx,
    help="Rentang histori harga yang diambil. Semakin panjang, MA20/MA50 makin akurat "
    "tapi chart makin padat dan load makin lama.",
)
period = {v: k for k, v in PERIOD_LABELS.items()}[period_label]

MIN_CANDLES_FOR_MA50 = 50
if interval == "1wk" and period in ("3mo", "6mo"):
    st.sidebar.warning(
        "⚠️ Interval Mingguan + periode pendek (3-6 bulan) menghasilkan candle < 50, "
        "MA50 & sinyal bisa muncul 'DATA KURANG'. Pilih periode 1y/2y untuk hasil optimal."
    )
elif interval == "1h" and period == "5d":
    st.sidebar.warning(
        "⚠️ Interval 1 Jam + periode 5 Hari menghasilkan candle < 50, "
        "MA50 & sinyal bisa muncul 'DATA KURANG'. Pilih periode 1-2 Bulan untuk hasil optimal."
    )
selected_tickers = st.sidebar.multiselect(
    "Watchlist", ALL_TICKERS, default=WATCHLIST,
    help="Default watchlist di atas cuma contoh punya saya. Tambah/ganti sesuai saham kamu sendiri!",
)

HOLD_LABELS = {5: "5 Candle", 10: "10 Candle", 20: "20 Candle"}
hold_label = st.sidebar.selectbox(
    "Backtest: periode holding",
    list(HOLD_LABELS.values()),
    index=1,
    help="Untuk backtest sinyal historis: setelah sinyal BUY/SELL muncul, "
    "harga dicek N candle ke depan untuk menentukan menang/kalah.",
)
hold_days = {v: k for k, v in HOLD_LABELS.items()}[hold_label]

st.sidebar.markdown("---")
st.sidebar.caption(
    "⚠️ Disclaimer: Ini rekomendasi berbasis aturan teknikal sederhana "
    "(rule-based), BUKAN saran finansial. Selalu lakukan riset sendiri "
    "sebelum mengambil keputusan trading."
)

# ==========================================================
# UI - MAIN
# ==========================================================
st.title("📊 Dashboard Rekomendasi Trading Saham IDX")
st.caption(
    f"Berdasarkan MA20/MA50, RSI(14), dan MACD — data {interval_label.lower()} dari Yahoo Finance"
)

if not selected_tickers:
    st.warning("Pilih minimal satu saham di sidebar.")
    st.stop()

# ---- Ringkasan semua saham (tabel) ----
data_cache = {}
last_dates = []
summary_rows = []

with st.spinner("Mengambil data..."):
    for t in selected_tickers:
        df = get_data(t, period, interval)
        if df is None or df.empty:
            summary_rows.append({
                "Saham": t, "Harga": None, "Perubahan (%)": None,
                "Tren 30h": None, "Volume": None,
                "Sinyal": "DATA KURANG", "Kekuatan": "", "RSI": None,
                "_sort_signal": SIGNAL_ORDER["DATA KURANG"], "_sort_score": 0,
            })
            continue

        df = calc_indicators(df)
        data_cache[t] = df
        last_dates.append(df.index[-1])

        signal, color, reasons, score = generate_signal(df)
        last_close = df["Close"].iloc[-1]
        prev_close = df["Close"].iloc[-2] if len(df) > 1 else last_close
        pct_change = (last_close - prev_close) / prev_close * 100
        rsi_val = df["RSI"].iloc[-1]
        volume = df["Volume"].iloc[-1]
        trend_30 = df["Close"].tail(30).tolist()

        summary_rows.append({
            "Saham": t,
            "Harga": last_close,
            "Perubahan (%)": pct_change,
            "Volume": volume,
            "Sinyal": f"{SIGNAL_ICON.get(signal, '')} {signal}",
            "Kekuatan": round(abs(score) / 3 * 100) if signal != "DATA KURANG" else None,
            "RSI": rsi_val if pd.notna(rsi_val) else None,
            "_trend_30": trend_30,
            "_signal_raw": signal,
            "_score_raw": score,
            "_sort_signal": SIGNAL_ORDER.get(signal, 3),
            "_sort_score": abs(score),
        })

summary_df = pd.DataFrame(summary_rows)
summary_df = summary_df.sort_values(
    ["_sort_signal", "_sort_score"], ascending=[True, False]
)
trend_lookup = summary_df.set_index("Saham")["_trend_30"].to_dict()
signal_lookup = summary_df.set_index("Saham")[["_signal_raw", "_score_raw"]].to_dict("index")
summary_df = summary_df.drop(columns=["_trend_30", "_signal_raw", "_score_raw", "_sort_signal", "_sort_score"])

def highlight_signal(val):
    sig = val.split(" ", 1)[-1] if isinstance(val, str) else val
    fg, bg = SIGNAL_COLORS.get(sig, (COLOR_MUTED, COLOR_SURFACE))
    return f"color:{fg}; background-color:{bg}; font-weight:600;"


# ==========================================================
# HALAMAN: RINGKASAN WATCHLIST
# ==========================================================
if page == "Ringkasan Watchlist":
    if last_dates:
        st.subheader("Ringkasan Watchlist")
        st.caption(f"🕒 Data per: {max(last_dates).strftime('%d %b %Y')} (close)")
    else:
        st.subheader("Ringkasan Watchlist")

    # ---- Kartu KPI ringkas ----
    if not summary_df.empty:
        sig_base = summary_df["Sinyal"].str.split(" ", n=1).str[-1]
        n_buy, n_sell, n_hold = (sig_base == "BUY").sum(), (sig_base == "SELL").sum(), (sig_base == "HOLD").sum()
        counts = {"BUY": n_buy, "SELL": n_sell, "HOLD": n_hold}
        dominant = max(counts, key=counts.get)
        dom_fg, _ = SIGNAL_COLORS[dominant]

        avg_pct = summary_df["Perubahan (%)"].mean(skipna=True)
        total_vol = summary_df["Volume"].sum(skipna=True)

        valid_trends = [v for v in trend_lookup.values() if v]
        agg_trend = []
        if valid_trends:
            common_len = min(len(v) for v in valid_trends)
            normed = [[p / v[-common_len] * 100 for p in v[-common_len:]] for v in valid_trends]
            agg_trend = [sum(pts) / len(pts) for pts in zip(*normed)]

        k1, k2, k3 = st.columns(3)
        kpi_card(
            k1, "Sinyal Dominan", f"{SIGNAL_ICON.get(dominant, '')} {dominant}",
            f"{counts[dominant]}/{len(summary_df)} saham", dom_fg,
            agg_trend, dom_fg,
        )
        kpi_card(
            k2, "Rata-rata Perubahan", f"{avg_pct:+.2f}%",
            "▲ naik" if avg_pct >= 0 else "▼ turun",
            COLOR_BUY if avg_pct >= 0 else COLOR_SELL,
            agg_trend, COLOR_ACCENT,
        )
        kpi_card(
            k3, "Total Volume", f"{total_vol / 1e6:,.0f}Jt",
            f"{len(summary_df)} saham", COLOR_ACCENT_2,
            agg_trend, COLOR_ACCENT_2,
        )
        st.write("")

    st.dataframe(
        summary_df.style.map(highlight_signal, subset=["Sinyal"]),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Harga": st.column_config.NumberColumn(format="Rp %,.0f"),
            "Perubahan (%)": st.column_config.NumberColumn(format="%+.2f%%"),
            "Volume": st.column_config.NumberColumn(format="compact"),
            "Kekuatan": st.column_config.ProgressColumn(
                format="%.0f%%", min_value=0, max_value=100
            ),
            "RSI": st.column_config.NumberColumn(format="%.1f"),
        },
    )
    st.caption(
        "Default urutan: BUY → HOLD → SELL, tiap grup diurutkan berdasarkan kekuatan sinyal. "
        "Klik header kolom untuk mengurutkan manual. Sinyal ditandai ikon ▲/▼/■ selain warna."
    )

# ==========================================================
# HALAMAN: TREN 30 HARI
# ==========================================================
elif page == "Tren 30 Hari":
    tickers_with_trend = [t for t in summary_df["Saham"] if trend_lookup.get(t)]
    if tickers_with_trend:
        st.subheader("Tren 30 Hari Terakhir")
        st.caption("Satu chart per saham, diurutkan dari performa terbaik. Scroll/drag di chart untuk zoom.")

        UP_COLOR = "#16a34a"
        DOWN_COLOR = "#dc2626"
        UP_FILL = "rgba(22, 163, 74, 0.10)"
        DOWN_FILL = "rgba(220, 38, 38, 0.10)"

        rows_sorted = sorted(
            tickers_with_trend,
            key=lambda t: (trend_lookup[t][-1] - trend_lookup[t][0]) / trend_lookup[t][0]
            if trend_lookup[t][0] else 0,
            reverse=True,
        )

        cols_per_row = 3
        for i in range(0, len(rows_sorted), cols_per_row):
            row_tickers = rows_sorted[i:i + cols_per_row]
            cols = st.columns(cols_per_row)
            for col, t in zip(cols, row_tickers):
                with col:
                    closes = trend_lookup[t]
                    dates = data_cache[t].index[-len(closes):]
                    delta_30 = (closes[-1] - closes[0]) / closes[0] * 100 if closes[0] else 0
                    is_up = delta_30 >= 0
                    color = UP_COLOR if is_up else DOWN_COLOR
                    fill_color = UP_FILL if is_up else DOWN_FILL
                    arrow = "▲" if is_up else "▼"

                    sig_info = signal_lookup.get(t, {})
                    pill_html = signal_pill_html(
                        sig_info.get("_signal_raw", "DATA KURANG"),
                        sig_info.get("_score_raw"),
                    )

                    with st.container(border=True):
                        c1, c2 = st.columns([1, 1])
                        c1.markdown(f"**{t}**")
                        c2.markdown(
                            f"<span style='color:{color}; font-weight:600; float:right'>"
                            f"{arrow} {delta_30:+.1f}%</span>",
                            unsafe_allow_html=True,
                        )
                        st.caption(f"Rp {closes[-1]:,.0f}")
                        st.markdown(pill_html, unsafe_allow_html=True)

                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=dates, y=closes,
                            mode="lines",
                            line=dict(color=color, width=2),
                            fill="tozeroy",
                            fillcolor=fill_color,
                            hovertemplate="%{x|%d %b}<br>Rp %{y:,.0f}<extra></extra>",
                        ))
                        fig.update_layout(
                            height=220,
                            margin=dict(l=0, r=0, t=4, b=0),
                            showlegend=False,
                            xaxis=dict(showgrid=False),
                            yaxis=dict(
                                showgrid=True,
                                gridcolor="rgba(128,128,128,0.15)",
                                tickformat=",.0f",
                            ),
                            plot_bgcolor="rgba(0,0,0,0)",
                            paper_bgcolor="rgba(0,0,0,0)",
                            dragmode="pan",
                        )
                        chart_with_zoom(fig, title=f"{t} — Tren 30 Hari", key=f"trend_{t}")
    else:
        st.info("Tidak ada data untuk ditampilkan.")

# ==========================================================
# HALAMAN: BACKTEST SINYAL
# ==========================================================
elif page == "Backtest Sinyal":
    if data_cache:
        st.subheader("Backtest Sinyal (Historis)")
        st.caption(
            f"Simulasi: setiap kali sinyal BUY/SELL muncul di histori, harga dicek "
            f"{hold_days} candle ke depan. BUY menang kalau harga naik, SELL menang "
            f"kalau harga turun."
        )

        backtest_rows = []
        for t in summary_df["Saham"]:
            if t not in data_cache:
                continue
            res = backtest_signals(data_cache[t], hold_days)
            row = {"Saham": t}
            for sig in ("BUY", "SELL"):
                r = res[sig]
                row[f"{sig} - Jumlah Sinyal"] = r["jumlah"]
                row[f"{sig} - Win Rate"] = r["win_rate"]
                row[f"{sig} - Avg Return"] = r["avg_return"]
            backtest_rows.append(row)

        backtest_df = pd.DataFrame(backtest_rows)
        st.dataframe(
            backtest_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "BUY - Win Rate": st.column_config.NumberColumn(format="%.0f%%"),
                "BUY - Avg Return": st.column_config.NumberColumn(format="%+.2f%%"),
                "SELL - Win Rate": st.column_config.NumberColumn(format="%.0f%%"),
                "SELL - Avg Return": st.column_config.NumberColumn(format="%+.2f%%"),
            },
        )
        st.caption(
            "⚠️ Backtest naif: tanpa biaya transaksi/slippage, dievaluasi in-sample "
            "(data historis yang sama dipakai untuk membentuk & menguji aturan), dan sinyal "
            "yang saling tumpang tindih dihitung independen. Jumlah sinyal kecil (periode data "
            "pendek) membuat win rate kurang bisa diandalkan. Ini bukan jaminan performa masa depan."
        )
    else:
        st.info("Tidak ada data untuk ditampilkan.")

# ==========================================================
# HALAMAN: DETAIL PER SAHAM
# ==========================================================
elif page == "Detail per Saham":
    st.subheader("Detail per Saham")
    tabs = st.tabs(selected_tickers)

    for tab, ticker in zip(tabs, selected_tickers):
        with tab:
            if ticker not in data_cache:
                st.error(f"Data untuk {ticker} tidak tersedia.")
                continue

            df = data_cache[ticker]
            signal, color, reasons, score = generate_signal(df)

            col1, col2 = st.columns([1, 2])

            with col1:
                delta_pct = None
                if len(df) > 1:
                    prev = df["Close"].iloc[-2]
                    delta_pct = (df["Close"].iloc[-1] - prev) / prev * 100

                st.metric(
                    label=f"Harga {ticker}",
                    value=f"Rp {df['Close'].iloc[-1]:,.0f}",
                    delta=f"{delta_pct:+.2f}%" if delta_pct is not None else None,
                )
                st.caption(f"Data per: {df.index[-1].strftime('%d %b %Y')} (close)")
                st.markdown(
                    f"<div style='margin:0.5rem 0 0.75rem'>{signal_pill_html(signal, score)}</div>",
                    unsafe_allow_html=True,
                )
                st.markdown("**Alasan:**")
                for r in reasons:
                    st.markdown(f"- {r}")

            with col2:
                # Chart harga + MA
                fig = go.Figure()
                fig.add_trace(go.Candlestick(
                    x=df.index, open=df["Open"], high=df["High"],
                    low=df["Low"], close=df["Close"], name="Harga",
                    increasing_line_color=COLOR_BUY, increasing_fillcolor=COLOR_BUY,
                    decreasing_line_color=COLOR_SELL, decreasing_fillcolor=COLOR_SELL,
                ))
                fig.add_trace(go.Scatter(x=df.index, y=df["MA20"], name="MA20", line=dict(width=1.5, color=COLOR_ACCENT)))
                fig.add_trace(go.Scatter(x=df.index, y=df["MA50"], name="MA50", line=dict(width=1.5, color="#F59E0B")))
                fig.update_layout(
                    height=400, margin=dict(l=10, r=10, t=30, b=10),
                    xaxis_rangeslider_visible=False,
                    title=f"{ticker}.JK - Harga & Moving Average",
                )
                style_chart(fig)
                chart_with_zoom(fig, title=f"{ticker}.JK - Harga & Moving Average", key=f"price_{ticker}")

            # RSI, MACD & Volume chart
            col3, col4, col5 = st.columns(3)
            with col3:
                fig_rsi = go.Figure()
                fig_rsi.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI", line=dict(color=COLOR_ACCENT)))
                fig_rsi.add_hline(y=70, line_dash="dash", line_color=COLOR_SELL)
                fig_rsi.add_hline(y=30, line_dash="dash", line_color=COLOR_BUY)
                fig_rsi.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10), title="RSI (14)")
                style_chart(fig_rsi)
                chart_with_zoom(fig_rsi, title=f"{ticker} — RSI (14)", key=f"rsi_{ticker}")

            with col4:
                fig_macd = go.Figure()
                fig_macd.add_trace(go.Scatter(x=df.index, y=df["MACD"], name="MACD", line=dict(color=COLOR_ACCENT)))
                fig_macd.add_trace(go.Scatter(x=df.index, y=df["Signal"], name="Signal", line=dict(color="#F59E0B")))
                hist_colors = [COLOR_BUY if v >= 0 else COLOR_SELL for v in df["MACD_Hist"]]
                fig_macd.add_trace(go.Bar(x=df.index, y=df["MACD_Hist"], name="Histogram", marker_color=hist_colors))
                fig_macd.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10), title="MACD")
                style_chart(fig_macd)
                chart_with_zoom(fig_macd, title=f"{ticker} — MACD", key=f"macd_{ticker}")

            with col5:
                vol_avg20 = df["Volume"].rolling(20).mean()
                last_vol = df["Volume"].iloc[-1]
                last_avg = vol_avg20.iloc[-1]
                vol_pct = (last_vol - last_avg) / last_avg * 100 if pd.notna(last_avg) and last_avg != 0 else None

                bar_colors = [
                    COLOR_BUY if c >= o else COLOR_SELL
                    for o, c in zip(df["Open"], df["Close"])
                ]
                fig_vol = go.Figure()
                fig_vol.add_trace(go.Bar(x=df.index, y=df["Volume"], name="Volume", marker_color=bar_colors))
                fig_vol.add_trace(go.Scatter(x=df.index, y=vol_avg20, name="Avg 20", line=dict(width=1.2, color=COLOR_MUTED)))
                title = "Volume"
                if vol_pct is not None:
                    arrow = "▲" if vol_pct >= 0 else "▼"
                    title = f"Volume ({arrow} {vol_pct:+.0f}% vs avg20)"
                fig_vol.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10), title=title, showlegend=False)
                style_chart(fig_vol)
                chart_with_zoom(fig_vol, title=f"{ticker} — {title}", key=f"vol_{ticker}")

# ==========================================================
# HALAMAN: PANDUAN
# ==========================================================
elif page == "Panduan":
    st.markdown(
        f"""
        <style>
        .pg-section-title {{
            font-family: "Sora", "Inter", sans-serif;
            font-size: 1.25rem;
            font-weight: 800;
            color: {COLOR_TEXT};
            margin: 2rem 0 0.9rem 0;
        }}
        .ind-card {{
            background: {COLOR_SURFACE};
            border: 1px solid {COLOR_BORDER};
            border-radius: 16px;
            padding: 1.2rem 1.3rem;
            height: 100%;
        }}
        .ind-icon {{
            font-size: 1.4rem;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 40px; height: 40px;
            border-radius: 12px;
            margin-bottom: 0.6rem;
        }}
        .ind-title {{ font-weight: 700; color: {COLOR_TEXT}; margin-bottom: 0.3rem; }}
        .ind-desc {{ font-size: 0.86rem; color: {COLOR_TEXT}; opacity: 0.8; line-height: 1.5; }}

        .score-table-wrap {{
            background: {COLOR_SURFACE};
            border: 1px solid {COLOR_BORDER};
            border-radius: 16px;
            padding: 1.1rem 1.3rem;
        }}
        .score-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            padding: 0.55rem 0;
            border-bottom: 1px solid {COLOR_BORDER};
            font-size: 0.88rem;
        }}
        .score-row:last-child {{ border-bottom: none; }}
        .score-label {{ font-weight: 600; color: {COLOR_TEXT}; flex: 1.1; }}
        .score-cond {{ flex: 1; color: {COLOR_TEXT}; opacity: 0.85; }}
        .score-badge {{
            font-weight: 700;
            font-size: 0.78rem;
            padding: 0.15rem 0.55rem;
            border-radius: 999px;
            white-space: nowrap;
        }}

        .result-row {{
            display: flex;
            gap: 1rem;
            margin-top: 1.1rem;
            flex-wrap: wrap;
        }}
        .result-card {{
            flex: 1;
            min-width: 180px;
            border-radius: 14px;
            padding: 0.9rem 1.1rem;
            text-align: center;
        }}
        .result-score {{ font-size: 0.78rem; opacity: 0.85; margin-top: 0.2rem; }}

        .menu-row {{
            display: flex;
            align-items: flex-start;
            gap: 0.9rem;
            padding: 0.7rem 0;
            border-bottom: 1px solid {COLOR_BORDER};
        }}
        .menu-row:last-child {{ border-bottom: none; }}
        .menu-icon {{ font-size: 1.2rem; width: 28px; text-align: center; }}
        .menu-title {{ font-weight: 700; color: {COLOR_TEXT}; font-size: 0.92rem; }}
        .menu-desc {{ font-size: 0.85rem; color: {COLOR_TEXT}; opacity: 0.75; line-height: 1.45; }}
        </style>

        <div class="hero-badge" style="display:inline-block; margin-bottom:0.6rem;">📖 PANDUAN</div>
        <div style="font-family:'Sora','Inter',sans-serif; font-size:1.9rem; font-weight:800; color:{COLOR_TEXT}; margin-bottom:0.3rem;">
            Cara Membaca Dashboard
        </div>
        <div style="color:{COLOR_TEXT}; opacity:0.75; font-size:0.98rem; max-width:720px;">
            Semua sinyal di dashboard ini dihitung dari 3 indikator teknikal klasik. Berikut cara bacanya.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="pg-section-title">📐 Indikator yang dipakai</div>', unsafe_allow_html=True)
    ind_cols = st.columns(3)
    indicators = [
        ("📈", COLOR_ACCENT_SOFT, "MA20 / MA50",
         "Rata-rata harga penutupan 20 & 50 hari terakhir. MA20 di atas MA50 = tren jangka pendek "
         "sedang naik (uptrend), dan sebaliknya."),
        ("⚡", "#F1EDFB", "RSI (14)",
         "Relative Strength Index, mengukur kecepatan naik/turun harga (skala 0-100). "
         "< 30 = oversold (potensi rebound), > 70 = overbought (waspada koreksi)."),
        ("🌊", "#FEF3C7", "MACD",
         "Selisih EMA12 & EMA26 (garis MACD) dibanding EMA9 dari MACD itu sendiri (signal line). "
         "MACD di atas signal = momentum positif."),
    ]
    for col, (icon, bg, title, desc) in zip(ind_cols, indicators):
        with col:
            st.markdown(
                f"""
                <div class="ind-card">
                    <div class="ind-icon" style="background:{bg}">{icon}</div>
                    <div class="ind-title">{title}</div>
                    <div class="ind-desc">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown('<div class="pg-section-title">🧮 Cara sinyal BUY/SELL/HOLD dihitung</div>', unsafe_allow_html=True)
    st.markdown(
        "Setiap indikator menyumbang skor **+1 / 0 / -1**, lalu dijumlah jadi skor total (rentang **-3 sampai +3**):"
    )
    st.markdown(
        f"""
        <div class="score-table-wrap">
            <div class="score-row">
                <div class="score-label">Trend (MA20 vs MA50)</div>
                <div class="score-cond">MA20 &gt; MA50</div>
                <div class="score-badge" style="color:{COLOR_BUY};background:{COLOR_BUY_SOFT}">+1</div>
                <div class="score-cond">MA20 &lt; MA50</div>
                <div class="score-badge" style="color:{COLOR_SELL};background:{COLOR_SELL_SOFT}">-1</div>
            </div>
            <div class="score-row">
                <div class="score-label">RSI</div>
                <div class="score-cond">RSI &lt; 30 (oversold)</div>
                <div class="score-badge" style="color:{COLOR_BUY};background:{COLOR_BUY_SOFT}">+1</div>
                <div class="score-cond">RSI &gt; 70 (overbought)</div>
                <div class="score-badge" style="color:{COLOR_SELL};background:{COLOR_SELL_SOFT}">-1</div>
            </div>
            <div class="score-row">
                <div class="score-label">MACD</div>
                <div class="score-cond">MACD &gt; Signal</div>
                <div class="score-badge" style="color:{COLOR_BUY};background:{COLOR_BUY_SOFT}">+1</div>
                <div class="score-cond">MACD &lt; Signal</div>
                <div class="score-badge" style="color:{COLOR_SELL};background:{COLOR_SELL_SOFT}">-1</div>
            </div>
        </div>
        <div class="result-row">
            <div class="result-card" style="background:{COLOR_BUY_SOFT}">
                <div class="sig-pill" style="color:{COLOR_BUY};background:transparent;font-size:1rem;padding:0">▲ BUY</div>
                <div class="result-score" style="color:{COLOR_BUY}">Skor total ≥ +2</div>
            </div>
            <div class="result-card" style="background:{COLOR_HOLD_SOFT}">
                <div class="sig-pill" style="color:{COLOR_HOLD};background:transparent;font-size:1rem;padding:0">■ HOLD</div>
                <div class="result-score" style="color:{COLOR_HOLD}">Selain BUY/SELL</div>
            </div>
            <div class="result-card" style="background:{COLOR_SELL_SOFT}">
                <div class="sig-pill" style="color:{COLOR_SELL};background:transparent;font-size:1rem;padding:0">▼ SELL</div>
                <div class="result-score" style="color:{COLOR_SELL}">Skor total ≤ -2</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(
        "\"Kekuatan\" sinyal (dots ●○ atau persen %) menunjukkan seberapa besar |skor| relatif terhadap "
        "maksimum 3 — makin banyak dot terisi/persen makin banyak indikator yang sepakat. Catatan: RSI di "
        "rentang 30-70 kontribusinya 0, jadi sinyal BUY/SELL murni bisa terjadi walau RSI netral, asal "
        "trend & MACD sudah searah."
    )

    menu1, menu2 = st.columns(2)
    with menu1:
        st.markdown('<div class="pg-section-title">⚙️ Menu di sidebar</div>', unsafe_allow_html=True)
        sidebar_items = [
            ("📅", "Periode data", "Rentang histori dari Yahoo Finance. Terlalu pendek bisa bikin MA50 "
             "belum terbentuk (DATA KURANG) — pilih minimal 6 bulan, idealnya 1y/2y."),
            ("🕯️", "Interval candle", "Granularitas candle (Harian, dst)."),
            ("⭐", "Watchlist", "Daftar kode saham (tanpa .JK) yang mau dipantau."),
            ("🔁", "Backtest: periode holding", "Khusus halaman Backtest Sinyal — setelah sinyal "
             "BUY/SELL historis muncul, harga dicek N candle ke depan untuk menilai menang/kalah."),
        ]
        for icon, title, desc in sidebar_items:
            st.markdown(
                f"""
                <div class="menu-row">
                    <div class="menu-icon">{icon}</div>
                    <div>
                        <div class="menu-title">{title}</div>
                        <div class="menu-desc">{desc}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with menu2:
        st.markdown('<div class="pg-section-title">🗺️ Halaman yang tersedia</div>', unsafe_allow_html=True)
        page_items = [
            ("📋", "Ringkasan Watchlist", "Tabel semua saham dengan sinyal, kekuatan, dan RSI terkini, "
             "diurutkan BUY → HOLD → SELL."),
            ("📈", "Tren 30 Hari", "Grafik harga 30 hari terakhir per saham, diurutkan dari performa terbaik."),
            ("🔁", "Backtest Sinyal", "Simulasi naif performa sinyal BUY/SELL historis."),
            ("🔍", "Detail per Saham", "Candlestick + MA, RSI, MACD, dan volume lengkap per saham."),
        ]
        for icon, title, desc in page_items:
            st.markdown(
                f"""
                <div class="menu-row">
                    <div class="menu-icon">{icon}</div>
                    <div>
                        <div class="menu-title">{title}</div>
                        <div class="menu-desc">{desc}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")
    st.markdown(
        """
        <div class="disclaimer-box">
            ⚠️ <b>Disclaimer</b>: Seluruh sinyal di dashboard ini berbasis aturan teknikal sederhana
            (rule-based), <b>BUKAN saran finansial</b> dan BUKAN hasil machine learning. Backtest
            bersifat naif (tanpa biaya transaksi/slippage, dievaluasi in-sample). Selalu lakukan riset
            sendiri sebelum mengambil keputusan trading.
        </div>
        """,
        unsafe_allow_html=True,
    )
