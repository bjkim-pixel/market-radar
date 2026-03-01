"""
KIS API 데이터 수집 v5
- 지수 API 파라미터 수정 (fid_cond_mrkt_div_code 제거)
- 거래량 순위 엔드포인트 수정 (/quotations/volume-rank)
- 신고가 순위 엔드포인트 수정
- KOSDAQ 시장 수급 파라미터 수정
- 전체 시장 자동 스캔 유지
"""
import os, json, time, requests, datetime, math
import pandas as pd
import numpy as np
from pathlib import Path

APP_KEY    = os.environ["KIS_APP_KEY"]
APP_SECRET = os.environ["KIS_APP_SECRET"]
ACCOUNT_NO = os.environ["KIS_ACCOUNT_NO"]
BASE_URL   = "https://openapi.koreainvestment.com:9443"

MAX_STOCKS  = 50
SUPPLY_DAYS = 30
OHLCV_COUNT = 60

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# ── 유틸 ───────────────────────────────────────────────
def safe_int(v, default=0):
    try:
        s = str(v).replace(",", "").strip()
        return int(float(s)) if s else default
    except:
        return default

def safe_float(v, default=0.0):
    try:
        s = str(v).replace(",", "").strip()
        f = float(s)
        return default if (math.isnan(f) or math.isinf(f)) else f
    except:
        return default

def fmt_bil(n):
    n = abs(int(n or 0))
    if n >= 1_000_000_000_000: return f"{n/1_000_000_000_000:.1f}조"
    if n >= 100_000_000:        return f"{n/100_000_000:.0f}억"
    return str(n)

def fmt_amt(n):
    return ("+" if n >= 0 else "-") + fmt_bil(abs(n))

def clean_nan(obj):
    if isinstance(obj, dict):  return {k: clean_nan(v) for k, v in obj.items()}
    if isinstance(obj, list):  return [clean_nan(v) for v in obj]
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)): return 0.0
    return obj

# ── 토큰 ───────────────────────────────────────────────
def get_token():
    cache = DATA_DIR / "token_cache.json"
    if cache.exists():
        try:
            c = json.loads(cache.read_text())
            if "exp" in c and datetime.datetime.now() < datetime.datetime.fromisoformat(c["exp"]) - datetime.timedelta(minutes=10):
                return c["token"]
        except:
            pass
    r = requests.post(f"{BASE_URL}/oauth2/tokenP",
        json={"grant_type": "client_credentials", "appkey": APP_KEY, "appsecret": APP_SECRET},
        timeout=15)
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
        params=params, timeout=15)
    r.raise_for_status()
    d = r.json()
    if d.get("rt_cd") != "0":
        raise RuntimeError(f"KIS 오류: {d.get('msg1','?')} [{tr_id}]")
    return d

# ── 지수 조회 (파라미터 수정: fid_cond_mrkt_div_code 제거) ──
def fetch_indices(token):
    result = []
    # iscd만 파라미터로 전달 (fid_cond_mrkt_div_code 불필요)
    for code, name in [("0001","KOSPI"), ("1001","KOSDAQ"), ("2001","KSP200")]:
        try:
            d = kis_get(
    "/uapi/domestic-stock/v1/quotations/inquire-index-price",
    {"fid_cond_mrkt_div_code": "U", "fid_input_iscd": code},
    "FHPUP02100000",
    token
)
            out = d.get("output") or d.get("output1") or {}
            if isinstance(out, list):
                out = out[0] if out else {}

            value   = safe_float(out.get("bstp_nmix_prpr") or out.get("stck_prpr") or 0)
            change  = safe_float(out.get("bstp_nmix_prdy_ctrt") or out.get("prdy_ctrt") or 0)
            diff    = safe_float(out.get("bstp_nmix_prdy_vrss") or out.get("prdy_vrss") or 0)
            vol_raw = safe_int(str(out.get("acml_tr_pbmn") or "0").replace(",",""))

            result.append({
                "name": name, "value": value, "change": change,
                "diff": diff, "vol": fmt_bil(vol_raw), "vol_raw": vol_raw,
            })
            print(f"  [{name}] {value:,.2f} ({change:+.2f}%)")
            time.sleep(0.3)
        except Exception as e:
            print(f"  지수 실패({name}): {e}")
    return result

