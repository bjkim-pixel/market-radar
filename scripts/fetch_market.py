import os, json, math, time, requests
from datetime import datetime, timedelta

APP_KEY    = os.environ["KIS_APP_KEY"]
APP_SECRET = os.environ["KIS_APP_SECRET"]
BASE_URL   = "https://openapi.koreainvestment.com:9443"


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
            r = requests.get(f"{BASE_URL}{path}", headers=headers,
                             params=params, timeout=15)
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
    try:    return float(str(v).replace(",", ""))
    except: return 0.0

def safe_int(v):
    try:    return int(float(str(v).replace(",", "")))
    except: return 0

def clean_nan(obj):
    if isinstance(obj, dict):  return {k: clean_nan(v) for k, v in obj.items()}
    if isinstance(obj, list):  return [clean_nan(v) for v in obj]
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)): return 0
    return obj


# ----------------------------------------
# 시총 1조 이상 주요 종목 목록
# ----------------------------------------
MAJOR_STOCKS = [
    # KOSPI
    ("005930","삼성전자","KOSPI"),
    ("000660","SK하이닉스","KOSPI"),
    ("373220","LG에너지솔루션","KOSPI"),
    ("207940","삼성바이오로직스","KOSPI"),
    ("005380","현대차","KOSPI"),
    ("068270","셀트리온","KOSPI"),
    ("105560","KB금융","KOSPI"),
    ("000270","기아","KOSPI"),
    ("005490","POSCO홀딩스","KOSPI"),
    ("055550","신한지주","KOSPI"),
    ("028260","삼성물산","KOSPI"),
    ("012330","현대모비스","KOSPI"),
    ("051910","LG화학","KOSPI"),
    ("006400","삼성SDI","KOSPI"),
    ("003550","LG","KOSPI"),
    ("086790","하나금융지주","KOSPI"),
    ("017670","SK텔레콤","KOSPI"),
    ("030200","KT","KOSPI"),
    ("009150","삼성전기","KOSPI"),
    ("032830","삼성생명","KOSPI"),
    ("066570","LG전자","KOSPI"),
    ("096770","SK이노베이션","KOSPI"),
    ("010130","고려아연","KOSPI"),
    ("010950","S-Oil","KOSPI"),
    ("034730","SK","KOSPI"),
    ("316140","우리금융지주","KOSPI"),
    ("002790","아모레퍼시픽","KOSPI"),
    ("004020","현대제철","KOSPI"),
    ("012450","한화에어로스페이스","KOSPI"),
    ("015760","한국전력","KOSPI"),
    ("033780","KT&G","KOSPI"),
    ("034020","두산에너빌리티","KOSPI"),
    ("042660","한화오션","KOSPI"),
    ("329180","현대중공업","KOSPI"),
    ("011200","HMM","KOSPI"),
    ("138040","메리츠금융지주","KOSPI"),
    ("078930","GS","KOSPI"),
    ("000880","한화","KOSPI"),
    ("003490","대한항공","KOSPI"),
    ("086280","현대글로비스","KOSPI"),
    ("139480","이마트","KOSPI"),
    ("097950","CJ제일제당","KOSPI"),
    ("128940","한미약품","KOSPI"),
    ("000100","유한양행","KOSPI"),
    ("185750","종근당","KOSPI"),
    ("006360","GS건설","KOSPI"),
    ("010140","삼성중공업","KOSPI"),
    ("047050","포스코인터내셔널","KOSPI"),
    ("064350","현대로템","KOSPI"),
    ("079550","LIG넥스원","KOSPI"),
    ("047810","한국항공우주","KOSPI"),
    ("024110","기업은행","KOSPI"),
    ("011780","금호석유","KOSPI"),
    ("000720","현대건설","KOSPI"),
    ("018260","삼성에스디에스","KOSPI"),
    ("326030","SK바이오팜","KOSPI"),
    ("000120","CJ대한통운","KOSPI"),
    ("011170","롯데케미칼","KOSPI"),
    ("282330","BGF리테일","KOSPI"),
    ("009830","한화솔루션","KOSPI"),
    ("000810","삼성화재","KOSPI"),
    ("032640","LG유플러스","KOSPI"),
    ("036460","한국가스공사","KOSPI"),
    ("021240","코웨이","KOSPI"),
    ("030000","제일기획","KOSPI"),
    ("002380","KCC","KOSPI"),
    ("010620","현대미포조선","KOSPI"),
    ("267250","HD현대","KOSPI"),
    ("004800","효성","KOSPI"),
    ("035250","강원랜드","KOSPI"),
    ("180640","한진칼","KOSPI"),
    ("071050","한국금융지주","KOSPI"),
    ("000060","메리츠화재","KOSPI"),
    ("001450","현대해상","KOSPI"),
    ("005945","NH투자증권","KOSPI"),
    ("039490","키움증권","KOSPI"),
    ("006800","미래에셋증권","KOSPI"),
    ("016360","삼성증권","KOSPI"),
    ("001040","CJ","KOSPI"),
    ("097230","한진","KOSPI"),
    ("004990","롯데지주","KOSPI"),
    ("023530","롯데쇼핑","KOSPI"),
    ("069960","현대백화점","KOSPI"),
    ("004170","신세계","KOSPI"),
    ("271560","오리온","KOSPI"),
    ("003230","삼양식품","KOSPI"),
    ("007310","오뚜기","KOSPI"),
    ("051600","한전KPS","KOSPI"),
    ("090430","아모레G","KOSPI"),
    ("161390","한국타이어앤테크놀로지","KOSPI"),
    ("042670","HD현대인프라코어","KOSPI"),
    ("011790","SKC","KOSPI"),
    ("003410","쌍용C&E","KOSPI"),
    ("001680","대상","KOSPI"),
    ("007070","GS리테일","KOSPI"),
    ("010060","OCI","KOSPI"),
    ("008560","메리츠증권","KOSPI"),
    ("382800","한화시스템","KOSPI"),
    ("003570","SNT다이내믹스","KOSPI"),
    ("000210","DL","KOSPI"),
    ("008770","호텔신라","KOSPI"),
    ("009540","HD한국조선해양","KOSPI"),
    ("000080","하이트진로","KOSPI"),
    ("307950","현대오토에버","KOSPI"),
    ("014680","한솔케미칼","KOSPI"),
    ("069620","대웅제약","KOSPI"),
    ("018880","한온시스템","KOSPI"),
    ("105630","한세실업","KOSPI"),
    # KOSDAQ
    ("247540","에코프로비엠","KOSDAQ"),
    ("086520","에코프로","KOSDAQ"),
    ("196170","알테오젠","KOSDAQ"),
    ("028300","HLB","KOSDAQ"),
    ("403870","HPSP","KOSDAQ"),
    ("141080","리가켐바이오","KOSDAQ"),
    ("145020","휴젤","KOSDAQ"),
    ("214150","클래시스","KOSDAQ"),
    ("214450","파마리서치","KOSDAQ"),
    ("277810","레인보우로보틱스","KOSDAQ"),
    ("357780","솔브레인","KOSDAQ"),
    ("036830","솔브레인홀딩스","KOSDAQ"),
    ("263750","펄어비스","KOSDAQ"),
    ("293490","카카오게임즈","KOSDAQ"),
    ("035900","JYP Ent","KOSDAQ"),
    ("041510","에스엠","KOSDAQ"),
    ("352820","하이브","KOSDAQ"),
    ("122870","와이지엔터테인먼트","KOSDAQ"),
    ("095340","ISC","KOSDAQ"),
    ("091990","셀트리온헬스케어","KOSDAQ"),
    ("039030","이오테크닉스","KOSDAQ"),
    ("240810","원익IPS","KOSDAQ"),
    ("131970","두산테스나","KOSDAQ"),
    ("348210","넥스틴","KOSDAQ"),
    ("039200","오스코텍","KOSDAQ"),
    ("067630","HLB생명과학","KOSDAQ"),
    ("048410","현대바이오","KOSDAQ"),
    ("335890","비올","KOSDAQ"),
    ("237690","에스티팜","KOSDAQ"),
    ("108490","로보티즈","KOSDAQ"),
    ("053800","안랩","KOSDAQ"),
    ("200780","티에스이","KOSDAQ"),
    ("251970","펩트론","KOSDAQ"),
    ("950130","엑세스바이오","KOSDAQ"),
    ("228760","지노믹트리","KOSDAQ"),
    ("066970","엘앤에프","KOSDAQ"),
    ("058470","리노공업","KOSDAQ"),
    ("336570","원텍","KOSDAQ"),
    ("950160","코오롱티슈진","KOSDAQ"),
    ("214420","토니모리","KOSDAQ"),
]


