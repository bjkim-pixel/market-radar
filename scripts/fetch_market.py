"""
KIS API 데이터 수집 + Phase 신호 계산 스크립트
GitHub Actions에서 자동 실행됩니다.
"""
import os, json, time, requests, datetime
import pandas as pd
import numpy as np
from pathlib import Path

# ─── 설정 ────────────────────────────────────────────────
APP_KEY    = os.environ["KIS_APP_KEY"]
APP_SECRET = os.environ["KIS_APP_SECRET"]
ACCOUNT_NO = os.environ["KIS_ACCOUNT_NO"]   # 예: "12345678-01"
BASE_URL   = "https://openapi.koreainvestment.com:9443"

# 관심 종목 코드 목록 (원하는 종목 추가/수정)
WATCH_LIST = [
    "005930",  # 삼성전자
    "000660",  # SK하이닉스
    "005380",  # 현대차
    "042700",  # 한미반도체
    "373220",  # LG에너지솔루션
    "035420",  # NAVER
    "035720",  # 카카오
    "003670",  # 포스코퓨처엠
    "012450",  # 한화에어로스페이스
    "178320",  # 서진시스템
]

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# ─── KIS API 토큰 발급 ───────────────────────────────────
def get_access_token():
    """OAuth 토큰 발급 (1일 유효)"""
    # 캐시된 토큰이 있으면 재사용
    token_file = DATA_DIR / "token_cache.json"
    if token_file.exists():
        cache = json.loads(token_file.read_text())
        expire = datetime.datetime.fromisoformat(cache["expires_at"])
        if datetime.datetime.now() < expire - datetime.timedelta(minutes=10):
            return cache["access_token"]

    resp = requests.post(
        f"{BASE_URL}/oauth2/tokenP",
        json={
            "grant_type": "client_credentials",
            "appkey":     APP_KEY,
            "appsecret":  APP_SECRET,
        },
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    token = data["access_token"]

    # 캐시 저장
    expires_at = datetime.datetime.now() + datetime.timedelta(hours=23)
    token_file.write_text(json.dumps({
        "access_token": token,
        "expires_at":   expires_at.isoformat(),
    }))
    return token


def kis_get(path, params, tr_id, token):
    """KIS REST API GET 헬퍼"""
    headers = {
        "authorization": f"Bearer {token}",
        "appkey":        APP_KEY,
        "appsecret":     APP_SECRET,
        "tr_id":         tr_id,
        "custtype":      "P",
    }
    resp = requests.get(
        f"{BASE_URL}{path}",
        headers=headers,
        params=params,
        timeout=10,
    )
    resp.raise_for_status()
    result = resp.json()
    if result.get("rt_cd") != "0":
        raise RuntimeError(f"KIS API 오류: {result.get('msg1')}")
    return result


# ─── 지수 조회 ────────────────────────────────────────────
def fetch_indices(token):
    """코스피·코스닥·코스피200 현재가 조회"""
    indices = []
    configs = [
        ("0001", "KOSPI",   "FHPUP02100000"),
        ("1001", "KOSDAQ",  "FHPUP02100000"),
        ("2001", "KSP200",  "FHPUP02100000"),
    ]
    for code, name, tr_id in configs:
        try:
            r = kis_get(
                "/uapi/domestic-stock/v1/quotations/inquire-index-price",
                {"iscd": code},
                tr_id,
                token,
            )
            o = r["output"]
            indices.append({
                "name":  name,
                "value": float(o.get("bstp_nmix_prpr", 0)),
                "change": float(o.get("bstp_nmix_prdy_ctrt", 0)),
                "diff":  float(o.get("bstp_nmix_prdy_vrss", 0)),
                "vol":   o.get("acml_tr_pbmn", "0"),
            })
            time.sleep(0.2)
        except Exception as e:
            print(f"⚠️ 지수 조회 실패 ({name}): {e}")
    return indices


# ─── 종목 현재가 ──────────────────────────────────────────
def fetch_stock_price(code, token):
    """종목 현재가·등락률·거래량 조회"""
    r = kis_get(
        "/uapi/domestic-stock/v1/quotations/inquire-price",
        {"fid_cond_mrkt_div_code": "J", "fid_input_iscd": code},
        "FHKST01010100",
        token,
    )
    o = r["output"]
    return {
        "code":   code,
        "name":   o.get("hts_kor_isnm", code),
        "price":  int(o.get("stck_prpr", 0)),
        "change": float(o.get("prdy_ctrt", 0)),        # 등락률%
        "diff":   int(o.get("prdy_vrss", 0)),           # 전일대비
        "volume": int(o.get("acml_vol", 0)),            # 누적거래량
        "vol_ratio": float(o.get("vol_tnrt", 0)),       # 거래량 회전율
        "high52": int(o.get("w52_hgpr", 0)),            # 52주 고가
        "low52":  int(o.get("w52_lwpr", 0)),            # 52주 저가
        "mktcap": int(o.get("hts_avls", 0)),            # 시가총액(억)
    }


# ─── 일봉 데이터 ─────────────────────────────────────────
def fetch_daily_ohlcv(code, token, count=60):
    """일봉 데이터 조회 (최근 count일)"""
    today = datetime.date.today().strftime("%Y%m%d")
    r = kis_get(
        "/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice",
        {
            "fid_cond_mrkt_div_code": "J",
            "fid_input_iscd":         code,
            "fid_input_date_1":       "19000101",
            "fid_input_date_2":       today,
            "fid_period_div_code":    "D",
            "fid_org_adj_prc":        "0",
        },
        "FHKST03010100",
        token,
    )
    rows = r.get("output2", [])[:count]
    records = []
    for row in reversed(rows):  # 오래된 순으로
        records.append({
            "date":   row.get("stck_bsop_date", ""),
            "open":   int(row.get("stck_oprc", 0)),
            "high":   int(row.get("stck_hgpr", 0)),
            "low":    int(row.get("stck_lwpr", 0)),
            "close":  int(row.get("stck_clpr", 0)),
            "volume": int(row.get("acml_vol", 0)),
        })
    return records


# ─── 수급 데이터 (외인·기관) ─────────────────────────────
def fetch_supply(code, token):
    """외인·기관 순매수 조회"""
    today = datetime.date.today().strftime("%Y%m%d")
    past  = (datetime.date.today() - datetime.timedelta(days=30)).strftime("%Y%m%d")
    try:
        r = kis_get(
            "/uapi/domestic-stock/v1/quotations/inquire-investor",
            {
                "fid_cond_mrkt_div_code": "J",
                "fid_input_iscd":         code,
                "fid_input_date_1":       past,
                "fid_input_date_2":       today,
                "fid_period_div_code":    "D",
            },
            "FHKST01010900",
            token,
        )
        rows = r.get("output", [])
        records = []
        for row in reversed(rows):
            records.append({
                "date":      row.get("stck_bsop_date", ""),
                "foreign":   int(row.get("frgn_ntby_qty", 0)),   # 외인 순매수량
                "inst":      int(row.get("orgn_ntby_qty", 0)),    # 기관 순매수량
                "individual":int(row.get("indv_ntby_qty", 0)),    # 개인 순매수량
                "foreign_amt": int(row.get("frgn_ntby_tr_pbmn", 0)),  # 외인 순매수 금액
                "inst_amt":    int(row.get("orgn_ntby_tr_pbmn", 0)),   # 기관 순매수 금액
            })
        return records
    except Exception as e:
        print(f"  ⚠️ 수급 조회 실패 ({code}): {e}")
        return []


# ─── 시장 전체 수급 ───────────────────────────────────────
def fetch_market_supply(token):
    """코스피 투자자별 매매 현황"""
    try:
        r = kis_get(
            "/uapi/domestic-stock/v1/quotations/inquire-investor",
            {
                "fid_cond_mrkt_div_code": "J",
                "fid_input_iscd":         "0001",
                "fid_input_date_1":       datetime.date.today().strftime("%Y%m%d"),
                "fid_input_date_2":       datetime.date.today().strftime("%Y%m%d"),
                "fid_period_div_code":    "D",
            },
            "FHKST01010900",
            token,
        )
        rows = r.get("output", [])
        if not rows:
            return {}
        row = rows[0]
        return {
            "foreign_net": int(row.get("frgn_ntby_tr_pbmn", 0)),
            "inst_net":    int(row.get("orgn_ntby_tr_pbmn", 0)),
            "indiv_net":   int(row.get("indv_ntby_tr_pbmn", 0)),
        }
    except Exception as e:
        print(f"  ⚠️ 시장 수급 조회 실패: {e}")
        return {}


# ─── Phase 신호 계산 ─────────────────────────────────────
def calc_phase_signals(ohlcv_list, supply_list, mktcap):
    """
    OBV, SMP, 무게수, 연속 순매수 기반 Phase 신호 계산
    Returns: dict with signal flags
    """
    if not ohlcv_list or len(ohlcv_list) < 21:
        return {"phase": "", "detail": "데이터 부족"}

    df = pd.DataFrame(ohlcv_list)
    df["close"]  = pd.to_numeric(df["close"])
    df["volume"] = pd.to_numeric(df["volume"])
    df["open"]   = pd.to_numeric(df["open"])
    df["high"]   = pd.to_numeric(df["high"])

    # 무게수 = 거래대금 / (종가 × 거래량)
    # 거래대금을 직접 못 가져오므로 (고가+저가+종가)/3 × 거래량 근사
    df["avg_price"] = (df["high"] + pd.to_numeric(df["low"]) + df["close"]) / 3
    df["tr_val"]    = df["avg_price"] * df["volume"]
    df["muges"]     = df["tr_val"] / (df["close"] * df["volume"].replace(0, np.nan))
    df["muges_ma20"] = df["muges"].rolling(20).mean()

    # OBV
    obv = [0]
    for i in range(1, len(df)):
        if df["close"].iloc[i] > df["close"].iloc[i - 1]:
            obv.append(obv[-1] + df["volume"].iloc[i])
        elif df["close"].iloc[i] < df["close"].iloc[i - 1]:
            obv.append(obv[-1] - df["volume"].iloc[i])
        else:
            obv.append(obv[-1])
    df["obv"]      = obv
    df["obv_ma20"] = df["obv"].rolling(20).mean()

    # 거래량 MA20 & 배수
    df["vol_ma20"]  = df["volume"].rolling(20).mean()
    df["vol_ratio"] = df["volume"] / df["vol_ma20"].replace(0, np.nan)

    # 수급 데이터 병합
    if supply_list:
        sup = pd.DataFrame(supply_list)
        sup["date"] = sup["date"].astype(str)
        df["date"]  = df["date"].astype(str)
        df = df.merge(sup[["date", "foreign", "inst", "individual", "foreign_amt", "inst_amt"]],
                      on="date", how="left")
        df[["foreign", "inst", "individual", "foreign_amt", "inst_amt"]] = \
            df[["foreign", "inst", "individual", "foreign_amt", "inst_amt"]].fillna(0)

        # SMP = 10일 외인+기관 순매수 금액합 / 시가총액 × 100
        if mktcap > 0:
            df["smp"] = (
                (df["foreign_amt"] + df["inst_amt"]).rolling(10).sum()
                / (mktcap * 1e8) * 100
            )
        else:
            df["smp"] = 0.0

        # 외인·기관 연속 순매수 계산
        def count_consec(series):
            """마지막 날부터 몇 일 연속인지"""
            vals = series.tolist()
            cnt = 0
            for v in reversed(vals):
                if v > 0:
                    cnt += 1
                else:
                    break
            return cnt

        f_consec = count_consec(df["foreign"].dropna())
        i_consec = count_consec(df["inst"].dropna())
    else:
        df["foreign"] = 0
        df["inst"]    = 0
        df["smp"]     = 0.0
        f_consec = 0
        i_consec = 0

    # 오늘 (마지막 행) 기준으로 신호 판단
    today = df.iloc[-1]

    smp       = float(today.get("smp", 0) or 0)
    muges     = float(today.get("muges", 1) or 1)
    muges_avg = float(today.get("muges_ma20", 1) or 1)
    muges_r   = muges / muges_avg if muges_avg > 0 else 1
    obv_val   = float(today["obv"])
    obv_ma    = float(today["obv_ma20"]) if not pd.isna(today["obv_ma20"]) else 0
    vol_r     = float(today["vol_ratio"]) if not pd.isna(today["vol_ratio"]) else 1
    chg_r     = float(today["close"] - df.iloc[-2]["close"]) / float(df.iloc[-2]["close"]) * 100 \
                if len(df) >= 2 else 0
    f_today   = float(today.get("foreign", 0) or 0)
    i_today   = float(today.get("inst", 0) or 0)

    # ── GOLDEN ─────────────────────────────────────────
    golden = (
        smp > 0 and
        f_consec >= 3 and
        i_today > 0 and
        muges_r < 0.8 and
        vol_r < 1.5
    )

    # ── P1 신호 ────────────────────────────────────────
    p1_obv    = obv_val > obv_ma and chg_r <= 0
    p1_supply = smp > 0 and f_consec >= 3 and i_today > 0
    p1_quiet  = muges_r < 0.5 and smp > 0 and f_today > 0
    # p1_samo: 사모 데이터 없으므로 생략

    # ── P2 신호 ────────────────────────────────────────
    p2_early = (
        f_today > 0 and i_today > 0 and
        vol_r >= 1.3 and smp > 0 and f_consec >= 2
    )
    p2_accel  = f_consec >= 5 and smp > 0 and vol_r >= 1.2
    p2_break  = vol_r >= 2.0 and f_today > 0

    # ── P3 신호 ────────────────────────────────────────
    p3_change = f_today < 0 and i_today < 0
    p3_spread = muges_r > 3.0 and f_today < 0

    # 우선순위로 대표 신호 선택
    if golden:
        phase, phase_key = "⭐ GOLDEN", "golden"
    elif p2_break:
        phase, phase_key = "🟢 P2 거래량돌파", "p2"
    elif p2_accel:
        phase, phase_key = "🟢 P2 수급가속", "p2"
    elif p2_early:
        phase, phase_key = "🟢 P2 상승초기", "p2"
    elif p1_supply:
        phase, phase_key = "🔵 P1 수급복합", "p1"
    elif p1_quiet:
        phase, phase_key = "🔵 P1 조용매집", "p1"
    elif p1_obv:
        phase, phase_key = "🔵 P1 OBV매집", "p1"
    elif p3_spread:
        phase, phase_key = "🔴 P3 분산경고", "p3"
    elif p3_change:
        phase, phase_key = "🔴 P3 손바뀜경고", "p3"
    else:
        phase, phase_key = "", "none"

    return {
        "phase":      phase,
        "phase_key":  phase_key,
        "smp":        round(smp, 2),
        "muges_ratio": round(muges_r, 2),
        "obv_above_ma": bool(obv_val > obv_ma),
        "vol_ratio":   round(vol_r, 2),
        "f_consec":    f_consec,
        "i_consec":    i_consec,
        "f_today_buy": f_today > 0,
        "i_today_buy": i_today > 0,
    }


# ─── 52주 신고가 판별 ─────────────────────────────────────
def check_new_high(stock):
    price   = stock["price"]
    high52  = stock["high52"]
    if high52 == 0:
        return ""
    ratio = price / high52 * 100
    if ratio >= 99.5:
        return "🔥신고가"
    elif ratio >= 97:
        return "📍신고가근접"
    return ""


# ─── 메인 실행 ───────────────────────────────────────────
def main():
    now_kst = datetime.datetime.now() + datetime.timedelta(hours=9)
    print(f"\n{'='*50}")
    print(f"📡 데이터 수집 시작: {now_kst.strftime('%Y-%m-%d %H:%M KST')}")
    print(f"{'='*50}")

    token = get_access_token()
    print("✅ KIS 토큰 발급 완료")

    # 1. 지수 수집
    print("\n📊 지수 수집 중...")
    indices = fetch_indices(token)

    # 2. 시장 수급
    print("💰 시장 수급 수집 중...")
    market_supply = fetch_market_supply(token)

    # 3. 종목별 수집
    stocks = []
    print(f"\n📈 종목 데이터 수집 중... ({len(WATCH_LIST)}개)")
    for code in WATCH_LIST:
        try:
            print(f"  [{code}] ", end="", flush=True)

            # 현재가
            stock = fetch_stock_price(code, token)
            time.sleep(0.3)

            # 일봉
            ohlcv = fetch_daily_ohlcv(code, token, count=60)
            time.sleep(0.3)

            # 수급
            supply = fetch_supply(code, token)
            time.sleep(0.3)

            # Phase 신호 계산
            signals = calc_phase_signals(ohlcv, supply, stock["mktcap"])
            stock.update(signals)

            # 신고가 여부
            stock["nh_flag"] = check_new_high(stock)

            # 최근 수급 요약 (오늘)
            if supply:
                today_sup = supply[-1]
                stock["foreign_today"] = today_sup.get("foreign_amt", 0)
                stock["inst_today"]    = today_sup.get("inst_amt", 0)
            else:
                stock["foreign_today"] = 0
                stock["inst_today"]    = 0

            stocks.append(stock)
            print(f"{stock['name']} | {stock['phase'] or '신호없음'}")

        except Exception as e:
            print(f"\n  ⚠️ {code} 실패: {e}")

    # 4. 저장
    now_str = now_kst.strftime("%Y-%m-%d %H:%M")
    payload = {
        "updated_at":     now_str,
        "is_market_open": 9*60+5 <= now_kst.hour*60+now_kst.minute <= 15*60+30,
        "indices":        indices,
        "market_supply":  market_supply,
        "stocks":         stocks,
        "phase_stats": {
            "golden": sum(1 for s in stocks if s.get("phase_key") == "golden"),
            "p1":     sum(1 for s in stocks if s.get("phase_key") == "p1"),
            "p2":     sum(1 for s in stocks if s.get("phase_key") == "p2"),
            "p3":     sum(1 for s in stocks if s.get("phase_key") == "p3"),
            "new_high": sum(1 for s in stocks if s.get("nh_flag") == "🔥신고가"),
        },
    }

    out_path = DATA_DIR / "market.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"\n✅ 저장 완료: {out_path}")
    print(f"   종목 {len(stocks)}개 | GOLDEN {payload['phase_stats']['golden']}개 | 신고가 {payload['phase_stats']['new_high']}개")


if __name__ == "__main__":
    main()