# ── 거래대금 상위 종목 (엔드포인트 수정) ────────────────
def fetch_top_volume_stocks(token, market="J", top_n=100):
    if market != "J":
        return fetch_fallback_stocks(token, market)
    stocks = []
    try:
        d = kis_get(
            "/uapi/domestic-stock/v1/quotations/volume-rank",
            {
                "fid_cond_mrkt_div_code": market,
                "fid_cond_scr_div_code":  "20171",
                "fid_input_iscd":         "0000",
                "fid_div_cls_code":       "0",
                "fid_blng_cls_code":      "0",
                "fid_trgt_cls_code":      "111111111",
                "fid_trgt_exls_cls_code": "000000",
                "fid_input_price_1":      "",
                "fid_input_price_2":      "",
                "fid_vol_cnt":            "",
                "fid_input_date_1":       "",
            },
            "FHPST01710000",
            token
        )
        rows = d.get("output", [])
        mkt_label = "KOSPI" if market == "J" else "KOSDAQ"
        for r in rows[:top_n]:
            price = safe_int(r.get("stck_prpr", 0))
            code  = r.get("mksc_shrn_iscd", "").strip()
            if not price or not code:
                continue
            stocks.append({
                "code":   code,
                "name":   r.get("hts_kor_isnm", "").strip(),
                "market": mkt_label,
                "price":  price,
                "change": safe_float(r.get("prdy_ctrt", 0)),
                "diff":   safe_int(r.get("prdy_vrss", 0)),
                "volume": safe_int(r.get("acml_vol", 0)),
                "tr_val": safe_int(r.get("acml_tr_pbmn", 0)),
                "high52": safe_int(r.get("w52_hgpr", 0)),
                "low52":  safe_int(r.get("w52_lwpr", 0)),
                "mktcap": safe_int(r.get("hts_avls", 0)),
                "sector": r.get("bstp_kor_isnm", "").strip(),
            })
        print(f"  [{mkt_label}] 거래대금 상위 {len(stocks)}개")
        time.sleep(0.5)
    except Exception as e:
        print(f"  거래대금 순위 실패({market}): {e}")
        stocks = fetch_fallback_stocks(token, market)
    return stocks

# ── 신고가 근접 종목 (엔드포인트 수정) ─────────────────
def fetch_near_high_stocks(token, market="J", top_n=30):
    """
    TR: FHPST01700000
    올바른 엔드포인트: /uapi/domestic-stock/v1/quotations/high-low-price-rank
    """
    stocks = []
    try:
        d = kis_get(
            "/uapi/domestic-stock/v1/quotations/high-low-price-rank",  # ← 수정
            {
                "fid_cond_mrkt_div_code": market,
                "fid_cond_scr_div_code":  "20170",
                "fid_input_iscd":         "0000",
                "fid_rank_sort_cls_code": "0",
                "fid_input_cnt_1":        "0",
                "fid_input_date_1":       "",
                "fid_trgt_cls_code":      "111111111",
                "fid_trgt_exls_cls_code": "000000",
                "fid_input_price_1":      "",
                "fid_input_price_2":      "",
                "fid_vol_cnt":            "",
            },
            "FHPST01700000",
            token
        )
        rows = d.get("output", [])
        mkt_label = "KOSPI" if market == "J" else "KOSDAQ"
        for r in rows[:top_n]:
            price = safe_int(r.get("stck_prpr", 0))
            code  = r.get("mksc_shrn_iscd", "").strip()
            if not price or not code:
                continue
            stocks.append({
                "code":   code,
                "name":   r.get("hts_kor_isnm", "").strip(),
                "market": mkt_label,
                "price":  price,
                "change": safe_float(r.get("prdy_ctrt", 0)),
                "diff":   safe_int(r.get("prdy_vrss", 0)),
                "volume": safe_int(r.get("acml_vol", 0)),
                "tr_val": safe_int(r.get("acml_tr_pbmn", 0)),
                "high52": safe_int(r.get("w52_hgpr", 0)),
                "low52":  safe_int(r.get("w52_lwpr", 0)),
                "mktcap": safe_int(r.get("hts_avls", 0)),
                "sector": r.get("bstp_kor_isnm", "").strip(),
            })
        print(f"  [{mkt_label}] 신고가 근접 {len(stocks)}개")
        time.sleep(0.5)
    except Exception as e:
        print(f"  신고가 조회 실패({market}): {e}")
    return stocks

