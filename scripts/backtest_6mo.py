"""6-month hindsight backtest of the calculator's default allocation.
Uses the most liquid listing per name, converts to USD, dividend-adjusted closes."""
import warnings
warnings.filterwarnings("ignore")
import pandas as pd
import yfinance as yf

# (framework ticker, data ticker, fx pair or None, tier)
NAMES = [
    ("WRTBY", "WRT1V.HE", "EURUSD=X", 1), ("TSNLF", "TSTL.L", "GBPUSD=X", 1),
    ("CLPBY", "CLPBY", None, 1), ("TDVXF", "TDVOX.ST", "SEKUSD", 1),
    ("YMM", "YMM", None, 1), ("SBDHF", "1414.T", "JPYUSD", 1),
    ("DLEGF", "DELTA.BK", "THBUSD", 1),
    ("BMBRF", "BIMAS.IS", "TRYUSD", 2), ("KMDA", "KMDA", None, 2),
    ("BB", "BB", None, 2), ("ENGCF", "ENGCON-B.ST", "SEKUSD", 2),
    ("CRMD", "CRMD", None, 2), ("SCTTF", "SCT.NZ", "NZDUSD=X", 2),
    ("CODYY", "SGO.PA", "EURUSD=X", 2),
    ("PEJMF", "9996.HK", "HKDUSD", 3), ("CERS", "CERS", None, 3),
    ("SHLS", "SHLS", None, 3), ("DMTRF", "7777.T", "JPYUSD", 3),
    ("ADMA", "ADMA", None, 3), ("BIRMF", "BRM.V", "CADUSD", 3),
    ("WSIOF", "3393.HK", "HKDUSD", 3),
]
INVERT = {"SEKUSD": "USDSEK=X", "JPYUSD": "USDJPY=X", "THBUSD": "USDTHB=X",
          "TRYUSD": "USDTRY=X", "HKDUSD": "USDHKD=X", "CADUSD": "USDCAD=X"}

tickers = sorted({d for _, d, _, _ in NAMES} | {"^GSPC"})
fx_syms = sorted({INVERT.get(f, f) for _, _, f, _ in NAMES if f})

px = yf.download(tickers, period="7mo", progress=False, threads=True, auto_adjust=True)["Close"]
fx = yf.download(fx_syms, period="7mo", progress=False, threads=True, auto_adjust=True)["Close"]

END = px.index[-1]
START = END - pd.DateOffset(months=6)

def ret_usd(data_tk, fxp):
    s = px[data_tk].dropna()
    s0 = s[s.index >= START]
    if len(s0) < 10:
        return None, None, None
    p0, p1 = s0.iloc[0], s0.iloc[-1]
    r_local = p1 / p0 - 1
    if fxp:
        sym = INVERT.get(fxp, fxp)
        f = fx[sym].dropna()
        f0 = f[f.index >= START]
        fx0, fx1 = f0.iloc[0], f0.iloc[-1]
        fx_ret = (fx1 / fx0 - 1)
        if sym.startswith("USD"):  # inverted pair
            r_usd = (1 + r_local) / (1 + fx_ret) - 1
        else:
            r_usd = (1 + r_local) * (1 + fx_ret) - 1
    else:
        r_usd = r_local
    return r_local, r_usd, str(s0.index[0].date())

W = {1: 0.60 / 7, 2: 0.28 / 7, 3: 0.10 / 7}
port, rows = 0.0, []
for fw, dt, fxp, tier in NAMES:
    r_l, r_u, d0 = ret_usd(dt, fxp)
    if r_u is None:
        print(f"{fw}: NO DATA")
        continue
    w = W[tier]
    port += w * r_u
    rows.append((fw, tier, r_l, r_u, w, d0))
    print(f"T{tier} {fw:6s} via {dt:12s} local {r_l:+7.1%}  USD {r_u:+7.1%}  w={w:.4f}")

spx = ret_usd("^GSPC", None)[1]
print(f"\nwindow: {START.date()} -> {END.date()}")
print(f"portfolio 6-mo return (60/28/10 equal-weight, 2% cash): {port:+.2%}")
print(f"S&P 500 same window: {spx:+.2%}")
base = 20282.65
print(f"applied to $20,282.65 (your value 6 months ago): ${base*(1+port):,.2f}  (gain ${base*port:,.2f})")
print(f"your actual: $24,212.91 (gain $3,930.26, +19.36%)")