# ----------------------------------------
# 1. 지수
# ----------------------------------------
def fetch_indices(token):
    INDICES = [
        ("0001","KOSPI","U"),
        ("1001","KOSDAQ","U"),
        ("0002","KOSPI200","U"),
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
    ("2005","IT"),("2006","제조"),("2007","건설"),("2008","유통"),
    ("2009","운송"),("2010","금융"),("2011","오락문화"),("2012","통신방송"),
    ("2013","인터넷"),("2014","디지털컨텐츠"),("2015","소프트웨어"),
    ("2016","컴퓨터서비스"),("2017","통신장비"),("2018","IT부품"),
    ("2019","반도체"),("2020","제약"),("2021","의료정밀기기"),("2022","음식료담배"),
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
# 3. 종목 현재가 + 기본정보
# ----------------------------------------
def fetch_stock_price(token, code, default_market="KOSPI"):
    d = kis_get(
        "/uapi/domestic-stock/v1/quotations/inquire-price",
        {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": code},
        "FHKST01010100", token
    )
    o = d.get("output", {})
    if not o:
        return None

    mrkt = o.get("rprs_mrkt_kor_name", "")
    if "코스닥" in mrkt or "KOSDAQ" in mrkt.upper():
        market = "KOSDAQ"
    elif "코스피" in mrkt or "KOSPI" in mrkt.upper():
        market = "KOSPI"
    else:
        market = default_market

    price = safe_int(o.get("stck_prpr", 0))
    if not price:
        return None

    return {
        "price":  price,
        "change": safe_float(o.get("prdy_ctrt", 0)),
        "diff":   safe_int(o.get("prdy_vrss", 0)),
        "volume": safe_int(o.get("acml_vol", 0)),
        "tr_val": safe_int(o.get("acml_tr_pbmn", 0)),
        "market": market,
        "sector": o.get("bstp_kor_isnm", "").strip(),
        "mktcap": safe_float(o.get("hts_avls", 0)),
        "high52": safe_int(o.get("d250_hgpr", 0)),
        "low52":  safe_int(o.get("d250_lwpr", 0)),
        "per":    safe_float(o.get("per", 0)),
        "pbr":    safe_float(o.get("pbr", 0)),
    }


# ----------------------------------------
# 4. 투자자 매매동향 30일
# ----------------------------------------
def fetch_stock_investor_history(token, code):
    d = kis_get(
        "/uapi/domestic-stock/v1/quotations/inquire-investor",
        {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": code},
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


# ----------------------------------------
# 5. 일별 종가 (최근 40일)
# ----------------------------------------
def fetch_stock_ohlcv(token, code):
    kst_now  = datetime.utcnow() + timedelta(hours=9)
    end_dt   = kst_now.strftime("%Y%m%d")
    start_dt = (kst_now - timedelta(days=40)).strftime("%Y%m%d")
    d = kis_get(
        "/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice",
        {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD":         code,
            "FID_INPUT_DATE_1":       start_dt,
            "FID_INPUT_DATE_2":       end_dt,
            "FID_PERIOD_DIV_CODE":    "D",
            "FID_ORG_ADJ_PRC":        "1",
        },
        "FHKST03010100", token
    )
    result = {}
    for r in (d.get("output2") or []):
        dt = r.get("stck_bsop_date", "")
        cl = safe_int(r.get("stck_clpr", 0))
        if dt and cl:
            result[dt] = cl
    return result


def calc_supply_periods(inv):
    def _sum(rows, n):
        return {
            "foreign": sum(r.get("famt", 0) for r in rows[:n]),
            "inst":    sum(r.get("iamt", 0) for r in rows[:n]),
            "indiv":   sum(r.get("pamt", 0) for r in rows[:n]),
        }
    return {
        "day":   _sum(inv, 1),
        "week":  _sum(inv, 5),
        "month": _sum(inv, 20),
    }


# ----------------------------------------
# 6. 매직지수
# ----------------------------------------
def calc_magic(famt, iamt, mktcap_won):
    if mktcap_won <= 0:
        return 0.0
    return round((famt + iamt) / mktcap_won * 100, 4)


# ----------------------------------------
# 7. Phase 판정
# ----------------------------------------
def determine_phase(f_consec, i_consec, magic, nh_flag, obv_up):
    if nh_flag and f_consec >= 3 and magic > 0:
        return "golden", "GOLDEN - 신고가+외인매집"
    if f_consec >= 5 and i_consec >= 3 and magic > 0.01:
        return "golden", "GOLDEN - 강한 매집"
    if magic < -0.05 and f_consec == 0:
        return "p3", "P3 - 기관외인 이탈"
    if f_consec >= 3 and magic > 0 and obv_up:
        return "p2", "P2 - 상승 추세"
    if f_consec >= 2 or i_consec >= 2:
        return "p1", "P1 - 매집 초기"
    return "", ""


def determine_daily_phase(famt, iamt):
    if famt > 0 and iamt > 0:
        return "매집",  "golden"
    if famt > 0:
        return "외인↑", "p2"
    if iamt > 0:
        return "기관↑", "p1"
    if famt < 0 and iamt < 0:
        return "이탈",  "p3"
    return "-", ""


# ----------------------------------------
# 8. 전체 종목 수집
# ----------------------------------------
def fetch_all_stocks(token):
    stocks = []
    total  = len(MAJOR_STOCKS)

    for i, (code, name, default_mkt) in enumerate(MAJOR_STOCKS):
        try:
            info = fetch_stock_price(token, code, default_mkt)
            time.sleep(0.07)
            if not info:
                continue

            mktcap_won = info["mktcap"] * 1e8

            inv_hist = fetch_stock_investor_history(token, code)
            time.sleep(0.07)

            ohlcv = fetch_stock_ohlcv(token, code)
            time.sleep(0.07)

            today   = inv_hist[0] if inv_hist else {}
            f_today = today.get("famt", 0)
            i_today = today.get("iamt", 0)
            p_today = today.get("pamt", 0)

            supply_periods = calc_supply_periods(inv_hist)

            f_consec = 0
            for row in inv_hist:
                if row.get("foreign", 0) > 0: f_consec += 1
                else: break

            i_consec = 0
            for row in inv_hist:
                if row.get("inst", 0) > 0: i_consec += 1
                else: break

            high52   = info["high52"]
            low52    = info["low52"]
            price    = info["price"]
            nh_ratio = round(price / high52 * 100, 1) if high52 else 0

            nh_flag = ""
            if nh_ratio >= 100:  nh_flag = "신고가"
            elif nh_ratio >= 99: nh_flag = "99%"
            elif nh_ratio >= 97: nh_flag = "97%+"

            magic  = calc_magic(f_today, i_today, mktcap_won)
            obv_up = (f_today + i_today) > 0

            phase_key, phase = determine_phase(
                f_consec, i_consec, magic, nh_flag, obv_up
            )

            daily_data = []
            for row in inv_hist[:10]:
                dt    = row.get("date", "")
                famt  = row.get("famt", 0)
                iamt  = row.get("iamt", 0)
                pamt  = row.get("pamt", 0)
                d_phase, d_key = determine_daily_phase(famt, iamt)
                daily_data.append({
                    "date":      dt,
                    "close":     ohlcv.get(dt, 0),
                    "famt":      famt,
                    "iamt":      iamt,
                    "pamt":      pamt,
                    "magic":     calc_magic(famt, iamt, mktcap_won),
                    "phase":     d_phase,
                    "phase_key": d_key,
                })

            stocks.append({
                "code":           code,
                "name":           name,
                "market":         info["market"],
                "price":          price,
                "change":         info["change"],
                "diff":           info["diff"],
                "volume":         info["volume"],
                "tr_val":         info["tr_val"],
                "sector":         info["sector"],
                "mktcap":         info["mktcap"],
                "per":            info["per"],
                "pbr":            info["pbr"],
                "high52":         high52,
                "low52":          low52,
                "nh_ratio":       nh_ratio,
                "nh_flag":        nh_flag,
                "foreign_today":  f_today,
                "inst_today":     i_today,
                "indiv_today":    p_today,
                "supply_periods": supply_periods,
                "f_consec":       f_consec,
                "i_consec":       i_consec,
                "magic":          magic,
                "obv_above_ma":   obv_up,
                "vol_ratio":      1.0,
                "phase_key":      phase_key,
                "phase":          phase,
                "daily_data":     daily_data,
            })

            if (i + 1) % 20 == 0:
                print(f"  ... {i+1}/{total} | stocks:{len(stocks)}")

        except Exception as e:
            print(f"  failed [{code}] {name}: {e}")

    print(f"  [stocks] total:{len(stocks)}")
    return stocks

def build_sector_stock_map(sectors, stocks):
    """
    섹터명 ↔ 종목 업종명 매핑 테이블 생성
    KIS API의 섹터명과 종목 업종명이 다를 수 있어서
    직접 매핑 테이블을 정의
    """
    # KIS 섹터명 → 종목 bstp_kor_isnm 키워드 매핑
    SECTOR_KEYWORD_MAP = {
        # KOSPI
        "에너지":       ["에너지","정유"],
        "소재":         ["소재","화학","철강","비철금속","종이"],
        "산업재":       ["산업재","기계","건설","운수","조선"],
        "경기소비재":   ["경기소비재","자동차","소매","미디어","호텔"],
        "필수소비재":   ["필수소비재","식품","음식료","생활용품"],
        "건강관리":     ["건강관리","제약","바이오","의료"],
        "금융":         ["금융","은행","증권","보험"],
        "IT":           ["IT","반도체","하드웨어","소프트웨어","통신장비"],
        "통신서비스":   ["통신서비스","통신"],
        "유틸리티":     ["유틸리티","전기","가스"],
        # KOSDAQ
        "제약":         ["제약","바이오","의약"],
        "반도체":       ["반도체","IT부품"],
        "소프트웨어":   ["소프트웨어","IT서비스"],
        "인터넷":       ["인터넷","디지털컨텐츠"],
        "제조":         ["제조","기계","장비"],
        "오락문화":     ["오락","엔터테인먼트","문화"],
        "의료정밀기기": ["의료기기","정밀기기","의료"],
    }

    sector_map = {}
    for sec in sectors:
        name    = sec.get("name", "")
        iscd    = sec.get("iscd", "")
        # 매핑 테이블에서 키워드 찾기
        keywords = None
        for key, kws in SECTOR_KEYWORD_MAP.items():
            if key in name or name in key:
                keywords = kws
                break

        if not keywords:
            # 매핑 없으면 섹터명 자체로 정확 매칭
            keywords = [name.replace(" ", "")]

        matched_codes = []
        for s in stocks:
            stock_sector = (s.get("sector") or "").replace(" ", "")
            for kw in keywords:
                if kw in stock_sector:
                    matched_codes.append(s["code"])
                    break

        sector_map[iscd] = matched_codes

    return sector_map


# ----------------------------------------
# 9. 집계
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
# 10. 텔레그램
# ----------------------------------------
def send_telegram(token, chat_id, message):
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": message, "parse_mode": "HTML"},
            timeout=10
        )
        if not r.ok:
            print(f"[telegram] 오류: {r.text[:200]}")
        else:
            print("[telegram] 전송 완료")
    except Exception as e:
        print(f"[telegram] 전송 실패: {e}")


def build_telegram_messages(indices, sectors, stocks, market_supply, phase_stats, now_str):
    """사이트 주요 내용을 섹션별 메시지 리스트로 반환"""

    def fmt(v):
        a = abs(v)
        s = f"{a/1e8:.0f}억" if a >= 1e8 else f"{a/1e4:.0f}만"
        return ("+" if v >= 0 else "-") + s

    def arrow(v):
        return "📈" if v >= 0 else "📉"

    def pct(v):
        return f"{'+' if v>=0 else ''}{v:.2f}%"

    messages = []

    # ── 메시지 1: 헤더 + 지수 + 시장 수급 ──────────────────
    idx_lines = "\n".join(
        f"  {arrow(i['change'])} <b>{i['name']}</b>  "
        f"{i['value']:,.0f}  <b>{pct(i['change'])}</b>  "
        f"(상승 {i.get('ascn',0)} / 하락 {i.get('down',0)})"
        for i in indices
    )
    ms = market_supply
    fn, inn, iv = ms.get('foreign_net',0), ms.get('inst_net',0), ms.get('indiv_net',0)

    msg1 = (
        f"📡 <b>마켓레이더  |  {now_str} KST</b>\n"
        f"{'━'*30}\n\n"
        f"📊 <b>[ 지수 ]</b>\n"
        f"{idx_lines}\n\n"
        f"💰 <b>[ 시장 수급 ]</b>\n"
        f"  외국인  <b>{fmt(fn)}</b>\n"
        f"  기관    <b>{fmt(inn)}</b>\n"
        f"  개인    <b>{fmt(iv)}</b>\n"
    )
    messages.append(msg1)

    # ── 메시지 2: Phase 신호 종목 ──────────────────────────
    golden = [s for s in stocks if s.get("phase_key") == "golden"]
    p2     = [s for s in stocks if s.get("phase_key") == "p2"]
    p1     = [s for s in stocks if s.get("phase_key") == "p1"]
    p3     = [s for s in stocks if s.get("phase_key") == "p3"]

    def phase_rows(lst, max_n=5):
        rows = []
        for s in lst[:max_n]:
            mk  = "Q" if s["market"] == "KOSDAQ" else "K"
            nh  = f" 🚀{s['nh_flag']}" if s.get("nh_flag") else ""
            rows.append(
                f"  • {s['name']}[{mk}]{nh}  "
                f"{pct(s['change'])}  "
                f"매직 {s['magic']:+.4f}%  "
                f"외인{s['f_consec']}일"
            )
        if len(lst) > max_n:
            rows.append(f"  ... 외 {len(lst)-max_n}개")
        return "\n".join(rows) if rows else "  없음"

    ps = phase_stats
    msg2 = (
        f"📡 <b>[ Phase 신호 ]</b>\n"
        f"⭐ GOLDEN {ps.get('golden',0)}개  "
        f"🟢 P2 {ps.get('p2',0)}개  "
        f"🔵 P1 {ps.get('p1',0)}개  "
        f"🔴 P3 {ps.get('p3',0)}개\n\n"
        f"⭐ <b>GOLDEN</b>\n{phase_rows(golden)}\n\n"
        f"🟢 <b>P2 상승추세</b>\n{phase_rows(p2)}\n\n"
        f"🔵 <b>P1 매집초기</b>\n{phase_rows(p1)}\n\n"
        f"🔴 <b>P3 이탈경고</b>\n{phase_rows(p3, 3)}\n"
    )
    messages.append(msg2)

    # ── 메시지 3: 외인/기관 Top 매수 ──────────────────────
    f_buy = sorted([s for s in stocks if s.get("foreign_today",0)>0],
                   key=lambda x: x["foreign_today"], reverse=True)[:5]
    i_buy = sorted([s for s in stocks if s.get("inst_today",0)>0],
                   key=lambda x: x["inst_today"], reverse=True)[:5]
    f_sell= sorted([s for s in stocks if s.get("foreign_today",0)<0],
                   key=lambda x: x["foreign_today"])[:3]
    i_sell= sorted([s for s in stocks if s.get("inst_today",0)<0],
                   key=lambda x: x["inst_today"])[:3]

    def trader_rows(lst, key):
        rows = []
        for s in lst:
            mk = "Q" if s["market"]=="KOSDAQ" else "K"
            rows.append(
                f"  • {s['name']}[{mk}]  "
                f"<b>{fmt(s[key])}</b>  {pct(s['change'])}"
            )
        return "\n".join(rows) if rows else "  없음"

    msg3 = (
        f"💰 <b>[ 외국인 수급 ]</b>\n"
        f"▲ 상위 매수\n{trader_rows(f_buy,'foreign_today')}\n\n"
        f"▽ 상위 매도\n{trader_rows(f_sell,'foreign_today')}\n\n"
        f"🏛️ <b>[ 기관 수급 ]</b>\n"
        f"▲ 상위 매수\n{trader_rows(i_buy,'inst_today')}\n\n"
        f"▽ 상위 매도\n{trader_rows(i_sell,'inst_today')}\n"
    )
    messages.append(msg3)

    # ── 메시지 4: 외인/기관 연속 순매수 + 신고가 ───────────
    f_consec_list = sorted([s for s in stocks if s.get("f_consec",0)>=3],
                            key=lambda x: x["f_consec"], reverse=True)[:5]
    i_consec_list = sorted([s for s in stocks if s.get("i_consec",0)>=3],
                            key=lambda x: x["i_consec"], reverse=True)[:5]
    nh_list       = [s for s in stocks if s.get("nh_flag")]
    nh_list       = sorted(nh_list, key=lambda x: x.get("nh_ratio",0), reverse=True)[:5]

    def consec_rows(lst, key):
        rows = []
        for s in lst:
            mk = "Q" if s["market"]=="KOSDAQ" else "K"
            rows.append(
                f"  • {s['name']}[{mk}]  "
                f"<b>{s[key]}일 연속</b>  {pct(s['change'])}"
            )
        return "\n".join(rows) if rows else "  없음"

    def nh_rows(lst):
        rows = []
        for s in lst:
            mk  = "Q" if s["market"]=="KOSDAQ" else "K"
            flag= s.get("nh_flag","")
            rows.append(
                f"  • {s['name']}[{mk}]  "
                f"<b>{flag}</b>  "
                f"고가대비 {s.get('nh_ratio',0)}%  {pct(s['change'])}"
            )
        return "\n".join(rows) if rows else "  없음"

    msg4 = (
        f"🔵 <b>[ 외인 연속 순매수 3일↑ ]</b>\n"
        f"{consec_rows(f_consec_list,'f_consec')}\n\n"
        f"🟡 <b>[ 기관 연속 순매수 3일↑ ]</b>\n"
        f"{consec_rows(i_consec_list,'i_consec')}\n\n"
        f"🚀 <b>[ 52주 신고가 근접 ]</b>  ({len(nh_list)}종목)\n"
        f"{nh_rows(nh_list)}\n"
    )
    messages.append(msg4)

    # ── 메시지 5: 섹터 상위/하위 ──────────────────────────
    EXCL = {"0001","1001","0002","0003","0004","0028"}
    sec_filtered = [s for s in sectors if s.get("iscd","") not in EXCL]
    sec_sorted   = sorted(sec_filtered, key=lambda x: x["change"], reverse=True)
    top3_sec  = sec_sorted[:3]
    bot3_sec  = sec_sorted[-3:]

    def sec_rows(lst):
        rows = []
        for s in lst:
            mk = "Q" if s.get("mkt_type")=="KOSDAQ" else "K"
            rows.append(
                f"  • {s['name']}[{mk}]  <b>{pct(s['change'])}</b>"
            )
        return "\n".join(rows) if rows else "  없음"

    msg5 = (
        f"🏭 <b>[ 섹터 등락 ]</b>\n\n"
        f"▲ 상위 섹터\n{sec_rows(top3_sec)}\n\n"
        f"▽ 하위 섹터\n{sec_rows(bot3_sec)}\n\n"
        f"🔗 <a href='https://bjkim-pixel.github.io/market-radar/'>마켓레이더 바로가기</a>"
    )
    messages.append(msg5)

    return messages


# ----------------------------------------
# MAIN
# ----------------------------------------
def main():
    kst_now  = datetime.utcnow() + timedelta(hours=9)
    now_str  = kst_now.strftime("%Y-%m-%d %H:%M")
    kst_date = kst_now.strftime("%Y-%m-%d")

    token = get_token()

    print("\n[1] index...")
    indices = fetch_indices(token)
    time.sleep(0.3)

    print("\n[2] sector...")
    sectors = fetch_all_sectors(token)
    time.sleep(0.3)

    print("\n[3] stocks...")
    stocks = fetch_all_stocks(token)
    time.sleep(0.3)

    market_supply = calc_market_supply(stocks)

    phase_stats = {
        "golden":   sum(1 for s in stocks if s.get("phase_key") == "golden"),
        "p2":       sum(1 for s in stocks if s.get("phase_key") == "p2"),
        "p1":       sum(1 for s in stocks if s.get("phase_key") == "p1"),
        "p3":       sum(1 for s in stocks if s.get("phase_key") == "p3"),
        "new_high": sum(1 for s in stocks if s.get("nh_flag")),
    }

    def top_by(lst, key, n=20, reverse=True):
        return sorted(
            [s for s in lst if s.get(key, 0) != 0],
            key=lambda x: x.get(key, 0), reverse=reverse
        )[:n]

    top_traders = {
        "foreign_buy":  top_by(stocks, "foreign_today", 20, True),
        "foreign_sell": top_by(stocks, "foreign_today", 20, False),
        "inst_buy":     top_by(stocks, "inst_today",    20, True),
        "inst_sell":    top_by(stocks, "inst_today",    20, False),
    }

    summary_lines    = build_summary(indices, stocks, market_supply, phase_stats)
    sector_stock_map = build_sector_stock_map(sectors, stocks)

    payload = clean_nan({
        "updated_at":       now_str,
        "date":             kst_date,
        "indices":          indices,
        "sectors":          sectors,
        "stocks":           stocks,
        "top_traders":      top_traders,
        "market_supply":    market_supply,
        "phase_stats":      phase_stats,
        "summary_lines":    summary_lines,
        "sector_stock_map": sector_stock_map,
    })

    os.makedirs("data", exist_ok=True)
    with open("data/market.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"\ndone: data/market.json")
    print(f"  index:{len(indices)} sector:{len(sectors)} stock:{len(stocks)}")
    print(f"  GOLDEN={phase_stats['golden']} P1={phase_stats['p1']} P3={phase_stats['p3']}")

    # 텔레그램 알림
    tg_token   = os.environ.get("TELEGRAM_TOKEN", "")
    tg_chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if tg_token and tg_chat_id:
        messages = build_telegram_messages(
            indices, sectors, stocks, market_supply, phase_stats, now_str
        )
        for i, msg in enumerate(messages):
            send_telegram(tg_token, tg_chat_id, msg)
            time.sleep(0.5)
        print(f"[telegram] {len(messages)}개 메시지 전송 완료")


if __name__ == "__main__":
    main()