# ── 폴백: 고정 종목 리스트 (API 실패 시) ───────────────
def fetch_fallback_stocks(token, market="J"):
    mkt_label = "KOSPI" if market == "J" else "KOSDAQ"
    if market == "J":
        codes = [
            ("005930","삼성전자"),("000660","SK하이닉스"),("005380","현대차"),
            ("042700","한미반도체"),("373220","LG에너지솔루션"),("035420","NAVER"),
            ("035720","카카오"),("003670","포스코퓨처엠"),("012450","한화에어로스페이스"),
            ("000270","기아"),("068270","셀트리온"),("105560","KB금융"),
            ("055550","신한지주"),("086790","하나금융지주"),("032830","삼성생명"),
            ("017670","SK텔레콤"),("030200","KT"),("011200","HMM"),
            ("009150","삼성전기"),("066570","LG전자"),
        ]
    else:
        codes = [
            ("178320","서진시스템"),("226950","올릭스"),("247540","에코프로비엠"),
            ("086520","에코프로"),("196170","알테오젠"),("263750","펄어비스"),
            ("293490","카카오게임즈"),("112040","위메이드"),("251270","넷마블"),
            ("035900","JYP엔터"),
        ]
    stocks = []
    for code, name in codes:
        try:
            d = kis_get("/uapi/domestic-stock/v1/quotations/inquire-price",
                        {"fid_cond_mrkt_div_code": "J", "fid_input_iscd": code},
                        "FHKST01010100", token)["output"]
            price = safe_int(d.get("stck_prpr", 0))
            if not price: continue
            mkt_raw = d.get("rprs_mrkt_kor_name","")
            market_l = "KOSDAQ" if "코스닥" in mkt_raw else "KOSPI"
            stocks.append({
                "code": code, "name": d.get("hts_kor_isnm","").strip() or name,
                "market": market_l, "price": price,
                "change": safe_float(d.get("prdy_ctrt",0)),
                "diff":   safe_int(d.get("prdy_vrss",0)),
                "volume": safe_int(d.get("acml_vol",0)),
                "tr_val": safe_int(d.get("acml_tr_pbmn",0)),
                "high52": safe_int(d.get("w52_hgpr",0)),
                "low52":  safe_int(d.get("w52_lwpr",0)),
                "mktcap": safe_int(d.get("hts_avls",0)),
                "sector": d.get("bstp_kor_isnm","").strip(),
            })
            time.sleep(0.2)
        except Exception as e:
            print(f"    {code} 실패: {e}")
    print(f"  [{mkt_label}] 폴백 {len(stocks)}개")
    return stocks

