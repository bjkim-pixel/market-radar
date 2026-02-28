"""
KIS API 데이터 수집 v2
- 종목명 + 시장구분(KOSPI/KOSDAQ) 정확히 수집
- 투자자별 세부 수급 + 기간별(일/주/월) 집계
- 거래주체별 top 종목
- 기간별 데이터 누적 저장
- 52주 신고가 판별
- 시장 요약 자동 생성
"""
import os, json, time, requests, datetime
import pandas as pd
import numpy as np
from pathlib import Path

APP_KEY    = os.environ["KIS_APP_KEY"]
APP_SECRET = os.environ["KIS_APP_SECRET"]
ACCOUNT_NO = os.environ["KIS_ACCOUNT_NO"]
BASE_URL   = "https://openapi.koreainvestment.com:9443"

# 종목코드: (종목명, 시장)
WATCH_LIST = {
    "005930": ("삼성전자",         "KOSPI"),
    "000660": ("SK하이닉스",       "KOSPI"),
    "005380": ("현대차",           "KOSPI"),
    "042700": ("한미반도체",       "KOSPI"),
    "373220": ("LG에너지솔루션",   "KOSPI"),
    "035420": ("NAVER",            "KOSPI"),
    "035720": ("카카오",           "KOSPI"),
    "003670": ("포스코퓨처엠",     "KOSPI"),
    "012450": ("한화에어로스페이스","KOSPI"),
    "178320": ("서진시스템",       "KOSDAQ"),
    "226950": ("올릭스",           "KOSDAQ"),
    "247540": ("에코프로비엠",     "KOSDAQ"),
    "091990": ("셀트리온헬스케어", "KOSDAQ"),
}

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


def get_token():
    cache = DATA_DIR / "token_cache.json"
    if cache.exists():
        c = json.loads(cache.read_text())
        if "exp" in c and datetime.datetime.now() < datetime.datetime.fromisoformat(c["exp"]) - datetime.timedelta(minutes=10):
            return c["token"]
    r = requests.post(f"{BASE_URL}/oauth2/tokenP",
        json={"grant_type": "client_credentials", "appkey": APP_KEY, "appsecret": APP_SECRET},
        timeout=10)
    r.raise_for_status()
    token = r.json()["access_token"]
    cache.write_text(json.dumps({
        "token": token,
        "exp": (datetime.datetime.now() + datetime.timedelta(hours=23)).isoformat()
    }))
    return token


def kis_get(path, params, tr_id, token):
    r = requests.get(f"{BASE_URL}{path}",
        headers={"authorization": f"Bearer {token}", "appkey": APP_KEY,
                 "appsecret": APP_SECRET, "tr_id": tr_id, "custtype": "P"},
        params=params, timeout=10)
    r.raise_for_status()
    d = r.json()
    if d.get("rt_cd") != "0":
        raise RuntimeError(f"KIS 오류: {d.get('msg1')} [{tr_id}]")
    return d


def fmt_bil(n):
    n = int(n)
    if n >= 1_000_000_000_000: return f"{n/1_000_000_000_000:.1f}조"
    if n >= 100_000_000:        return f"{n/100_000_000:.0f}억"
    return str(n)


def fmt_amt(n):
    s = "+" if n >= 0 else ""
    return s + fmt_bil(abs(n))


# ── 지수 ──────────────────────────────────────────────────
def fetch_indices(token):
    result = []
    for code, name in [("0001","KOSPI"), ("1001","KOSDAQ"), ("2001","KSP200")]:
        try:
            d = kis_get("/uapi/domestic-stock/v1/quotations/inquire-index-price",
                        {"iscd": code}, "FHPUP02100000", token)["output"]
            vol_raw = int(d.get("acml_tr_pbmn", "0").replace(",", "") or 0)
            result.append({
                "name": name,
                "value": float(d.get("bstp_nmix_prpr", 0)),
                "change": float(d.get("bstp_nmix_prdy_ctrt", 0)),
                "diff": float(d.get("bstp_nmix_prdy_vrss", 0)),
                "vol": fmt_bil(vol_raw),
                "vol_raw": vol_raw,
            })
            time.sleep(0.2)
        except Exception as e:
            print(f"  지수 실패({name}): {e}")
    return result


