#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_market.py v6 — KIS API 스펙 완전 정확 버전
=================================================
확인된 API 스펙:
  지수:     FHPUP02100000  fid_cond_mrkt_div_code="U"  FID_INPUT_ISCD=0001/1001/2001
  현재가:   FHKST01010100  fid_cond_mrkt_div_code="J"  FID_INPUT_ISCD=종목코드
  일봉:     FHKST03010100  FID_PERIOD_DIV_CODE="D"  → output2 배열
  투자자:   FHKST01010900  fid_cond_mrkt_div_code="J"  FID_INPUT_ISCD=종목코드
  거래량순위: FHPST01710000  fid_cond_mrkt_div_code="J" (KOSPI만, KOSDAQ 안됨)
"""
import os, json, time, math, datetime
import requests
import pandas as pd
import numpy as np

BASE_URL   = "https://openapi.koreainvestment.com:9443"
APP_KEY    = os.environ.get("KIS_APP_KEY", "")
APP_SECRET = os.environ.get("KIS_APP_SECRET", "")
TOKEN_FILE = "/tmp/kis_token_cache.json"
KST = datetime.timezone(datetime.timedelta(hours=9))

# ── KOSDAQ 폴백 (거래량순위 API KOSDAQ 미지원) ─────────────────────────
KOSDAQ_FALLBACK = [
    ("263750","펄어비스"), ("041510","에스엠"), ("035900","JYP Ent."),
    ("122870","와이지엔터"), ("251270","넷마블"), ("293490","카카오게임즈"),
    ("357780","솔브레인"), ("036570","엔씨소프트"), ("112040","위메이드"),
    ("086520","에코프로"), ("247540","에코프로비엠"), ("352820","하이브"),
    ("079550","LIG넥스원"), ("196170","알테오젠"), ("101490","에스앤에스텍"),
    ("006280","녹십자"), ("039030","이오테크닉스"), ("095340","ISC"),
    ("041960","블루오션"), ("166090","하나머티리얼즈"),
]

KOSPI_FALLBACK = [
    ("005930","삼성전자"), ("000660","SK하이닉스"), ("207940","삼성바이오로직스"),
    ("005380","현대차"), ("000270","기아"), ("068270","셀트리온"),
    ("105560","KB금융"), ("055550","신한지주"), ("086790","하나금융지주"),
    ("028260","삼성물산"), ("012330","현대모비스"), ("066570","LG전자"),
    ("003550","LG"), ("017670","SK텔레콤"), ("030200","KT"),
    ("015760","한국전력"), ("032830","삼성생명"), ("009150","삼성전기"),
    ("034730","SK"), ("096770","SK이노베이션"),
]

# ── 유틸 ──────────────────────────────────────────────────────────────
def safe_int(v, d=0):
    try: return int(str(v).replace(",","").strip() or 0)
    except: return d

def safe_float(v, d=0.0):
    try:
        f = float(str(v).replace(",","").strip())
        return d if (math.isnan(f) or math.isinf(f)) else f
    except: return d

def clean_nan(obj):
    if isinstance(obj, dict):  return {k: clean_nan(v) for k,v in obj.items()}
    if isinstance(obj, list):  return [clean_nan(v) for v in obj]
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)): return 0.0
    return obj

def today_str():
    return datetime.datetime.now(KST).strftime("%Y%m%d")

def ndays_ago(n):
    return (datetime.datetime.now(KST) - datetime.timedelta(days=n)).strftime("%Y%m%d")

# ── 인증 ──────────────────────────────────────────────────────────────
def get_token():
    now = datetime.datetime.now(KST).timestamp()
    if os.path.exists(TOKEN_FILE):
        try:
            c = json.load(open(TOKEN_FILE))
            if "exp" in c and c["exp"] > now + 60:
                return c["token"]
        except: pass
    r = requests.post(f"{BASE_URL}/oauth2/tokenP", json={
        "grant_type": "client_credentials",
        "appkey": APP_KEY, "appsecret": APP_SECRET,
    }, timeout=10)
    r.raise_for_status()
    data = r.json()
    token = data["access_token"]
    try:
        exp_str = data.get("access_token_token_expired","")
        exp_ts = datetime.datetime.strptime(exp_str,"%Y-%m-%d %H:%M:%S").replace(tzinfo=KST).timestamp()
    except:
        exp_ts = now + 82800
    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    json.dump({"token": token, "exp": exp_ts}, open(TOKEN_FILE,"w"))
    return token

def kis_get(path, params, tr_id, token):
    r = requests.get(
        BASE_URL + path,
        headers={
            "content-type": "application/json; charset=utf-8",
            "authorization": f"Bearer {token}",
            "appkey": APP_KEY, "appsecret": APP_SECRET,
            "tr_id": tr_id, "custtype": "P",
        },
        params=params, timeout=10
    )
    r.raise_for_status()
    data = r.json()
    if data.get("rt_cd","") != "0":
        raise Exception(f"KIS 오류: {data.get('msg1','').strip()} [{tr_id}]")
    return data

# ── 1. 지수 ── FHPUP02100000 ──────────────────────────────────────────
# fid_cond_mrkt_div_code = "U" (업종/지수 전용, J 사용하면 에러!)
# FID_INPUT_ISCD: 0001=KOSPI, 1001=KOSDAQ, 2001=KOSPI200
def fetch_indices(token):
    INDEX_CODES = [("0001","KOSPI"), ("1001","KOSDAQ"), ("2001","KSP200")]
    results = []
    for iscd, name in INDEX_CODES:
        try:
            d = kis_get(
                "/uapi/domestic-stock/v1/quotations/inquire-index-price",
                {"fid_cond_mrkt_div_code": "U", "FID_INPUT_ISCD": iscd},
                "FHPUP02100000", token
            )
            o = d.get("output", {})
            val  = safe_float(o.get("bstp_nmix_prpr", 0))
            diff = safe_float(o.get("bstp_nmix_prdy_vrss", 0))
            chg  = safe_float(o.get("bstp_nmix_prdy_ctrt", 0))
            sign = o.get("prdy_vrss_sign", "3")
            if sign in ("4","5"): diff = -abs(diff); chg = -abs(chg)
            results.append({
                "name": name, "iscd": iscd,
                "value": val, "diff": diff, "change": chg,
                "vol": safe_int(o.get("acml_vol",0)),
                "tr_amt": safe_int(o.get("acml_tr_pbmn",0)),
                "ascn": safe_int(o.get("ascn_issu_cnt",0)),
                "down": safe_int(o.get("down_issu_cnt",0)),
                "vol_fmt": f"{safe_int(o.get('acml_vol',0))/1e6:.0f}백만주",
            })
            print(f"  [{name}] {val:,.2f} ({chg:+.2f}%)")
            time.sleep(0.3)
        except Exception as e:
            print(f"  지수 실패({name}): {e}")
    return results

# ── 2. 거래량 순위 ── FHPST01710000 ────────────────────────────────────
# KOSPI(J)만 지원. KOSDAQ(Q) → ERROR INVALID fid_cond_mrkt_div_code
def fetch_top_volume_stocks(token, market="J", top_n=50):
    if market != "J":
        return _fetch_fallback(token, KOSDAQ_FALLBACK, "KOSDAQ")
    stocks = []
    try:
        d = kis_get(
            "/uapi/domestic-stock/v1/quotations/volume-rank",
            {
                "fid_cond_mrkt_div_code": "J",
                "FID_COND_SCR_DIV_CODE":  "20171",
                "FID_INPUT_ISCD":         "0000",
                "FID_DIV_CLS_CODE":       "0",
                "FID_BLNG_CLS_CODE":      "0",
                "FID_TRGT_CLS_CODE":      "111111111",
                "FID_TRGT_EXLS_CLS_CODE": "000000",
                "FID_INPUT_PRICE_1": "", "FID_INPUT_PRICE_2": "",
                "FID_VOL_CNT": "", "FID_INPUT_DATE_1": "",
            },
            "FHPST01710000", token
        )
        for r in (d.get("output",[]))[:top_n]:
            code  = r.get("mksc_shrn_iscd","").strip()
            price = safe_int(r.get("stck_prpr",0))
            if not code or not price: continue
            sign = r.get("prdy_vrss_sign","3")
            diff = safe_int(r.get("prdy_vrss",0))
            chg  = safe_float(r.get("prdy_ctrt",0))
            if sign in ("4","5"): diff=-abs(diff); chg=-abs(chg)
            stocks.append({
                "code": code, "name": r.get("hts_kor_isnm","").strip(),
                "market": "KOSPI", "price": price, "change": chg, "diff": diff,
                "volume": safe_int(r.get("acml_vol",0)),
                "tr_val": safe_int(r.get("acml_tr_pbmn",0)),
                "high52": safe_int(r.get("w52_hgpr",0)),
                "low52":  safe_int(r.get("w52_lwpr",0)),
                "mktcap": safe_int(r.get("hts_avls",0)),
                "sector": r.get("bstp_kor_isnm","").strip(),
            })
        print(f"  [KOSPI] 거래대금 상위 {len(stocks)}개")
        time.sleep(0.5)
    except Exception as e:
        print(f"  거래량 순위 실패: {e}")
        stocks = _fetch_fallback(token, KOSPI_FALLBACK, "KOSPI")
    return stocks

def _fetch_fallback(token, fallback_list, label):
    """폴백: 고정 리스트로 현재가 개별 조회"""
    stocks = []
    for code, name in fallback_list[:20]:
        try:
            d = kis_get(
                "/uapi/domestic-stock/v1/quotations/inquire-price",
                {"fid_cond_mrkt_div_code": "J", "FID_INPUT_ISCD": code},
                "FHKST01010100", token
            )
            o = d.get("output", {})
            price = safe_int(o.get("stck_prpr",0))
            if not price: continue
            sign = o.get("prdy_vrss_sign","3")
            diff = safe_int(o.get("prdy_vrss",0))
            chg  = safe_float(o.get("prdy_ctrt",0))
            if sign in ("4","5"): diff=-abs(diff); chg=-abs(chg)
            stocks.append({
                "code": code, "name": o.get("hts_kor_isnm",name).strip() or name,
                "market": label, "price": price, "change": chg, "diff": diff,
                "volume": safe_int(o.get("acml_vol",0)),
                "tr_val": safe_int(o.get("acml_tr_pbmn",0)),
                "high52": safe_int(o.get("w52_hgpr",0)),
                "low52":  safe_int(o.get("w52_lwpr",0)),
                "mktcap": safe_int(o.get("hts_avls",0)),
                "sector": o.get("bstp_kor_isnm","").strip(),
            })
            time.sleep(0.12)
        except Exception as e:
            print(f"    {name} 실패: {e}")
    print(f"  [{label}] 폴백 {len(stocks)}개")
    return stocks

# ── 3. 일봉 ── FHKST03010100 ──────────────────────────────────────────
# output2 배열 사용 (output1은 당일 1건만)
def fetch_ohlcv(code, token, days=60):
    try:
        d = kis_get(
            "/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice",
            {
                "fid_cond_mrkt_div_code": "J",
                "FID_INPUT_ISCD":         code,
                "FID_INPUT_DATE_1":       ndays_ago(days + 30),
                "FID_INPUT_DATE_2":       today_str(),
                "FID_PERIOD_DIV_CODE":    "D",
                "FID_ORG_ADJ_PRC":        "0",
            },
            "FHKST03010100", token
        )
        rows = d.get("output2", [])
        if not rows: return pd.DataFrame()
        df = pd.DataFrame(rows).rename(columns={
            "stck_bsop_date":"date","stck_clpr":"close","stck_oprc":"open",
            "stck_hgpr":"high","stck_lwpr":"low","acml_vol":"volume","acml_tr_pbmn":"tr_val",
        })
        for c in ["close","open","high","low","volume","tr_val"]:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c].astype(str).str.replace(",",""), errors="coerce").fillna(0)
        return df.sort_values("date").tail(days).reset_index(drop=True)
    except:
        return pd.DataFrame()

# ── 4. 투자자 ── FHKST01010900 ────────────────────────────────────────
# output 배열 최근 30일, frgn_ntby_tr_pbmn=외인순매수대금(백만원단위)
def fetch_stock_supply(code, token):
    try:
        d = kis_get(
            "/uapi/domestic-stock/v1/quotations/inquire-investor",
            {"fid_cond_mrkt_div_code": "J", "FID_INPUT_ISCD": code},
            "FHKST01010900", token
        )
        rows = d.get("output", [])
        if not rows: return pd.DataFrame()
        df = pd.DataFrame(rows).rename(columns={
            "stck_bsop_date":"date",
            "frgn_ntby_qty":"frgn_qty", "orgn_ntby_qty":"orgn_qty", "prsn_ntby_qty":"prsn_qty",
            "frgn_ntby_tr_pbmn":"frgn_amt", "orgn_ntby_tr_pbmn":"orgn_amt", "prsn_ntby_tr_pbmn":"prsn_amt",
        })
        for c in ["frgn_qty","orgn_qty","prsn_qty","frgn_amt","orgn_amt","prsn_amt"]:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c].astype(str).str.replace(",",""), errors="coerce").fillna(0)
        return df.sort_values("date").reset_index(drop=True)
    except:
        return pd.DataFrame()

# ── 5. Phase 계산 ────────────────────────────────────────────────────
def calc_consec(supply, col):
    if supply.empty or col not in supply.columns: return 0
    cnt = 0
    for v in supply[col].values[::-1]:
        if v > 0: cnt += 1
        else: break
    return cnt

def calc_phase(ohlcv, supply):
    result = {"phase":"","phase_key":"","muges_ratio":1.0,"smp":0.0,
              "vol_ratio":1.0,"obv_above_ma":False,
              "f_consec":0,"i_consec":0,
              "foreign_today":0,"inst_today":0,"indiv_today":0}
    if ohlcv.empty or len(ohlcv) < 10: return result
    df = ohlcv.copy()
    df["ma5"]  = df["close"].rolling(5).mean()
    df["ma20"] = df["close"].rolling(20).mean()
    df["ma60"] = df["close"].rolling(min(60,len(df))).mean()
    df["dir"]  = np.sign(df["close"].diff().fillna(0))
    df["obv"]  = (df["dir"] * df["volume"]).cumsum()
    df["obv_ma20"] = df["obv"].rolling(20).mean()
    t = df.iloc[-1]
    vol_ma = df["volume"].rolling(20).mean().iloc[-1] or 1
    result["vol_ratio"] = round(t["volume"] / vol_ma, 2)
    result["obv_above_ma"] = bool(t["obv"] > safe_float(t.get("obv_ma20",0)))

    if not supply.empty:
        result["f_consec"] = calc_consec(supply, "frgn_qty")
        result["i_consec"] = calc_consec(supply, "orgn_qty")
        last = supply.iloc[-1]
        # frgn_amt는 천원 단위 → 원 단위 변환
        result["foreign_today"] = int(safe_float(last.get("frgn_amt",0)) * 1_000_000)
        result["inst_today"]    = int(safe_float(last.get("orgn_amt",0)) * 1_000_000)
        result["indiv_today"]   = int(safe_float(last.get("prsn_amt",0)) * 1_000_000)
        smp5 = (supply.tail(5)["frgn_amt"].sum() + supply.tail(5)["orgn_amt"].sum())
        tr5  = df.tail(5)["tr_val"].sum() / 1000 or 1
        result["smp"] = round(smp5 / tr5 * 100, 2)

    fc, ic = result["f_consec"], result["i_consec"]
    vr, smp = result["vol_ratio"], result["smp"]
    obv_up = result["obv_above_ma"]
    ma5, ma20, ma60 = safe_float(t.get("ma5",0)), safe_float(t.get("ma20",0)), safe_float(t.get("ma60",0))

    if fc >= 10 and ic >= 5 and obv_up and smp > 2 and ma5 > ma20 > ma60:
        result.update({"phase":"⭐ GOLDEN 강한매집","phase_key":"golden"})
    elif (fc >= 3 or ic >= 3) and obv_up and smp > 0 and ma5 >= ma20:
        ph = "🟢 P2 거래량돌파" if vr >= 2.0 else ("🟢 P2 수급가속" if smp > 1 else "🟢 P2 상승추세")
        result.update({"phase":ph,"phase_key":"p2"})
    elif (fc >= 2 or ic >= 2) and obv_up:
        result.update({"phase":"🔵 P1 OBV매집","phase_key":"p1"})
    elif fc < 0 and ic < 0 and smp < -2:
        result.update({"phase":"🔴 P3 손바뀜경고","phase_key":"p3"})
    return result

def calc_supply_summary(supply):
    if supply.empty: return {"day":{},"week":{},"month":{}}
    def sums(n):
        t = supply.tail(n)
        return {
            "foreign": int(t["frgn_amt"].sum() * 1_000_000),
            "inst":    int(t["orgn_amt"].sum() * 1_000_000),
            "indiv":   int(t["prsn_amt"].sum() * 1_000_000),
        }
    return {"day":sums(1), "week":sums(5), "month":sums(22)}

def calc_nh(s):
    price, h52 = s.get("price",0), s.get("high52",0)
    if not price or not h52: return "", 0
    r = round(price / h52 * 100, 1)
    if r >= 100:  return "📍 52주 신고가!", r
    if r >= 97:   return "📍 신고가 근접", r
    return "", r

# ── 요약 문장 ─────────────────────────────────────────────────────────
def make_summary(indices, stocks, ms, ps):
    def fmt_b(n):
        s = "+" if n>=0 else "-"; a = abs(n)
        if a>=1e8: return f"{s}{a/1e8:.0f}억"
        return f"{s}{a/1e4:.0f}만"
    lines = []
    for idx in indices[:2]:
        sign = "▲" if idx["change"]>=0 else "▼"
        lines.append(f"📊 {idx['name']} {idx['value']:,.2f} ({sign}{abs(idx['change']):.2f}%) · 상승{idx.get('ascn',0)} 하락{idx.get('down',0)}")
    fn, inst, indiv = ms.get("foreign_net",0), ms.get("inst_net",0), ms.get("indiv_net",0)
    if any([fn,inst,indiv]):
        lines.append(f"💰 외국인 {fmt_b(fn)} · 기관 {fmt_b(inst)} · 개인 {fmt_b(indiv)}")
    parts = []
    if ps.get("golden"): parts.append(f"⭐GOLDEN {ps['golden']}개")
    if ps.get("p2"):     parts.append(f"🟢P2 {ps['p2']}개")
    if ps.get("p1"):     parts.append(f"🔵P1매집 {ps['p1']}개")
    if ps.get("p3"):     parts.append(f"🔴P3경고 {ps['p3']}개")
    if ps.get("new_high"): parts.append(f"🚀신고가 {ps['new_high']}개")
    if parts: lines.append("📡 신호: " + " · ".join(parts))
    top5 = sorted(stocks, key=lambda s:abs(s.get("tr_val",0)), reverse=True)[:5]
    if top5:
        lines.append("🔥 거래대금 상위: " + ", ".join(
            f"{s['name']}({'+' if s['change']>=0 else ''}{s['change']:.1f}%)" for s in top5))
    return lines

# ── 메인 ─────────────────────────────────────────────────────────────
def main():
    now = datetime.datetime.now(KST)
    print("=" * 55)
    print(f"📡 수집 시작: {now.strftime('%Y-%m-%d %H:%M')} KST")
    print("=" * 55)
    token = get_token()
    print("✅ 토큰 OK")

    print("\n📊 지수 수집...")
    indices = fetch_indices(token)

    print("\n🔍 전체 시장 스캔...")
    kospi  = fetch_top_volume_stocks(token, "J", 50)
    kosdaq = fetch_top_volume_stocks(token, "Q", 20)

    seen, unique = set(), []
    for s in sorted(kospi + kosdaq, key=lambda x: x.get("tr_val",0), reverse=True):
        if s["code"] not in seen and s["price"] > 0:
            seen.add(s["code"]); unique.append(s)
    print(f"\n  → 총 {len(unique)}개 종목 (상위 50개 상세분석)")

    print("\n📈 상세 분석...")
    stocks = []
    for i, s in enumerate(unique[:50]):
        code, name = s["code"], s["name"]
        try:
            ohlcv  = fetch_ohlcv(code, token, 60); time.sleep(0.1)
            supply = fetch_stock_supply(code, token); time.sleep(0.1)
            s.update(calc_phase(ohlcv, supply))
            s["supply_periods"] = calc_supply_summary(supply)
            nh_flag, nh_ratio = calc_nh(s)
            s["nh_flag"] = nh_flag; s["nh_ratio"] = nh_ratio
            print(f"  [{i+1:2d}/50] {name} → {s.get('phase','') or '신호없음'} {nh_flag}")
        except Exception as e:
            print(f"  [{i+1}] {name} 실패: {e}")
        stocks.append(s)

    ps = {
        "golden": sum(1 for s in stocks if s.get("phase_key")=="golden"),
        "p2":     sum(1 for s in stocks if s.get("phase_key")=="p2"),
        "p1":     sum(1 for s in stocks if s.get("phase_key")=="p1"),
        "p3":     sum(1 for s in stocks if s.get("phase_key")=="p3"),
        "new_high": sum(1 for s in stocks if s.get("nh_flag")),
    }
    ms = {
        "foreign_net": sum(s.get("foreign_today",0) for s in stocks),
        "inst_net":    sum(s.get("inst_today",0) for s in stocks),
        "indiv_net":   sum(s.get("indiv_today",0) for s in stocks),
    }
    summary = make_summary(indices, stocks, ms, ps)

    payload = clean_nan({
        "date": now.strftime("%Y-%m-%d"),
        "updated_at": now.strftime("%Y-%m-%d %H:%M"),
        "indices": indices,
        "market_supply": ms,
        "stocks": stocks,
        "phase_stats": ps,
        "summary_lines": summary,
    })
    os.makedirs("data", exist_ok=True)
    with open("data/market.json","w",encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 완료! 지수{len(indices)} | 종목{len(stocks)} | GOLDEN{ps['golden']} P2{ps['p2']} P1{ps['p1']} P3{ps['p3']} 신고가{ps['new_high']}")

if __name__ == "__main__":
    main()