# ── 시장 전체 수급 (KOSDAQ 파라미터 수정) ───────────────
def fetch_market_supply(token):
    result = {}
    today = datetime.date.today().strftime("%Y%m%d")

    # KOSPI: fid_cond_mrkt_div_code=J, iscd=0001
    try:
        rows = kis_get(
            "/uapi/domestic-stock/v1/quotations/inquire-investor",
            {"fid_cond_mrkt_div_code": "J",
             "fid_input_iscd": "0001",
             "fid_input_date_1": today,
             "fid_input_date_2": today,
             "fid_period_div_code": "D"},
            "FHKST01010900", token
        ).get("output", [])
        if rows:
            r = rows[0]
            fn  = safe_int(r.get("frgn_ntby_tr_pbmn",0)) or safe_int(r.get("frgn_ntby_qty",0))
            inn = safe_int(r.get("orgn_ntby_tr_pbmn",0)) or safe_int(r.get("orgn_ntby_qty",0))
            ivn = safe_int(r.get("indv_ntby_tr_pbmn",0)) or safe_int(r.get("indv_ntby_qty",0))
            result["kospi"] = {"foreign_net": fn, "inst_net": inn, "indiv_net": ivn}
            print(f"  시장수급[KOSPI]: 외인={fmt_amt(fn)}, 기관={fmt_amt(inn)}, 개인={fmt_amt(ivn)}")
        time.sleep(0.3)
    except Exception as e:
        print(f"  KOSPI 수급 실패: {e}")

    # KOSDAQ: fid_cond_mrkt_div_code=J, iscd=1001 (KOSDAQ도 J 사용)
    try:
        rows = kis_get(
            "/uapi/domestic-stock/v1/quotations/inquire-investor",
            {"fid_cond_mrkt_div_code": "J",   # ← KOSDAQ도 J
             "fid_input_iscd": "1001",          # ← iscd로 구분
             "fid_input_date_1": today,
             "fid_input_date_2": today,
             "fid_period_div_code": "D"},
            "FHKST01010900", token
        ).get("output", [])
        if rows:
            r = rows[0]
            fn  = safe_int(r.get("frgn_ntby_tr_pbmn",0)) or safe_int(r.get("frgn_ntby_qty",0))
            inn = safe_int(r.get("orgn_ntby_tr_pbmn",0)) or safe_int(r.get("orgn_ntby_qty",0))
            ivn = safe_int(r.get("indv_ntby_tr_pbmn",0)) or safe_int(r.get("indv_ntby_qty",0))
            result["kosdaq"] = {"foreign_net": fn, "inst_net": inn, "indiv_net": ivn}
            print(f"  시장수급[KOSDAQ]: 외인={fmt_amt(fn)}, 기관={fmt_amt(inn)}, 개인={fmt_amt(ivn)}")
        time.sleep(0.3)
    except Exception as e:
        print(f"  KOSDAQ 수급 실패: {e}")

    return {
        "foreign_net": sum(v.get("foreign_net",0) for v in result.values()),
        "inst_net":    sum(v.get("inst_net",0)    for v in result.values()),
        "indiv_net":   sum(v.get("indiv_net",0)   for v in result.values()),
        "by_market":   result,
    }

# ── 일봉 ───────────────────────────────────────────────
def fetch_ohlcv(code, token, count=60):
    today = datetime.date.today().strftime("%Y%m%d")
    try:
        rows = kis_get(
            "/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice",
            {"fid_cond_mrkt_div_code": "J", "fid_input_iscd": code,
             "fid_input_date_1": "19000101", "fid_input_date_2": today,
             "fid_period_div_code": "D", "fid_org_adj_prc": "0"},
            "FHKST03010100", token).get("output2", [])[:count]
        return [{"date": r.get("stck_bsop_date",""),
                 "open":   safe_int(r.get("stck_oprc",0)),
                 "high":   safe_int(r.get("stck_hgpr",0)),
                 "low":    safe_int(r.get("stck_lwpr",0)),
                 "close":  safe_int(r.get("stck_clpr",0)),
                 "volume": safe_int(r.get("acml_vol",0))}
                for r in reversed(rows) if safe_int(r.get("stck_clpr",0)) > 0]
    except:
        return []

# ── 종목별 수급 ─────────────────────────────────────────
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
        result = []
        for r in reversed(rows):
            f_amt  = safe_int(r.get("frgn_ntby_tr_pbmn",0))
            i_amt  = safe_int(r.get("orgn_ntby_tr_pbmn",0))
            iv_amt = safe_int(r.get("indv_ntby_tr_pbmn",0))
            f_qty  = safe_int(r.get("frgn_ntby_qty",0))
            i_qty  = safe_int(r.get("orgn_ntby_qty",0))
            iv_qty = safe_int(r.get("indv_ntby_qty",0))
            result.append({
                "date":        r.get("stck_bsop_date",""),
                "foreign_amt": f_amt, "inst_amt": i_amt, "indiv_amt": iv_amt,
                "foreign_qty": f_qty, "inst_qty": i_qty, "indiv_qty": iv_qty,
                "foreign": f_amt if f_amt != 0 else f_qty,
                "inst":    i_amt if i_amt != 0 else i_qty,
                "indiv":   iv_amt if iv_amt != 0 else iv_qty,
            })
        return result
    except:
        return []

# ── 기간별 수급 집계 ────────────────────────────────────
def summarize_supply(rows):
    if not rows: return {"day":{}, "week":{}, "month":{}}
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d", errors="coerce")
    df = df.dropna(subset=["date"])
    if df.empty: return {"day":{}, "week":{}, "month":{}}
    today = df["date"].max()
    def agg(sub):
        return {"foreign": int(sub["foreign"].sum()),
                "inst":    int(sub["inst"].sum()),
                "indiv":   int(sub["indiv"].sum())}
    return {
        "day":   agg(df[df["date"]==today]),
        "week":  agg(df[df["date"]>=today-pd.Timedelta(days=5)]),
        "month": agg(df[df["date"]>=today-pd.Timedelta(days=22)]),
    }