# ── 종목 현재가 ───────────────────────────────────────────
def fetch_price(code, fallback_name, fallback_market, token):
    d = kis_get("/uapi/domestic-stock/v1/quotations/inquire-price",
                {"fid_cond_mrkt_div_code": "J", "fid_input_iscd": code},
                "FHKST01010100", token)["output"]

    # 종목명: API 우선, 없으면 WATCH_LIST
    name = d.get("hts_kor_isnm", "").strip() or fallback_name

    # 시장구분
    mkt_raw = d.get("rprs_mrkt_kor_name", "")
    if "코스닥" in mkt_raw or "KOSDAQ" in mkt_raw.upper():
        market = "KOSDAQ"
    elif "코스피" in mkt_raw or "KOSPI" in mkt_raw.upper():
        market = "KOSPI"
    else:
        market = fallback_market

    return {
        "code": code,
        "name": name,
        "market": market,
        "price": int(d.get("stck_prpr", 0)),
        "change": float(d.get("prdy_ctrt", 0)),
        "diff": int(d.get("prdy_vrss", 0)),
        "volume": int(d.get("acml_vol", 0)),
        "tr_val": int(d.get("acml_tr_pbmn", "0").replace(",", "") or 0),
        "high52": int(d.get("w52_hgpr", 0)),
        "low52":  int(d.get("w52_lwpr", 0)),
        "mktcap": int(d.get("hts_avls", 0)),
        "sector": d.get("bstp_kor_isnm", ""),
    }


# ── 일봉 ─────────────────────────────────────────────────
def fetch_ohlcv(code, token, count=60):
    today = datetime.date.today().strftime("%Y%m%d")
    rows = kis_get(
        "/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice",
        {"fid_cond_mrkt_div_code": "J", "fid_input_iscd": code,
         "fid_input_date_1": "19000101", "fid_input_date_2": today,
         "fid_period_div_code": "D", "fid_org_adj_prc": "0"},
        "FHKST03010100", token).get("output2", [])[:count]
    return [{"date": r.get("stck_bsop_date",""),
             "open": int(r.get("stck_oprc", 0)),
             "high": int(r.get("stck_hgpr", 0)),
             "low":  int(r.get("stck_lwpr", 0)),
             "close":int(r.get("stck_clpr", 0)),
             "volume":int(r.get("acml_vol", 0))}
            for r in reversed(rows)]


# ── 종목별 수급 ───────────────────────────────────────────
def fetch_stock_supply(code, token, days=30):
    today = datetime.date.today().strftime("%Y%m%d")
    past  = (datetime.date.today() - datetime.timedelta(days=days)).strftime("%Y%m%d")
    try:
        rows = kis_get(
            "/uapi/domestic-stock/v1/quotations/inquire-investor",
            {"fid_cond_mrkt_div_code": "J", "fid_input_iscd": code,
             "fid_input_date_1": past, "fid_input_date_2": today,
             "fid_period_div_code": "D"},
            "FHKST01010900", token).get("output", [])
        return [{"date": r.get("stck_bsop_date",""),
                 "foreign":     int(r.get("frgn_ntby_qty", 0)),
                 "inst":        int(r.get("orgn_ntby_qty", 0)),
                 "indiv":       int(r.get("indv_ntby_qty", 0)),
                 "foreign_amt": int(r.get("frgn_ntby_tr_pbmn", 0)),
                 "inst_amt":    int(r.get("orgn_ntby_tr_pbmn", 0)),
                 "indiv_amt":   int(r.get("indv_ntby_tr_pbmn", 0))}
                for r in reversed(rows)]
    except Exception as e:
        print(f"    수급 실패({code}): {e}")
        return []


