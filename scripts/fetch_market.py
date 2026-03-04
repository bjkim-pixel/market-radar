import os, json, math, time, requests
from datetime import datetime, timedelta

APP_KEY    = os.environ["KIS_APP_KEY"]
APP_SECRET = os.environ["KIS_APP_SECRET"]
BASE_URL   = "https://openapi.koreainvestment.com:9443"
TODAY      = datetime.now().strftime("%Y%m%d")


def get_token():
    r = requests.post(f"{BASE_URL}/oauth2/tokenP", json={
        "grant_type": "client_credentials",
        "appkey":     APP_KEY,
        "appsecret":  APP_SECRET,
    }, timeout=10)
    token = r.json()["access_token"]
    print("[token] issued")
    return token


def kis_get(path, params, tr_id, token, retry=2):
    headers = {
        "Content-Type":  "application/json",
        "authorization": f"Bearer {token}",
        "appkey":        APP_KEY,
        "appsecret":     APP_SECRET,
        "tr_id":         tr_id,
        "custtype":      "P",
    }
    for attempt in range(retry):
        try:
            r = requests.get(
                f"{BASE_URL}{path}",
                headers=headers,
                params=params,
                timeout=15
            )
            if not r.text or not r.text.strip():
                return {}
            d = r.json()
            if d.get("rt_cd") == "0":
                return d
            code = d.get("msg_cd", "")
            if code in ("EGW00201", "EGW00202"):
                time.sleep(0.4)
                continue
            print(f"  API error [{tr_id}]: {d.get('msg1','')}")
            return {}
        except Exception as e:
            print(f"  request failed [{tr_id}]: {e}")
            time.sleep(0.5)
    return {}


def safe_float(v):
    try:
        return float(str(v).replace(",", ""))
    except Exception:
        return 0.0


def safe_int(v):
    try:
        return int(float(str(v).replace(",", "")))
    except Exception:
        return 0