# ── Phase 신호 ─────────────────────────────────────────
def calc_phase(ohlcv, supply, mktcap):
    empty = {"phase":"","phase_key":"none","smp":0.0,"muges_ratio":1.0,
             "vol_ratio":1.0,"f_consec":0,"i_consec":0,"obv_above_ma":False}
    if not ohlcv or len(ohlcv) < 21: return empty
    try:
        df = pd.DataFrame(ohlcv)
        for c in ["close","volume","open","high","low"]:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
        df = df[df["close"]>0].reset_index(drop=True)
        if len(df)<21: return empty

        df["avg_p"]      = (df["high"]+df["low"]+df["close"])/3
        df["muges"]      = (df["avg_p"]*df["volume"]/(df["close"]*df["volume"].replace(0,np.nan))).fillna(1)
        df["muges_ma20"] = df["muges"].rolling(20).mean()
        obv = [0]
        for i in range(1, len(df)):
            p, c_, v = df["close"].iloc[i-1], df["close"].iloc[i], df["volume"].iloc[i]
            obv.append(obv[-1]+(v if c_>p else -v if c_<p else 0))
        df["obv"]       = obv
        df["obv_ma20"]  = pd.Series(obv).rolling(20).mean().values
        df["vol_ma20"]  = df["volume"].rolling(20).mean()
        df["vol_ratio"] = (df["volume"]/df["vol_ma20"].replace(0,np.nan)).fillna(1)

        f_consec=i_consec=0
        if supply:
            sup = pd.DataFrame(supply)
            sup["date"]=sup["date"].astype(str); df["date"]=df["date"].astype(str)
            df = df.merge(sup[["date","foreign","inst","foreign_amt","inst_amt"]], on="date", how="left")
            for col in ["foreign","inst","foreign_amt","inst_amt"]:
                df[col]=df[col].fillna(0)
            if mktcap>0:
                df["smp"]=(df["foreign_amt"]+df["inst_amt"]).rolling(10).sum()/(mktcap*1e8)*100
            else:
                df["smp"]=0.0
            def consec(s):
                c=0
                for v in reversed(s.dropna().tolist()):
                    if v>0: c+=1
                    else: break
                return c
            f_consec=consec(df["foreign"]); i_consec=consec(df["inst"])
        else:
            df["foreign"]=df["inst"]=df["smp"]=0.0

        t   = df.iloc[-1]
        smp = safe_float(t.get("smp",0))
        mm  = safe_float(t.get("muges_ma20",1)) or 1
        mr  = safe_float(t.get("muges",1))/mm
        vr  = safe_float(t.get("vol_ratio",1))
        obv_ma = safe_float(t["obv_ma20"]) if not pd.isna(t["obv_ma20"]) else 0
        obv_up = safe_float(t["obv"]) > obv_ma
        chg=0.0
        if len(df)>=2:
            p1,p2=safe_float(df.iloc[-2]["close"]),safe_float(t["close"])
            chg=(p2-p1)/p1*100 if p1>0 else 0
        ft=safe_float(t.get("foreign",0)); it_=safe_float(t.get("inst",0))

        if   smp>0 and f_consec>=3 and it_>0 and mr<0.8 and vr<1.5: ph,pk="⭐ GOLDEN","golden"
        elif vr>=2.0 and ft>0:                                         ph,pk="🟢 P2 거래량돌파","p2"
        elif f_consec>=5 and smp>0 and vr>=1.2:                       ph,pk="🟢 P2 수급가속","p2"
        elif ft>0 and it_>0 and vr>=1.3 and smp>0 and f_consec>=2:   ph,pk="🟢 P2 상승초기","p2"
        elif smp>0 and f_consec>=3 and it_>0:                         ph,pk="🔵 P1 수급복합","p1"
        elif mr<0.5 and smp>0 and ft>0:                               ph,pk="🔵 P1 조용매집","p1"
        elif obv_up and chg<=0:                                        ph,pk="🔵 P1 OBV매집","p1"
        elif mr>3.0 and ft<0:                                          ph,pk="🔴 P3 분산경고","p3"
        elif ft<0 and it_<0:                                           ph,pk="🔴 P3 손바뀜경고","p3"
        else:                                                           ph,pk="","none"

        return {"phase":ph,"phase_key":pk,"smp":round(smp,2),
                "muges_ratio":round(mr,2),"vol_ratio":round(vr,2),
                "f_consec":f_consec,"i_consec":i_consec,"obv_above_ma":bool(obv_up)}
    except Exception as e:
        print(f"    Phase 오류: {e}")
        return empty