# ── 시장 전체 수급 ────────────────────────────────────────
def fetch_market_supply(token):
    result = {}
    for iscd, label in [("0001","kospi"), ("1001","kosdaq")]:
        try:
            today = datetime.date.today().strftime("%Y%m%d")
            mkt = "J" if label == "kospi" else "Q"
            rows = kis_get(
                "/uapi/domestic-stock/v1/quotations/inquire-investor",
                {"fid_cond_mrkt_div_code": mkt, "fid_input_iscd": iscd,
                 "fid_input_date_1": today, "fid_input_date_2": today,
                 "fid_period_div_code": "D"},
                "FHKST01010900", token).get("output", [])
            if rows:
                r = rows[0]
                result[label] = {
                    "foreign_net": int(r.get("frgn_ntby_tr_pbmn", 0)),
                    "inst_net":    int(r.get("orgn_ntby_tr_pbmn", 0)),
                    "indiv_net":   int(r.get("indv_ntby_tr_pbmn", 0)),
                }
            time.sleep(0.25)
        except Exception as e:
            print(f"  시장수급 실패({label}): {e}")

    combined = {
        "foreign_net": sum(v.get("foreign_net", 0) for v in result.values()),
        "inst_net":    sum(v.get("inst_net", 0)    for v in result.values()),
        "indiv_net":   sum(v.get("indiv_net", 0)   for v in result.values()),
        "by_market":   result,
    }
    return combined


# ── 기간별 수급 집계 ──────────────────────────────────────
def summarize_supply_periods(rows):
    if not rows:
        return {"day": {}, "week": {}, "month": {}}
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d", errors="coerce")
    df = df.dropna(subset=["date"])
    if df.empty:
        return {"day": {}, "week": {}, "month": {}}
    today = df["date"].max()

    def agg(sub):
        return {
            "foreign": int(sub["foreign_amt"].sum()),
            "inst":    int(sub["inst_amt"].sum()),
            "indiv":   int(sub["indiv_amt"].sum()),
        }
    return {
        "day":   agg(df[df["date"] == today]),
        "week":  agg(df[df["date"] >= today - pd.Timedelta(days=5)]),
        "month": agg(df[df["date"] >= today - pd.Timedelta(days=22)]),
    }


# ── 거래주체별 Top 종목 ───────────────────────────────────
def calc_top_traders(stocks):
    out = {}
    for actor, key in [("foreign","foreign_today"), ("inst","inst_today"), ("indiv","indiv_today")]:
        buying  = sorted([s for s in stocks if s.get(key,0)>0], key=lambda x:x.get(key,0), reverse=True)
        selling = sorted([s for s in stocks if s.get(key,0)<0], key=lambda x:x.get(key,0))
        out[actor] = {
            "top_buy":  [{"name":s["name"],"market":s["market"],"amt":s[key]} for s in buying[:5]],
            "top_sell": [{"name":s["name"],"market":s["market"],"amt":s[key]} for s in selling[:5]],
        }
    return out