def clean_nan(obj):
    if isinstance(obj, dict):
        return {k: clean_nan(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_nan(v) for v in obj]
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return 0
    return obj


# ----------------------------------------
# 1. 지수
# ----------------------------------------
def fetch_indices(token):
    INDICES = [
        ("0001", "KOSPI",    "U"),
        ("1001", "KOSDAQ",   "U"),
        ("0002", "KOSPI200", "U"),
    ]
    results = []
    for iscd, name, div in INDICES:
        d = kis_get(
            "/uapi/domestic-stock/v1/quotations/inquire-index-price",
            {"FID_COND_MRKT_DIV_CODE": div, "FID_INPUT_ISCD": iscd},
            "FHPUP02100000", token
        )
        o = d.get("output", {})
        if not o:
            continue
        results.append({
            "name":   name,
            "value":  safe_float(o.get("bstp_nmix_prpr", 0)),
            "change": safe_float(o.get("bstp_nmix_prdy_ctrt", 0)),
            "diff":   safe_float(o.get("bstp_nmix_prdy_vrss", 0)),
            "ascn":   safe_int(o.get("ascn_issu_cnt", 0)),
            "down":   safe_int(o.get("down_issu_cnt", 0)),
            "tr_amt": safe_float(o.get("acml_tr_pbmn", 0)),
        })
        time.sleep(0.05)
    print(f"  [index] {len(results)}")
    return results


# ----------------------------------------
# 2. 섹터
# ----------------------------------------
KOSPI_SECTORS = [
    ("1028","에너지"),("1029","소재"),("1030","산업재"),("1031","경기소비재"),
    ("1032","필수소비재"),("1033","건강관리"),("1034","금융"),("1035","IT"),
    ("1036","통신서비스"),("1037","유틸리티"),
    ("0003","대형주"),("0004","중형주"),("0005","소형주"),
]
KOSDAQ_SECTORS = [
    ("2005","IT"),("2006","제조"),("2007","건설"),("2008","유통"),("2009","운송"),
    ("2010","금융"),("2011","오락문화"),("2012","통신방송"),("2013","인터넷"),
    ("2014","디지털컨텐츠"),("2015","소프트웨어"),("2016","컴퓨터서비스"),
    ("2017","통신장비"),("2018","IT부품"),("2019","반도체"),("2020","제약"),
    ("2021","의료정밀기기"),("2022","음식료담배"),
]


def fetch_all_sectors(token):
    sectors = []
    targets = (
        [(iscd, n, "KOSPI")  for iscd, n in KOSPI_SECTORS] +
        [(iscd, n, "KOSDAQ") for iscd, n in KOSDAQ_SECTORS]
    )
    for iscd, name, mkt in targets:
        d = kis_get(
            "/uapi/domestic-stock/v1/quotations/inquire-index-price",
            {"FID_COND_MRKT_DIV_CODE": "U", "FID_INPUT_ISCD": iscd},
            "FHPUP02100000", token
        )
        o = d.get("output", {})
        val = safe_float(o.get("bstp_nmix_prpr", 0))
        if not o or not val:
            time.sleep(0.05)
            continue
        sectors.append({
            "iscd":     iscd,
            "name":     o.get("hts_kor_isnm", name),
            "mkt_type": mkt,
            "value":    val,
            "change":   safe_float(o.get("bstp_nmix_prdy_ctrt", 0)),
            "tr_amt":   safe_float(o.get("acml_tr_pbmn", 0)) / 1_000_000,
            "history":  [],
        })
        time.sleep(0.06)
    print(f"  [sector] {len(sectors)}")
    return sectors


# ----------------------------------------
# 3. ★ 시총 1조 이상 전체 종목 스캔
#    TR_ID: FHKST04010200 (시총순 정렬)
#    FID_BLNG_CLS_CODE=0 전체, 시총순으로 페이지 수집
# ----------------------------------------
def fetch_large_cap_stocks(token, mkt_div, min_mktcap_billion=1000):
    """
    시총 기준 상위 종목 수집
    min_mktcap_billion: 최소 시총 (억원 단위, 1000 = 1조)
    FHKST04010200: 시장조건별 종목 순위 (시총순 정렬)
    """
    mkt_name = "KOSPI" if mkt_div == "J" else "KOSDAQ"

    # 시총순 정렬로 종목 수집
    params = {
        "FID_COND_MRKT_DIV_CODE": mkt_div,
        "FID_COND_SCR_DIV_CODE":  "20171",
        "FID_INPUT_ISCD":         "0000",
        "FID_DIV_CLS_CODE":       "0",
        "FID_BLNG_CLS_CODE":      "0",
        "FID_TRGT_CLS_CODE":      "111111111",
        "FID_TRGT_EXLS_CLS_CODE": "000000",
        "FID_INPUT_PRICE_1":      "",
        "FID_INPUT_PRICE_2":      "",
        "FID_VOL_CNT":            "",
        "FID_INPUT_DATE_1":       "",
    }

    d = kis_get(
        "/uapi/domestic-stock/v1/quotations/volume-rank",
        params, "FHKST04010200", token
    )

    rows = d.get("output", [])
    if not rows:
        print(f"  [large cap] {mkt_name}: no data")
        return []

    results = []
    for r in rows:
        code   = r.get("mksc_shrn_iscd", "").strip()
        price  = safe_int(r.get("stck_prpr", 0))
        # 시가총액: data_rank API 결과에 없는 경우가 많아 일단 수집 후 상세에서 보완
        if not code or not price:
            continue
        results.append({
            "code":   code,
            "name":   r.get("hts_kor_isnm", "").strip(),
            "market": mkt_name,   # 나중에 종목기본정보로 덮어씀
            "price":  price,
            "change": safe_float(r.get("prdy_ctrt", 0)),
            "diff":   safe_int(r.get("prdy_vrss", 0)),
            "volume": safe_int(r.get("acml_vol", 0)),
            "tr_val": safe_int(r.get("acml_tr_pbmn", 0)),
            "sector": r.get("bstp_kor_isnm", "").strip(),
            "high52": safe_int(r.get("d250_hgpr", 0)),
            "low52":  safe_int(r.get("d250_lwpr", 0)),
            "mktcap": 0,  # 상세에서 채움
        })

    print(f"  [large cap raw] {mkt_name} {len(results)}")
    return results


# ----------------------------------------
# 4. ★ 종목 기본정보 조회
#    TR_ID: FHKST01010100
#    - 정확한 시장구분 (KOSPI/KOSDAQ)
#    - 업종명
#    - 시가총액
# ----------------------------------------
def fetch_stock_info(token, code):
    """
    종목 기본정보: 시장구분, 업종, 시가총액
    TR_ID: FHKST01010100 (주식현재가 시세)
    """
    d = kis_get(
        "/uapi/domestic-stock/v1/quotations/inquire-price",
        {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD":         code,
        },
        "FHKST01010100", token
    )
    o = d.get("output", {})
    if not o:
        return {}

    # 시장구분: bstp_kor_isnm 또는 rprs_mrkt_kor_name
    mrkt_name = o.get("rprs_mrkt_kor_name", "")
    if "코스닥" in mrkt_name or "KOSDAQ" in mrkt_name:
        market = "KOSDAQ"
    else:
        market = "KOSPI"

    # 시가총액 (억원 단위로 저장)
    mktcap_str = o.get("hts_avls", "0")  # 시가총액 (억원)
    mktcap = safe_float(mktcap_str)       # 억원

    return {
        "market": market,
        "sector": o.get("bstp_kor_isnm", "").strip(),   # 업종명
        "mktcap": mktcap,                                # 억원
        "high52": safe_int(o.get("d250_hgpr", 0)),
        "low52":  safe_int(o.get("d250_lwpr", 0)),
        "per":    safe_float(o.get("per", 0)),
        "pbr":    safe_float(o.get("pbr", 0)),
    }


# ----------------------------------------
# 5. 투자자 매매동향 30일
# ----------------------------------------
def fetch_stock_investor_history(token, code, market="J"):
    d = kis_get(
        "/uapi/domestic-stock/v1/quotations/inquire-investor",
        {"FID_COND_MRKT_DIV_CODE": market, "FID_INPUT_ISCD": code},
        "FHKST01010900", token
    )
    rows = d.get("output", [])
    result = []
    for r in rows:
        result.append({
            "date":    r.get("stck_bsop_date", ""),
            "foreign": safe_int(r.get("frgn_ntby_qty", 0)),
            "inst":    safe_int(r.get("orgn_ntby_qty", 0)),
            "indiv":   safe_int(r.get("prsn_ntby_qty", 0)),
            "famt":    safe_float(r.get("frgn_ntby_tr_pbmn", 0)) * 1_000_000,
            "iamt":    safe_float(r.get("orgn_ntby_tr_pbmn", 0)) * 1_000_000,
            "pamt":    safe_float(r.get("prsn_ntby_tr_pbmn", 0)) * 1_000_000,
        })
    return result


def calc_supply_periods(investor_history):
    def _sum(rows, n):
        return {
            "foreign": sum(r.get("famt", 0) for r in rows[:n]),
            "inst":    sum(r.get("iamt", 0) for r in rows[:n]),
            "indiv":   sum(r.get("pamt", 0) for r in rows[:n]),
        }
    return {
        "day":   _sum(investor_history, 1),
        "week":  _sum(investor_history, 5),
        "month": _sum(investor_history, 20),
    }


# ----------------------------------------
# 6. Phase 판정
# ----------------------------------------
def determine_phase(f_consec, i_consec, smp, nh_flag, obv_up):
    if nh_flag and f_consec >= 3 and smp > 0:
        return "golden", "GOLDEN - 신고가+외인매집"
    if f_consec >= 5 and i_consec >= 3 and smp > 1:
        return "golden", "GOLDEN - 강한 매집"
    if smp < -2 and f_consec == 0:
        return "p3", "P3 - 기관외인 이탈"
    if f_consec >= 3 and smp > 0 and obv_up:
        return "p2", "P2 - 상승 추세"
    if f_consec >= 2 or i_consec >= 2:
        return "p1", "P1 - 매집 초기"
    return "", ""


# ----------------------------------------
# 7. ★ 종목 상세 수집 (기본정보 + 투자자)
# ----------------------------------------
def fetch_stock_detail(token, stock, min_mktcap_billion=1000):
    """
    1. 종목기본정보 → 정확한 시장/업종/시가총액
    2. 투자자 30일 → 수급/Phase
    3. 시총 필터: min_mktcap_billion 억 미만이면 None 반환
    """
    code = stock["code"]

    # Step 1: 종목 기본정보 (시장/업종/시총 정확히)
    info = fetch_stock_info(token, code)
    time.sleep(0.07)

    if info:
        stock["market"] = info["market"]          # 정확한 시장 덮어쓰기
        stock["sector"] = info.get("sector") or stock.get("sector", "")
        stock["mktcap"] = info.get("mktcap", 0)  # 억원
        if info.get("high52"):
            stock["high52"] = info["high52"]
        if info.get("low52"):
            stock["low52"]  = info["low52"]
        stock["per"] = info.get("per", 0)
        stock["pbr"] = info.get("pbr", 0)

    # 시총 필터 (1조 = 10000억)
    mktcap = stock.get("mktcap", 0)
    if mktcap > 0 and mktcap < min_mktcap_billion:
        return None  # 필터 아웃

    # Step 2: 투자자 30일 히스토리
    market_code = "J" if stock["market"] == "KOSPI" else "Q"
    inv_hist = fetch_stock_investor_history(token, code, market_code)
    time.sleep(0.07)

    today_row     = inv_hist[0] if inv_hist else {}
    foreign_today = today_row.get("famt", 0)
    inst_today    = today_row.get("iamt", 0)
    indiv_today   = today_row.get("pamt", 0)

    supply_periods = calc_supply_periods(inv_hist)

    f_consec = 0
    for row in inv_hist:
        if row.get("foreign", 0) > 0:
            f_consec += 1
        else:
            break

    i_consec = 0
    for row in inv_hist:
        if row.get("inst", 0) > 0:
            i_consec += 1
        else:
            break

    high52   = stock.get("high52", 0)
    low52    = stock.get("low52",  0)
    price    = stock.get("price",  0)
    nh_ratio = round(price / high52 * 100, 1) if high52 else 0

    nh_flag = ""
    if nh_ratio >= 100:
        nh_flag = "신고가"
    elif nh_ratio >= 99:
        nh_flag = "99%"
    elif nh_ratio >= 97:
        nh_flag = "97%+"

    tr_val = stock.get("tr_val", 1) or 1
    smp    = round((foreign_today + inst_today) / tr_val * 100, 2)
    obv_up = (foreign_today + inst_today) > 0

    phase_key, phase = determine_phase(f_consec, i_consec, smp, nh_flag, obv_up)

    stock.update({
        "foreign_today":  foreign_today,
        "inst_today":     inst_today,
        "indiv_today":    indiv_today,
        "supply_periods": supply_periods,
        "f_consec":       f_consec,
        "i_consec":       i_consec,
        "high52":         high52,
        "low52":          low52,
        "nh_ratio":       nh_ratio,
        "nh_flag":        nh_flag,
        "smp":            smp,
        "obv_above_ma":   obv_up,
        "vol_ratio":      1.0,
        "phase_key":      phase_key,
        "phase":          phase,
    })
    return stock


# ----------------------------------------
# 8. 집계
# ----------------------------------------
def calc_market_supply(stocks):
    return {
        "foreign_net": sum(s.get("foreign_today", 0) for s in stocks),
        "inst_net":    sum(s.get("inst_today",    0) for s in stocks),
        "indiv_net":   sum(s.get("indiv_today",   0) for s in stocks),
    }


def build_summary(indices, stocks, market_supply, phase_stats):
    lines = []
    for idx in indices[:2]:
        sym = "+" if idx["change"] >= 0 else ""
        lines.append(f"{idx['name']} {sym}{idx['change']:.2f}% ({idx['value']:,.0f})")

    fn  = market_supply.get("foreign_net", 0)
    inn = market_supply.get("inst_net",    0)
    iv  = market_supply.get("indiv_net",   0)

    def amt_str(v):
        a = abs(v)
        s = f"{a/1e8:.0f}억" if a >= 1e8 else f"{a/1e4:.0f}만"
        return ("+" if v >= 0 else "-") + s

    lines.append(f"외국인 {amt_str(fn)} / 기관 {amt_str(inn)} / 개인 {amt_str(iv)}")

    if phase_stats.get("golden"):
        lines.append(f"GOLDEN {phase_stats['golden']}개 / P1매집 {phase_stats.get('p1', 0)}개")

    nh = [s for s in stocks if s.get("nh_flag")]
    if nh:
        lines.append(f"신고가 근접 {len(nh)}종목 / 대표: {nh[0]['name']}")

    return lines


# ----------------------------------------
# MAIN
# ----------------------------------------
def main():
    token = get_token()

    print("\n[1] index...")
    indices = fetch_indices(token)
    time.sleep(0.3)

    print("\n[2] sector...")
    sectors = fetch_all_sectors(token)
    time.sleep(0.3)

    # ----------------------------------------
    # 종목 수집: 거래대금 상위 (KOSPI 100 + KOSDAQ 50)
    # + 시총 1조 이상 필터는 상세 수집 단계에서 적용
    # ----------------------------------------
    print("\n[3] large cap stock list...")
    kospi_stocks  = fetch_large_cap_stocks(token, "J")
    time.sleep(0.25)
    kosdaq_stocks = fetch_large_cap_stocks(token, "Q")
    time.sleep(0.3)

    # 중복 제거 (거래대금 내림차순 우선)
    all_raw = kospi_stocks + kosdaq_stocks
    seen, unique = set(), []
    for s in sorted(all_raw, key=lambda x: x.get("tr_val", 0), reverse=True):
        if s["code"] not in seen and s["price"] > 0:
            seen.add(s["code"])
            unique.append(s)
    print(f"  raw unique: {len(unique)}")

    # ----------------------------------------
    # 종목 상세: 기본정보(시장/업종/시총) + 투자자(수급/Phase)
    # 시총 1조 미만은 자동 제외
    # ----------------------------------------
    print("\n[4] stock detail (info + investor + phase)...")
    MIN_MKTCAP = 10000   # 1조 = 10000억
    MAX_STOCKS = 200     # 최대 처리 수 (API 부하 고려)

    stocks = []
    filtered_out = 0

    for i, stock in enumerate(unique[:MAX_STOCKS]):
        try:
            s = fetch_stock_detail(token, stock, min_mktcap_billion=MIN_MKTCAP)
            if s is None:
                filtered_out += 1
            else:
                stocks.append(s)
            time.sleep(0.08)
            if (i + 1) % 20 == 0:
                kept = len(stocks)
                print(f"  ... {i+1}/{min(len(unique), MAX_STOCKS)} | kept:{kept} filtered:{filtered_out}")
        except Exception as e:
            print(f"  failed {stock.get('name', '?')}: {e}")

    print(f"  detail done: {len(stocks)} (filtered out: {filtered_out})")

    # ----------------------------------------
    # 집계
    # ----------------------------------------
    market_supply = calc_market_supply(stocks)
    phase_stats   = {
        "golden":   sum(1 for s in stocks if s.get("phase_key") == "golden"),
        "p2":       sum(1 for s in stocks if s.get("phase_key") == "p2"),
        "p1":       sum(1 for s in stocks if s.get("phase_key") == "p1"),
        "p3":       sum(1 for s in stocks if s.get("phase_key") == "p3"),
        "new_high": sum(1 for s in stocks if s.get("nh_flag")),
    }

    def top_by(lst, key, n=20, reverse=True):
        return sorted(
            [s for s in lst if s.get(key, 0) != 0],
            key=lambda x: x.get(key, 0),
            reverse=reverse
        )[:n]

    top_traders = {
        "foreign_buy":  top_by(stocks, "foreign_today", 20, True),
        "foreign_sell": top_by(stocks, "foreign_today", 20, False),
        "inst_buy":     top_by(stocks, "inst_today",    20, True),
        "inst_sell":    top_by(stocks, "inst_today",    20, False),
    }

    summary_lines = build_summary(indices, stocks, market_supply, phase_stats)
    now_str       = datetime.now().strftime("%Y-%m-%d %H:%M")

    payload = clean_nan({
        "updated_at":    now_str,
        "date":          datetime.now().strftime("%Y-%m-%d"),
        "indices":       indices,
        "sectors":       sectors,
        "stocks":        stocks,
        "top_traders":   top_traders,
        "market_supply": market_supply,
        "phase_stats":   phase_stats,
        "summary_lines": summary_lines,
    })

    os.makedirs("data", exist_ok=True)
    with open("data/market.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"\ndone: data/market.json")
    print(f"  index:{len(indices)} sector:{len(sectors)} stock:{len(stocks)}")
    print(f"  GOLDEN={phase_stats['golden']} P1={phase_stats['p1']} P3={phase_stats['p3']}")


if __name__ == "__main__":
    main()