# ── Top 거래주체 ────────────────────────────────────────
def calc_top_traders(stocks):
    out={}
    for actor, key in [("foreign","foreign_today"),("inst","inst_today"),("indiv","indiv_today")]:
        buying  = sorted([s for s in stocks if s.get(key,0)>0], key=lambda x:x.get(key,0), reverse=True)
        selling = sorted([s for s in stocks if s.get(key,0)<0], key=lambda x:x.get(key,0))
        out[actor]={
            "top_buy":  [{"name":s["name"],"market":s["market"],"price":s["price"],"amt":s[key]} for s in buying[:10]],
            "top_sell": [{"name":s["name"],"market":s["market"],"price":s["price"],"amt":s[key]} for s in selling[:10]],
        }
    return out

# ── 과거 데이터 누적 ────────────────────────────────────
def load_history():
    p = DATA_DIR/"history.json"
    return json.loads(p.read_text()) if p.exists() else {}

def save_history(hist):
    (DATA_DIR/"history.json").write_text(json.dumps(hist, ensure_ascii=False))

def append_history(hist, date_str, stocks, ms, indices):
    hist[date_str]={
        "stocks":{s["code"]:{
            "name":s["name"],"market":s["market"],
            "price":s["price"],"change":s["change"],
            "phase":s.get("phase",""),"phase_key":s.get("phase_key","none"),
            "nh_flag":s.get("nh_flag",""),
        } for s in stocks if s.get("price",0)>0},
        "market_supply":ms,"indices":indices,
    }
    for k in sorted(hist.keys())[:-60]: del hist[k]
    return hist

# ── 시장 요약 ───────────────────────────────────────────
def make_summary(indices, ms, stocks, ps):
    lines=[]
    kospi  = next((i for i in indices if i["name"]=="KOSPI"), None)
    kosdaq = next((i for i in indices if i["name"]=="KOSDAQ"),None)
    if kospi:
        kq=(f" | 코스닥 {kosdaq['value']:,.2f} ({'+' if kosdaq['change']>=0 else ''}{kosdaq['change']:.2f}%)" if kosdaq else "")
        lines.append(f"코스피 {kospi['value']:,.2f} ({'+' if kospi['change']>=0 else ''}{kospi['change']:.2f}%){kq}")
    fn,in_,iv=ms.get("foreign_net",0),ms.get("inst_net",0),ms.get("indiv_net",0)
    if fn!=0 or in_!=0 or iv!=0:
        lines.append(f"외국인 {fmt_amt(fn)} | 기관 {fmt_amt(in_)} | 개인 {fmt_amt(iv)}")
    for key,emoji,label in [("golden","⭐","GOLDEN"),("p2","🟢","P2 신호"),("p3","⚠️","P3 경고")]:
        if ps.get(key,0)>0:
            names=[s["name"] for s in stocks if s.get("phase_key")==key][:5]
            lines.append(f"{emoji} {label} {ps[key]}종목: {', '.join(names)}")
    nh=[s["name"] for s in stocks if "신고가" in s.get("nh_flag","")][:5]
    if nh: lines.append(f"🔥 52주 신고가: {', '.join(nh)}")
    return lines