# ── Phase 신호 ────────────────────────────────────────────
def calc_phase(ohlcv, supply, mktcap):
    empty = {"phase":"","phase_key":"none","smp":0,"muges_ratio":1,"vol_ratio":1,"f_consec":0,"i_consec":0,"obv_above_ma":False}
    if not ohlcv or len(ohlcv) < 21:
        return empty
    df = pd.DataFrame(ohlcv)
    for c in ["close","volume","open","high","low"]:
        df[c] = pd.to_numeric(df[c])

    df["avg_p"]   = (df["high"] + df["low"] + df["close"]) / 3
    df["muges"]   = df["avg_p"] * df["volume"] / (df["close"] * df["volume"].replace(0, np.nan))
    df["muges_ma20"] = df["muges"].rolling(20).mean()

    obv = [0]
    for i in range(1, len(df)):
        if   df["close"].iloc[i] > df["close"].iloc[i-1]: obv.append(obv[-1] + df["volume"].iloc[i])
        elif df["close"].iloc[i] < df["close"].iloc[i-1]: obv.append(obv[-1] - df["volume"].iloc[i])
        else: obv.append(obv[-1])
    df["obv"] = obv
    df["obv_ma20"] = pd.Series(obv).rolling(20).mean().values
    df["vol_ma20"] = df["volume"].rolling(20).mean()
    df["vol_ratio"]= df["volume"] / df["vol_ma20"].replace(0, np.nan)

    f_consec = i_consec = 0
    if supply:
        sup = pd.DataFrame(supply)
        sup["date"] = sup["date"].astype(str)
        df["date"]  = df["date"].astype(str)
        df = df.merge(sup[["date","foreign","inst","foreign_amt","inst_amt"]], on="date", how="left")
        df[["foreign","inst","foreign_amt","inst_amt"]] = df[["foreign","inst","foreign_amt","inst_amt"]].fillna(0)
        if mktcap > 0:
            df["smp"] = (df["foreign_amt"] + df["inst_amt"]).rolling(10).sum() / (mktcap * 1e8) * 100
        else:
            df["smp"] = 0.0
        def consec(s):
            c = 0
            for v in reversed(s.dropna().tolist()):
                if v > 0: c += 1
                else: break
            return c
        f_consec = consec(df["foreign"])
        i_consec = consec(df["inst"])
    else:
        df["foreign"] = df["inst"] = df["smp"] = 0.0

    t   = df.iloc[-1]
    smp = float(t.get("smp", 0) or 0)
    mm  = float(t.get("muges_ma20", 1) or 1)
    mr  = float(t.get("muges", 1) or 1) / mm if mm else 1
    vr  = float(t.get("vol_ratio", 1) or 1)
    obv_up = float(t["obv"]) > (float(t["obv_ma20"]) if not pd.isna(t["obv_ma20"]) else 0)
    chg = (float(t["close"]) - float(df.iloc[-2]["close"])) / float(df.iloc[-2]["close"]) * 100 if len(df)>=2 else 0
    ft  = float(t.get("foreign", 0) or 0)
    it_ = float(t.get("inst", 0) or 0)

    if   smp>0 and f_consec>=3 and it_>0 and mr<0.8 and vr<1.5: phase,key="⭐ GOLDEN","golden"
    elif vr>=2.0 and ft>0:                                         phase,key="🟢 P2 거래량돌파","p2"
    elif f_consec>=5 and smp>0 and vr>=1.2:                       phase,key="🟢 P2 수급가속","p2"
    elif ft>0 and it_>0 and vr>=1.3 and smp>0 and f_consec>=2:   phase,key="🟢 P2 상승초기","p2"
    elif smp>0 and f_consec>=3 and it_>0:                         phase,key="🔵 P1 수급복합","p1"
    elif mr<0.5 and smp>0 and ft>0:                               phase,key="🔵 P1 조용매집","p1"
    elif obv_up and chg<=0:                                        phase,key="🔵 P1 OBV매집","p1"
    elif mr>3.0 and ft<0:                                          phase,key="🔴 P3 분산경고","p3"
    elif ft<0 and it_<0:                                           phase,key="🔴 P3 손바뀜경고","p3"
    else:                                                           phase,key="","none"

    return {"phase":phase,"phase_key":key,"smp":round(smp,2),"muges_ratio":round(mr,2),
            "vol_ratio":round(vr,2),"f_consec":f_consec,"i_consec":i_consec,"obv_above_ma":bool(obv_up)}


# ── 과거 데이터 누적 ──────────────────────────────────────
def load_history():
    p = DATA_DIR / "history.json"
    return json.loads(p.read_text()) if p.exists() else {}

def save_history(hist):
    (DATA_DIR / "history.json").write_text(json.dumps(hist, ensure_ascii=False))

def append_history(hist, date_str, stocks):
    hist[date_str] = {s["code"]: {
        "name": s["name"], "market": s["market"],
        "price": s["price"], "change": s["change"],
        "phase": s.get("phase",""), "phase_key": s.get("phase_key","none"),
    } for s in stocks}
    keys = sorted(hist.keys())
    for k in keys[:-60]: del hist[k]
    return hist


# ── 시장 요약 텍스트 ──────────────────────────────────────
def make_summary(indices, ms, stocks, ps):
    lines = []
    kospi  = next((i for i in indices if i["name"]=="KOSPI"),  None)
    kosdaq = next((i for i in indices if i["name"]=="KOSDAQ"), None)

    if kospi and kosdaq:
        lines.append(
            f"코스피 {kospi['value']:,.2f} ({'+' if kospi['change']>=0 else ''}{kospi['change']:.2f}%) | "
            f"코스닥 {kosdaq['value']:,.2f} ({'+' if kosdaq['change']>=0 else ''}{kosdaq['change']:.2f}%)"
        )

    fn = ms.get("foreign_net",0)
    in_ = ms.get("inst_net",0)
    iv  = ms.get("indiv_net",0)
    lines.append(f"외국인 {fmt_amt(fn)} | 기관 {fmt_amt(in_)} | 개인 {fmt_amt(iv)}")

    if ps["golden"] > 0:
        names = [s["name"] for s in stocks if s.get("phase_key")=="golden"]
        lines.append(f"⭐ GOLDEN {ps['golden']}종목: {', '.join(names)}")
    if ps["p2"] > 0:
        names = [s["name"] for s in stocks if s.get("phase_key")=="p2"]
        lines.append(f"🟢 P2 상승신호 {ps['p2']}종목: {', '.join(names)}")
    if ps["p3"] > 0:
        names = [s["name"] for s in stocks if s.get("phase_key")=="p3"]
        lines.append(f"⚠️ P3 경고 {ps['p3']}종목: {', '.join(names)}")

    nh = [s["name"] for s in stocks if "신고가" in s.get("nh_flag","")]
    if nh:
        lines.append(f"🔥 52주 신고가: {', '.join(nh)}")

    return lines


# ── 메인 ──────────────────────────────────────────────────
def main():
    now_kst   = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    today_str = now_kst.strftime("%Y-%m-%d")
    now_str   = now_kst.strftime("%Y-%m-%d %H:%M")
    print(f"\n{'='*55}\n📡 수집 시작: {now_str} KST\n{'='*55}")

    token = get_token()
    print("✅ 토큰 OK")

    # 지수
    print("\n📊 지수 수집...")
    indices = fetch_indices(token)

    # 시장 수급
    print("💰 시장 수급 수집...")
    market_supply = fetch_market_supply(token)
    time.sleep(0.3)

    # 종목별
    stocks = []
    print(f"\n📈 종목 수집 ({len(WATCH_LIST)}개)...")
    for code, (name, market) in WATCH_LIST.items():
        try:
            print(f"  [{code}] {name} ", end="", flush=True)
            stock  = fetch_price(code, name, market, token); time.sleep(0.25)
            ohlcv  = fetch_ohlcv(code, token, 60);           time.sleep(0.25)
            supply = fetch_stock_supply(code, token, 30);    time.sleep(0.25)

            sig = calc_phase(ohlcv, supply, stock["mktcap"])
            stock.update(sig)

            # 52주 신고가 판별
            p, h = stock["price"], stock["high52"]
            if h > 0:
                r = p / h * 100
                stock["nh_flag"] = "🔥52주신고가" if r >= 99.5 else "📍신고가근접" if r >= 97 else ""
                stock["nh_ratio"] = round(r, 1)
            else:
                stock["nh_flag"] = ""; stock["nh_ratio"] = 0

            # 수급 집계
            stock["supply_periods"] = summarize_supply_periods(supply)

            # 오늘 수급
            td = supply[-1] if supply else {}
            stock["foreign_today"] = td.get("foreign_amt", 0)
            stock["inst_today"]    = td.get("inst_amt",    0)
            stock["indiv_today"]   = td.get("indiv_amt",   0)

            stocks.append(stock)
            print(f"→ {stock['market']} | {stock['phase'] or '신호없음'}")
        except Exception as e:
            print(f"\n  ⚠️ {code} 실패: {e}")

    top_traders = calc_top_traders(stocks)

    hist = load_history()
    hist = append_history(hist, today_str, stocks)
    save_history(hist)

    ps = {
        "golden":   sum(1 for s in stocks if s.get("phase_key")=="golden"),
        "p1":       sum(1 for s in stocks if s.get("phase_key")=="p1"),
        "p2":       sum(1 for s in stocks if s.get("phase_key")=="p2"),
        "p3":       sum(1 for s in stocks if s.get("phase_key")=="p3"),
        "new_high": sum(1 for s in stocks if "신고가" in s.get("nh_flag","")),
    }
    summary_lines = make_summary(indices, market_supply, stocks, ps)

    payload = {
        "updated_at":     now_str,
        "date":           today_str,
        "is_market_open": 9*60+5 <= now_kst.hour*60+now_kst.minute <= 15*60+30,
        "indices":        indices,
        "market_supply":  market_supply,
        "stocks":         stocks,
        "top_traders":    top_traders,
        "phase_stats":    ps,
        "summary_lines":  summary_lines,
    }
    (DATA_DIR/"market.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"\n✅ 완료 → data/market.json | 종목 {len(stocks)}개 | GOLDEN {ps['golden']} | 신고가 {ps['new_high']}")


if __name__ == "__main__":
    main()