# ── 메인 ───────────────────────────────────────────────
def main():
    now_kst   = datetime.datetime.utcnow()+datetime.timedelta(hours=9)
    today_str = now_kst.strftime("%Y-%m-%d")
    now_str   = now_kst.strftime("%Y-%m-%d %H:%M")
    print(f"\n{'='*55}\n📡 수집 시작: {now_str} KST\n{'='*55}")

    token=get_token(); print("✅ 토큰 OK")

    print("\n📊 지수 수집...")
    indices=fetch_indices(token)

    print("\n💰 시장 수급 수집...")
    market_supply=fetch_market_supply(token)
    time.sleep(0.3)

    print("\n🔍 전체 시장 스캔...")
    all_raw=[]
    print("  거래대금 상위 종목 조회...")
    all_raw.extend(fetch_top_volume_stocks(token,"J",100)); time.sleep(0.5)
    all_raw.extend(fetch_top_volume_stocks(token,"Q",100)); time.sleep(0.5)
    print("  신고가 근접 종목 조회...")
    all_raw.extend(fetch_near_high_stocks(token,"J",30));   time.sleep(0.5)
    all_raw.extend(fetch_near_high_stocks(token,"Q",30));   time.sleep(0.5)

    seen=set(); unique=[]
    for s in sorted(all_raw, key=lambda x:x.get("tr_val",0), reverse=True):
        if s.get("code") and s["code"] not in seen and s.get("price",0)>0:
            seen.add(s["code"]); unique.append(s)
    print(f"\n  → 총 {len(unique)}개 종목 대상 (상위 {MAX_STOCKS}개 상세분석)")

    stocks=[]
    print(f"\n📈 상세 분석 시작...")
    for i, stock in enumerate(unique[:MAX_STOCKS]):
        code=stock["code"]
        try:
            print(f"  [{i+1}/{min(len(unique),MAX_STOCKS)}] {stock['name']}({code}) ", end="", flush=True)
            ohlcv  = fetch_ohlcv(code, token, OHLCV_COUNT); time.sleep(0.25)
            supply = fetch_stock_supply(code, token, SUPPLY_DAYS); time.sleep(0.25)
            stock.update(calc_phase(ohlcv, supply, stock.get("mktcap",0)))

            p,h=stock["price"],stock.get("high52",0)
            r=p/h*100 if h>0 else 0
            stock["nh_flag"]  ="🔥52주신고가" if r>=99.5 else "📍신고가근접" if r>=97 else ""
            stock["nh_ratio"] =round(r,1)
            stock["supply_periods"]=summarize_supply(supply)
            td=supply[-1] if supply else {}
            stock["foreign_today"]=td.get("foreign",0)
            stock["inst_today"]   =td.get("inst",0)
            stock["indiv_today"]  =td.get("indiv",0)
            stocks.append(stock)
            print(f"→ {stock.get('phase') or '신호없음'} | {stock['nh_flag'] or '신고가아님'}")
        except Exception as e:
            print(f"\n  ⚠️ {code} 실패: {e}")
            stocks.append(stock)

    top_traders=calc_top_traders(stocks)
    ps={"golden":sum(1 for s in stocks if s.get("phase_key")=="golden"),
        "p1":    sum(1 for s in stocks if s.get("phase_key")=="p1"),
        "p2":    sum(1 for s in stocks if s.get("phase_key")=="p2"),
        "p3":    sum(1 for s in stocks if s.get("phase_key")=="p3"),
        "new_high":sum(1 for s in stocks if "신고가" in s.get("nh_flag","")),
        "total": len(stocks)}

    hist=load_history()
    hist=append_history(hist, today_str, stocks, market_supply, indices)
    save_history(hist)

    payload=clean_nan({
        "updated_at":today_str and now_str,
        "date":today_str,
        "is_market_open":9*60+5<=now_kst.hour*60+now_kst.minute<=15*60+30,
        "indices":indices,"market_supply":market_supply,
        "stocks":stocks,"top_traders":top_traders,
        "phase_stats":ps,
        "summary_lines":make_summary(indices,market_supply,stocks,ps),
        "available_dates":sorted(hist.keys(),reverse=True)[:30],
    })
    (DATA_DIR/"market.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2))
    print(f"\n{'='*55}\n✅ 완료!")
    print(f"   지수 {len(indices)}개 | 종목 {len(stocks)}개")
    print(f"   GOLDEN {ps['golden']} | P1 {ps['p1']} | P2 {ps['p2']} | P3 {ps['p3']} | 신고가 {ps['new_high']}")
    if not indices: print("   ⚠️ 지수 0개 — 장마감/주말이거나 API 키 권한 확인 필요")

if __name__=="__main__":
    main()
