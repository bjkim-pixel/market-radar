#!/usr/bin/env python3
"""
주식 분석 텔레그램 챗봇
시총 1조 이상 종목 대상
종목명/코드 감지 → 현재가/수급(KIS) + 실적(DART) + 컨센서스(Naver) + 규칙기반 분석
"""

import os, time, requests, re
from datetime import datetime, timedelta

# ── 환경변수 ──────────────────────────────────────────
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
DART_API_KEY   = os.environ.get("DART_API_KEY", "")
KIS_APP_KEY    = os.environ.get("KIS_APP_KEY", "")
KIS_APP_SECRET = os.environ.get("KIS_APP_SECRET", "")

KIS_BASE  = "https://openapi.koreainvestment.com:9443"
DART_BASE = "https://opendart.fss.or.kr/api"
TG_BASE   = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

OFFSET_FILE = "data/bot_offset.txt"

# 트리거 키워드
TRIGGERS = [
    "분석", "실적", "목표주가", "리포트", "수급",
    "어때", "알려줘", "조회", "재무", "전망", "주가",
    "얼마", "어떻게", "봐줘", "분석해", "정보"
]

# ── 시총 1조 이상 종목 목록 ───────────────────────────
MAJOR_STOCKS = [
    # KOSPI
    ("005930", "삼성전자",               "KOSPI"),
    ("000660", "SK하이닉스",             "KOSPI"),
    ("373220", "LG에너지솔루션",         "KOSPI"),
    ("207940", "삼성바이오로직스",       "KOSPI"),
    ("005380", "현대차",                 "KOSPI"),
    ("068270", "셀트리온",               "KOSPI"),
    ("105560", "KB금융",                 "KOSPI"),
    ("000270", "기아",                   "KOSPI"),
    ("005490", "POSCO홀딩스",            "KOSPI"),
    ("055550", "신한지주",               "KOSPI"),
    ("028260", "삼성물산",               "KOSPI"),
    ("012330", "현대모비스",             "KOSPI"),
    ("051910", "LG화학",                 "KOSPI"),
    ("006400", "삼성SDI",                "KOSPI"),
    ("003550", "LG",                     "KOSPI"),
    ("086790", "하나금융지주",           "KOSPI"),
    ("017670", "SK텔레콤",               "KOSPI"),
    ("030200", "KT",                     "KOSPI"),
    ("009150", "삼성전기",               "KOSPI"),
    ("032830", "삼성생명",               "KOSPI"),
    ("066570", "LG전자",                 "KOSPI"),
    ("096770", "SK이노베이션",           "KOSPI"),
    ("010130", "고려아연",               "KOSPI"),
    ("010950", "S-Oil",                  "KOSPI"),
    ("034730", "SK",                     "KOSPI"),
    ("316140", "우리금융지주",           "KOSPI"),
    ("002790", "아모레퍼시픽",           "KOSPI"),
    ("004020", "현대제철",               "KOSPI"),
    ("012450", "한화에어로스페이스",     "KOSPI"),
    ("015760", "한국전력",               "KOSPI"),
    ("033780", "KT&G",                   "KOSPI"),
    ("034020", "두산에너빌리티",         "KOSPI"),
    ("042660", "한화오션",               "KOSPI"),
    ("329180", "현대중공업",             "KOSPI"),
    ("011200", "HMM",                    "KOSPI"),
    ("138040", "메리츠금융지주",         "KOSPI"),
    ("078930", "GS",                     "KOSPI"),
    ("000880", "한화",                   "KOSPI"),
    ("003490", "대한항공",               "KOSPI"),
    ("086280", "현대글로비스",           "KOSPI"),
    ("139480", "이마트",                 "KOSPI"),
    ("097950", "CJ제일제당",             "KOSPI"),
    ("128940", "한미약품",               "KOSPI"),
    ("000100", "유한양행",               "KOSPI"),
    ("185750", "종근당",                 "KOSPI"),
    ("006360", "GS건설",                 "KOSPI"),
    ("010140", "삼성중공업",             "KOSPI"),
    ("047050", "포스코인터내셔널",       "KOSPI"),
    ("064350", "현대로템",               "KOSPI"),
    ("079550", "LIG넥스원",              "KOSPI"),
    ("047810", "한국항공우주",           "KOSPI"),
    ("024110", "기업은행",               "KOSPI"),
    ("011780", "금호석유",               "KOSPI"),
    ("000720", "현대건설",               "KOSPI"),
    ("018260", "삼성에스디에스",         "KOSPI"),
    ("326030", "SK바이오팜",             "KOSPI"),
    ("000120", "CJ대한통운",             "KOSPI"),
    ("011170", "롯데케미칼",             "KOSPI"),
    ("282330", "BGF리테일",              "KOSPI"),
    ("009830", "한화솔루션",             "KOSPI"),
    ("000810", "삼성화재",               "KOSPI"),
    ("032640", "LG유플러스",             "KOSPI"),
    ("036460", "한국가스공사",           "KOSPI"),
    ("021240", "코웨이",                 "KOSPI"),
    ("030000", "제일기획",               "KOSPI"),
    ("002380", "KCC",                    "KOSPI"),
    ("010620", "현대미포조선",           "KOSPI"),
    ("267250", "HD현대",                 "KOSPI"),
    ("004800", "효성",                   "KOSPI"),
    ("035250", "강원랜드",               "KOSPI"),
    ("180640", "한진칼",                 "KOSPI"),
    ("071050", "한국금융지주",           "KOSPI"),
    ("000060", "메리츠화재",             "KOSPI"),
    ("001450", "현대해상",               "KOSPI"),
    ("005945", "NH투자증권",             "KOSPI"),
    ("039490", "키움증권",               "KOSPI"),
    ("006800", "미래에셋증권",           "KOSPI"),
    ("016360", "삼성증권",               "KOSPI"),
    ("001040", "CJ",                     "KOSPI"),
    ("097230", "한진",                   "KOSPI"),
    ("004990", "롯데지주",               "KOSPI"),
    ("023530", "롯데쇼핑",               "KOSPI"),
    ("069960", "현대백화점",             "KOSPI"),
    ("004170", "신세계",                 "KOSPI"),
    ("271560", "오리온",                 "KOSPI"),
    ("003230", "삼양식품",               "KOSPI"),
    ("007310", "오뚜기",                 "KOSPI"),
    ("051600", "한전KPS",                "KOSPI"),
    ("090430", "아모레G",                "KOSPI"),
    ("161390", "한국타이어앤테크놀로지", "KOSPI"),
    ("042670", "HD현대인프라코어",       "KOSPI"),
    ("011790", "SKC",                    "KOSPI"),
    ("003410", "쌍용C&E",                "KOSPI"),
    ("001680", "대상",                   "KOSPI"),
    ("007070", "GS리테일",               "KOSPI"),
    ("010060", "OCI",                    "KOSPI"),
    ("008560", "메리츠증권",             "KOSPI"),
    ("382800", "한화시스템",             "KOSPI"),
    ("000210", "DL",                     "KOSPI"),
    ("008770", "호텔신라",               "KOSPI"),
    ("009540", "HD한국조선해양",         "KOSPI"),
    ("000080", "하이트진로",             "KOSPI"),
    ("307950", "현대오토에버",           "KOSPI"),
    ("014680", "한솔케미칼",             "KOSPI"),
    ("069620", "대웅제약",               "KOSPI"),
    ("018880", "한온시스템",             "KOSPI"),
    ("105630", "한세실업",               "KOSPI"),
    # KOSDAQ
    ("247540", "에코프로비엠",           "KOSDAQ"),
    ("086520", "에코프로",               "KOSDAQ"),
    ("196170", "알테오젠",               "KOSDAQ"),
    ("028300", "HLB",                    "KOSDAQ"),
    ("403870", "HPSP",                   "KOSDAQ"),
    ("141080", "리가켐바이오",           "KOSDAQ"),
    ("145020", "휴젤",                   "KOSDAQ"),
    ("214150", "클래시스",               "KOSDAQ"),
    ("214450", "파마리서치",             "KOSDAQ"),
    ("277810", "레인보우로보틱스",       "KOSDAQ"),
    ("357780", "솔브레인",               "KOSDAQ"),
    ("036830", "솔브레인홀딩스",         "KOSDAQ"),
    ("263750", "펄어비스",               "KOSDAQ"),
    ("293490", "카카오게임즈",           "KOSDAQ"),
    ("035900", "JYP Ent",                "KOSDAQ"),
    ("041510", "에스엠",                 "KOSDAQ"),
    ("352820", "하이브",                 "KOSDAQ"),
    ("122870", "와이지엔터테인먼트",     "KOSDAQ"),
    ("095340", "ISC",                    "KOSDAQ"),
    ("091990", "셀트리온헬스케어",       "KOSDAQ"),
    ("039030", "이오테크닉스",           "KOSDAQ"),
    ("240810", "원익IPS",                "KOSDAQ"),
    ("131970", "두산테스나",             "KOSDAQ"),
    ("348210", "넥스틴",                 "KOSDAQ"),
    ("039200", "오스코텍",               "KOSDAQ"),
    ("067630", "HLB생명과학",            "KOSDAQ"),
    ("048410", "현대바이오",             "KOSDAQ"),
    ("335890", "비올",                   "KOSDAQ"),
    ("237690", "에스티팜",               "KOSDAQ"),
    ("108490", "로보티즈",               "KOSDAQ"),
    ("053800", "안랩",                   "KOSDAQ"),
    ("200780", "티에스이",               "KOSDAQ"),
    ("251970", "펩트론",                 "KOSDAQ"),
    ("066970", "엘앤에프",               "KOSDAQ"),
    ("058470", "리노공업",               "KOSDAQ"),
    ("336570", "원텍",                   "KOSDAQ"),
]

# 종목명 → (코드, 이름) 검색 딕셔너리
STOCK_MAP = {}
for code, name, mkt in MAJOR_STOCKS:
    STOCK_MAP[name.lower().replace(" ", "")] = (code, name)

# 별칭 추가
ALIASES = {
    "삼전":       "005930", "반도체대장": "005930",
    "하이닉스":   "000660", "sk하이":    "000660",
    "현대자동차": "005380", "현차":      "005380",
    "포스코":     "005490", "신한":      "055550",
    "하나":       "086790", "skt":       "017670",
    "한전":       "015760", "에쓰오일":  "010950",
    "삼성바이오": "207940", "삼성sds":   "018260",
    "lg엔솔":     "373220", "카항":      "047810",
    "한화에어로": "012450", "레인보우":  "277810",
    "jyp":        "035900", "sm":        "041510",
    "yg":         "122870", "에코비엠":  "247540",
}
for alias, code in ALIASES.items():
    matched = next((n for c, n, _ in MAJOR_STOCKS if c == code), None)
    if matched:
        STOCK_MAP[alias.lower()] = (code, matched)


# ═══════════════════════════════════════
# 텔레그램
# ═══════════════════════════════════════

def tg_get_updates(offset=None):
    params = {"timeout": 5, "allowed_updates": ["message"]}
    if offset:
        params["offset"] = offset
    try:
        r = requests.get(f"{TG_BASE}/getUpdates", params=params, timeout=15)
        return r.json().get("result", [])
    except:
        return []


def tg_send(chat_id, text, parse_mode="HTML"):
    try:
        r = requests.post(
            f"{TG_BASE}/sendMessage",
            json={
                "chat_id":                  chat_id,
                "text":                     text,
                "parse_mode":               parse_mode,
                "disable_web_page_preview": True,
            },
            timeout=15
        )
        if not r.ok:
            print(f"[tg_send] 오류: {r.text[:100]}")
    except Exception as e:
        print(f"[tg_send] 실패: {e}")


def tg_typing(chat_id):
    try:
        requests.post(
            f"{TG_BASE}/sendChatAction",
            json={"chat_id": chat_id, "action": "typing"},
            timeout=5
        )
    except:
        pass


def load_offset():
    try:
        with open(OFFSET_FILE, "r") as f:
            return int(f.read().strip())
    except:
        return None


def save_offset(offset):
    os.makedirs("data", exist_ok=True)
    with open(OFFSET_FILE, "w") as f:
        f.write(str(offset))


# ═══════════════════════════════════════
# 종목 감지
# ═══════════════════════════════════════

def detect_stock(text):
    if not text:
        return None

    text_raw   = text.strip()
    text_lower = text_raw.lower().replace(" ", "")

    # /분석 005930  또는  /분석 삼성전자 명령어
    cmd_match = re.match(r'^/(분석|종목|주가|조회)\s*(.+)', text_raw)
    if cmd_match:
        query = cmd_match.group(2).strip().lower().replace(" ", "")
        if re.match(r'^\d{6}$', query):
            matched = next(((c, n) for c, n, _ in MAJOR_STOCKS if c == query), None)
            return matched
        if query in STOCK_MAP:
            return STOCK_MAP[query]
        return None

    # 트리거 키워드 확인
    has_trigger = any(t in text_raw for t in TRIGGERS)
    if not has_trigger:
        return None

    # 6자리 숫자 코드
    code_match = re.search(r'\b(\d{6})\b', text_raw)
    if code_match:
        code    = code_match.group(1)
        matched = next(((c, n) for c, n, _ in MAJOR_STOCKS if c == code), None)
        if matched:
            return matched

    # 종목명 매칭 (긴 이름 우선)
    sorted_map = sorted(STOCK_MAP.items(), key=lambda x: len(x[0]), reverse=True)
    for key, (code, name) in sorted_map:
        if key in text_lower:
            return (code, name)

    return None


# ═══════════════════════════════════════
# KIS API
# ═══════════════════════════════════════

def get_kis_token():
    try:
        r = requests.post(f"{KIS_BASE}/oauth2/tokenP", json={
            "grant_type": "client_credentials",
            "appkey":     KIS_APP_KEY,
            "appsecret":  KIS_APP_SECRET,
        }, timeout=10)
        return r.json().get("access_token", "")
    except:
        return ""


def kis_get(path, params, tr_id, token):
    headers = {
        "Content-Type":  "application/json",
        "authorization": f"Bearer {token}",
        "appkey":        KIS_APP_KEY,
        "appsecret":     KIS_APP_SECRET,
        "tr_id":         tr_id,
        "custtype":      "P",
    }
    try:
        r = requests.get(f"{KIS_BASE}{path}", headers=headers,
                         params=params, timeout=15)
        d = r.json()
        if d.get("rt_cd") == "0":
            return d
    except:
        pass
    return {}


def sf(v):
    try:    return float(str(v).replace(",", ""))
    except: return 0.0

def si(v):
    try:    return int(float(str(v).replace(",", "")))
    except: return 0


def fetch_price_supply(code, token):
    result = {}

    # 현재가
    d = kis_get(
        "/uapi/domestic-stock/v1/quotations/inquire-price",
        {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": code},
        "FHKST01010100", token
    )
    o = d.get("output", {})
    if o:
        price  = si(o.get("stck_prpr", 0))
        high52 = si(o.get("d250_hgpr", 0))
        low52  = si(o.get("d250_lwpr", 0))
        mktcap = sf(o.get("hts_avls", 0))
        result.update({
            "price":    price,
            "change":   sf(o.get("prdy_ctrt", 0)),
            "diff":     si(o.get("prdy_vrss", 0)),
            "volume":   si(o.get("acml_vol", 0)),
            "tr_val":   si(o.get("acml_tr_pbmn", 0)),
            "high52":   high52,
            "low52":    low52,
            "per":      sf(o.get("per", 0)),
            "pbr":      sf(o.get("pbr", 0)),
            "mktcap":   mktcap,
            "sector":   o.get("bstp_kor_isnm", "").strip(),
            "nh_ratio": round(price / high52 * 100, 1) if high52 else 0,
        })
    time.sleep(0.1)

    # 수급 (최근 10일)
    d2   = kis_get(
        "/uapi/domestic-stock/v1/quotations/inquire-investor",
        {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": code},
        "FHKST01010900", token
    )
    rows = d2.get("output", [])[:10]
    if rows:
        f_today = sf(rows[0].get("frgn_ntby_tr_pbmn", 0)) * 1e6
        i_today = sf(rows[0].get("orgn_ntby_tr_pbmn", 0)) * 1e6
        p_today = sf(rows[0].get("prsn_ntby_tr_pbmn", 0)) * 1e6
        f5  = sum(sf(r.get("frgn_ntby_tr_pbmn", 0)) for r in rows[:5]) * 1e6
        i5  = sum(sf(r.get("orgn_ntby_tr_pbmn", 0)) for r in rows[:5]) * 1e6
        f10 = sum(sf(r.get("frgn_ntby_tr_pbmn", 0)) for r in rows)     * 1e6
        i10 = sum(sf(r.get("orgn_ntby_tr_pbmn", 0)) for r in rows)     * 1e6

        f_consec = i_consec = 0
        for row in rows:
            if si(row.get("frgn_ntby_qty", 0)) > 0: f_consec += 1
            else: break
        for row in rows:
            if si(row.get("orgn_ntby_qty", 0)) > 0: i_consec += 1
            else: break

        mktcap_won = result.get("mktcap", 0) * 1e8
        magic = round((f_today + i_today) / mktcap_won * 100, 4) if mktcap_won else 0

        result.update({
            "today_foreign": f_today,
            "today_inst":    i_today,
            "today_indiv":   p_today,
            "foreign_5d":    f5,
            "inst_5d":       i5,
            "foreign_10d":   f10,
            "inst_10d":      i10,
            "f_consec":      f_consec,
            "i_consec":      i_consec,
            "magic":         magic,
        })

    return result


# ═══════════════════════════════════════
# DART
# ═══════════════════════════════════════

def get_dart_corp_code(stock_code):
    try:
        r = requests.get(
            f"{DART_BASE}/company.json",
            params={"crtfc_key": DART_API_KEY, "stock_code": stock_code},
            timeout=10
        )
        d = r.json()
        if d.get("status") == "000":
            return d.get("corp_code", "")
    except:
        pass
    return ""


def fetch_dart_financial(corp_code):
    results  = {}
    kst_year = (datetime.utcnow() + timedelta(hours=9)).year

    for year in [kst_year - 1, kst_year - 2]:
        try:
            r = requests.get(
                f"{DART_BASE}/fnlttSinglAcnt.json",
                params={
                    "crtfc_key":  DART_API_KEY,
                    "corp_code":  corp_code,
                    "bsns_year":  str(year),
                    "reprt_code": "11011",
                    "fs_div":     "CFS",
                },
                timeout=15
            )
            d = r.json()
            if d.get("status") == "000":
                annual = {}
                for item in d.get("list", []):
                    acnt = item.get("account_nm", "")
                    val  = item.get("thstrm_amount", "").replace(",", "")
                    if "매출액" in acnt and "영업" not in acnt and not annual.get("revenue"):
                        try: annual["revenue"] = int(val)
                        except: pass
                    if "영업이익" in acnt and "손실" not in acnt and not annual.get("op_income"):
                        try: annual["op_income"] = int(val)
                        except: pass
                    if "당기순이익" in acnt and not annual.get("net_income"):
                        try: annual["net_income"] = int(val)
                        except: pass
                if annual:
                    results[f"{year}년"] = annual
        except:
            pass
        time.sleep(0.15)

    # 최근 분기
    for reprt_code, label in [("11014", "Q3"), ("11012", "Q2"), ("11013", "Q1")]:
        try:
            r = requests.get(
                f"{DART_BASE}/fnlttSinglAcnt.json",
                params={
                    "crtfc_key":  DART_API_KEY,
                    "corp_code":  corp_code,
                    "bsns_year":  str(kst_year),
                    "reprt_code": reprt_code,
                    "fs_div":     "CFS",
                },
                timeout=15
            )
            d = r.json()
            if d.get("status") == "000":
                qtr = {}
                for item in d.get("list", []):
                    acnt = item.get("account_nm", "")
                    val  = item.get("thstrm_amount", "").replace(",", "")
                    if "매출액" in acnt and "영업" not in acnt and not qtr.get("revenue"):
                        try: qtr["revenue"] = int(val)
                        except: pass
                    if "영업이익" in acnt and "손실" not in acnt and not qtr.get("op_income"):
                        try: qtr["op_income"] = int(val)
                        except: pass
                if qtr:
                    results[f"{kst_year} {label}"] = qtr
                    break
        except:
            pass
        time.sleep(0.15)

    return results


# ═══════════════════════════════════════
# 컨센서스
# ═══════════════════════════════════════

def fetch_consensus(code):
    try:
        url = f"https://m.stock.naver.com/api/stock/{code}/investmentOpinion"
        r   = requests.get(url, timeout=10,
                           headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            d     = r.json()
            items = d if isinstance(d, list) else d.get("items", [])
            if items:
                prices    = [i.get("targetPrice", 0) for i in items if i.get("targetPrice", 0) > 0]
                opinions  = [str(i.get("opinion", "")) for i in items]
                buy_cnt   = sum(1 for o in opinions
                                if "매수" in o or "BUY" in o.upper() or "Outperform" in o)
                avg_tp    = int(sum(prices) / len(prices)) if prices else 0
                recent    = []
                for i in items[:3]:
                    firm = i.get("firm", "")
                    tp   = i.get("targetPrice", 0)
                    op   = i.get("opinion", "")
                    date = i.get("date", "")[:10] if i.get("date") else ""
                    if firm:
                        recent.append(f"{firm} {op} {tp:,}원 ({date})")
                return {
                    "avg_target": avg_tp,
                    "buy_count":  buy_cnt,
                    "total":      len(items),
                    "buy_ratio":  round(buy_cnt / len(items) * 100) if items else 0,
                    "recent":     recent,
                }
    except:
        pass
    return {}


# ═══════════════════════════════════════
# 규칙 기반 자동 분석 (무료)
# ═══════════════════════════════════════

def rule_based_analysis(price_data, financial, consensus):
    comments = []
    price    = price_data.get("price", 0)
    high52   = price_data.get("high52", 0)
    low52    = price_data.get("low52", 0)
    f_consec = price_data.get("f_consec", 0)
    i_consec = price_data.get("i_consec", 0)
    f5       = price_data.get("foreign_5d", 0)
    i5       = price_data.get("inst_5d", 0)
    per      = price_data.get("per", 0)
    pbr      = price_data.get("pbr", 0)
    change   = price_data.get("change", 0)
    magic    = price_data.get("magic", 0)
    avg_tp   = consensus.get("avg_target", 0)
    buy_cnt  = consensus.get("buy_count", 0)
    total_op = consensus.get("total", 1) or 1

    # 수급
    if f_consec >= 5 and i_consec >= 3:
        comments.append(f"🔥 외인 {f_consec}일 + 기관 {i_consec}일 동반 순매수 → 강한 매집 신호")
    elif f_consec >= 5:
        comments.append(f"🔵 외국인 {f_consec}일 연속 순매수 → 외인 주도 상승 가능성")
    elif f_consec >= 3:
        comments.append(f"🔵 외국인 {f_consec}일 연속 순매수 → 매집 초기 단계")
    elif f_consec >= 2:
        comments.append(f"🔵 외국인 {f_consec}일 연속 순매수 → 추이 주목")

    if i_consec >= 5:
        comments.append(f"🟡 기관 {i_consec}일 연속 순매수 → 기관 주도 매집")
    elif i_consec >= 3 and f_consec < 2:
        comments.append(f"🟡 기관 {i_consec}일 연속 순매수")

    if f5 < 0 and i5 < 0:
        comments.append("🔴 외인·기관 동반 5일 순매도 → 단기 수급 부담")

    # 매직지수
    if magic >= 0.05:
        comments.append(f"⭐ 매직지수 {magic:+.4f}% → GOLDEN 수준 매집 강도")
    elif magic >= 0.01:
        comments.append(f"✅ 매직지수 {magic:+.4f}% → 양호한 수급")
    elif magic <= -0.05:
        comments.append(f"🔴 매직지수 {magic:+.4f}% → 이탈 신호 주의")

    # 52주 고저
    if high52 > 0:
        nh = price / high52 * 100
        nl = price / low52  * 100 if low52 else 0
        if nh >= 100:
            comments.append("🚀 52주 신고가 돌파 → 강한 상승 모멘텀")
        elif nh >= 99:
            comments.append(f"📍 52주 신고가 근접 ({nh:.1f}%) → 돌파 시 추가 상승 기대")
        elif nh >= 97:
            comments.append(f"📍 신고가 {nh:.1f}% 수준 → 모멘텀 확인 구간")
        if nl <= 105:
            comments.append(f"📉 52주 저가 근접 ({nl:.1f}%) → 하방 리스크 주의")

    # 밸류에이션
    if 0 < per <= 8:
        comments.append(f"💎 PER {per:.1f}배 → 저평가 구간")
    elif 8 < per <= 15:
        comments.append(f"✅ PER {per:.1f}배 → 적정 밸류에이션")
    elif per > 40:
        comments.append(f"⚠️ PER {per:.1f}배 → 고평가 부담")

    if 0 < pbr <= 0.7:
        comments.append(f"💎 PBR {pbr:.2f}배 → 자산가치 대비 저평가")

    # 실적 트렌드
    if financial:
        years = list(financial.keys())
        if len(years) >= 2:
            curr = financial[years[0]].get("op_income", 0)
            prev = financial[years[1]].get("op_income", 0)
            if prev and curr:
                growth = (curr - prev) / abs(prev) * 100
                if prev < 0 and curr > 0:
                    comments.append("📈 영업이익 흑자 전환 → 실적 턴어라운드")
                elif growth >= 100:
                    comments.append(f"📈 영업이익 {growth:.0f}% 급증 → 강한 실적 모멘텀")
                elif growth >= 20:
                    comments.append(f"📈 영업이익 {growth:.0f}% 증가 → 실적 개선세")
                elif growth <= -50:
                    comments.append(f"📉 영업이익 {growth:.0f}% 급감 → 실적 부진 주의")

    # 컨센서스
    if avg_tp > 0 and price > 0:
        upside    = (avg_tp - price) / price * 100
        buy_ratio = buy_cnt / total_op * 100
        if upside >= 30 and buy_ratio >= 80:
            comments.append(f"🏦 상승여력 {upside:.0f}% + 매수의견 {buy_ratio:.0f}% → 증권사 강력 추천")
        elif upside >= 15:
            comments.append(f"🏦 목표주가 대비 상승여력 {upside:.0f}% → 긍정적 시각")
        elif upside < -5:
            comments.append(f"🏦 현재가 목표주가 상회 ({abs(upside):.0f}%) → 차익 실현 유의")

    if not comments:
        if change >= 3:
            comments.append("📈 강한 상승세, 거래량과 수급 동향 확인 권장")
        elif change <= -3:
            comments.append("📉 큰 폭 하락, 지지선 및 수급 확인 필요")
        else:
            comments.append("➡️ 특이 시그널 없음, 추이 관찰 필요")

    return "\n".join(f"  {c}" for c in comments)


# ═══════════════════════════════════════
# 리포트 생성
# ═══════════════════════════════════════

def fmt_won(v):
    if v == 0: return "-"
    neg = v < 0
    a   = abs(v)
    if a >= 1e12:  s = f"{a/1e12:.1f}조"
    elif a >= 1e8: s = f"{a/1e8:.0f}억"
    elif a >= 1e4: s = f"{a/1e4:.0f}만"
    else:          s = f"{a:,.0f}"
    return ("-" if neg else "+") + s


def build_report(name, code, mkt, price_data, financial, consensus, analysis):
    price    = price_data.get("price", 0)
    change   = price_data.get("change", 0)
    diff     = price_data.get("diff", 0)
    high52   = price_data.get("high52", 0)
    low52    = price_data.get("low52", 0)
    nh_ratio = price_data.get("nh_ratio", 0)
    mktcap   = price_data.get("mktcap", 0)
    per      = price_data.get("per", 0)
    pbr      = price_data.get("pbr", 0)
    sector   = price_data.get("sector", "-")
    volume   = price_data.get("volume", 0)
    magic    = price_data.get("magic", 0)
    f_today  = price_data.get("today_foreign", 0)
    i_today  = price_data.get("today_inst", 0)
    p_today  = price_data.get("today_indiv", 0)
    f5       = price_data.get("foreign_5d", 0)
    i5       = price_data.get("inst_5d", 0)
    f_consec = price_data.get("f_consec", 0)
    i_consec = price_data.get("i_consec", 0)

    arr    = "📈" if change >= 0 else "📉"
    sign   = "+" if change >= 0 else ""
    mk_tag = "KOSDAQ" if mkt == "KOSDAQ" else "KOSPI"

    lines = [
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"📊 <b>{name}</b>  <code>{code}</code>  [{mk_tag}]",
        f"<i>{sector}</i>",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"",
        f"💵 <b>현재가</b>",
        f"  <b>{price:,}원</b>  {arr} <b>{sign}{change:.2f}%</b>  ({'+' if diff>=0 else ''}{diff:,}원)",
        f"  시총 {fmt_won(mktcap*1e8)}  ·  거래량 {volume:,}",
        f"  PER <b>{per:.1f}배</b>  ·  PBR <b>{pbr:.2f}배</b>",
        f"  52주 고가 {high52:,}원 ({nh_ratio}%)  ·  저가 {low52:,}원",
        f"",
        f"💰 <b>투자자 수급</b>",
        f"  구분      오늘           5일",
        f"  외국인  {fmt_won(f_today):>8}  /  {fmt_won(f5)}",
        f"  기관    {fmt_won(i_today):>8}  /  {fmt_won(i5)}",
        f"  개인    {fmt_won(p_today):>8}",
    ]

    if f_consec >= 2:
        lines.append(f"  🔵 외국인 <b>{f_consec}일 연속</b> 순매수")
    if i_consec >= 2:
        lines.append(f"  🟡 기관 <b>{i_consec}일 연속</b> 순매수")

    lines.append(f"  매직지수  <b>{magic:+.4f}%</b>")
    lines.append("")

    # 실적
    if financial:
        lines.append("📋 <b>실적 현황 (DART)</b>")
        for period, data in list(financial.items())[:3]:
            rev = data.get("revenue", 0)
            op  = data.get("op_income", 0)
            net = data.get("net_income", 0)
            if rev or op:
                lines.append(
                    f"  {period}  매출 {fmt_won(rev)}  영업익 {fmt_won(op)}"
                    + (f"  순익 {fmt_won(net)}" if net else "")
                )
        lines.append("")

    # 컨센서스
    avg_tp   = consensus.get("avg_target", 0)
    buy_cnt  = consensus.get("buy_count", 0)
    total_op = consensus.get("total", 0)
    recent   = consensus.get("recent", [])
    if avg_tp > 0:
        upside = round((avg_tp - price) / price * 100, 1) if price else 0
        lines.append("🏦 <b>증권사 컨센서스</b>")
        lines.append(
            f"  목표주가 <b>{avg_tp:,}원</b>  "
            f"(현재가 대비 <b>{upside:+.1f}%</b>)"
        )
        if total_op:
            lines.append(f"  매수의견 <b>{buy_cnt}/{total_op}개</b>")
        for r in recent[:2]:
            lines.append(f"  · {r}")
        lines.append("")

    # 자동 분석
    lines.append("🔍 <b>자동 분석</b>")
    lines.append(analysis)
    lines.append("")

    kst_now = datetime.utcnow() + timedelta(hours=9)
    lines.append(
        f"<i>🕐 {kst_now.strftime('%Y-%m-%d %H:%M')} KST  "
        f"· 투자 참고용, 본인 판단으로</i>"
    )

    # 빈 줄 중복 제거
    result, prev_empty = [], False
    for line in lines:
        if line == "":
            if not prev_empty:
                result.append(line)
            prev_empty = True
        else:
            result.append(line)
            prev_empty = False

    return "\n".join(result)


# ═══════════════════════════════════════
# 도움말
# ═══════════════════════════════════════

HELP_TEXT = """
📡 <b>마켓레이더 주식봇 사용법</b>

<b>[ 명령어 ]</b>
/분석 삼성전자    → 종목명으로 분석
/분석 005930     → 종목코드로 분석
/도움말           → 이 메시지

<b>[ 자연어 ]</b>
삼성전자 분석해줘
SK하이닉스 실적 어때?
현대차 목표주가 알려줘
005930 수급 조회
에코프로 전망이 어때?

<b>[ 분석 내용 ]</b>
• 현재가 · 등락률 · 시총 · PER/PBR
• 외인/기관/개인 수급 (오늘·5일)
• 매직지수 (외인+기관 / 시총)
• 연속 순매수 일수
• DART 실적 (매출·영업익·순익)
• 증권사 컨센서스 (목표주가·매수의견)
• 규칙 기반 자동 분석 코멘트

<b>[ 조회 가능 종목 ]</b>
시총 1조원 이상 KOSPI/KOSDAQ 148개

⚠️ 투자 참고용 · 본인 판단으로 결정하세요
"""


# ═══════════════════════════════════════
# 메시지 처리
# ═══════════════════════════════════════

def process_message(chat_id, text, user_name):
    text_raw = text.strip()

    # 도움말
    if text_raw in ["/start", "/도움말", "/help", "/봇", "/사용법"]:
        tg_send(chat_id, HELP_TEXT)
        return

    detected = detect_stock(text_raw)
    if not detected:
        return

    code, name = detected
    mkt = next((m for c, n, m in MAJOR_STOCKS if c == code), "KOSPI")

    print(f"  [{user_name}] '{text_raw[:30]}' → {name}({code}) 분석 시작")

    tg_typing(chat_id)
    tg_send(chat_id,
            f"🔍 <b>{name}</b> ({code}) 분석 중...\n"
            f"현재가·수급·실적·컨센서스 수집 중입니다 ⏳")

    # 데이터 수집
    tg_typing(chat_id)
    kis_token  = get_kis_token()
    price_data = fetch_price_supply(code, kis_token) if kis_token else {}

    tg_typing(chat_id)
    corp_code = get_dart_corp_code(code)
    financial = fetch_dart_financial(corp_code) if corp_code else {}

    tg_typing(chat_id)
    consensus = fetch_consensus(code)

    if not price_data:
        tg_send(chat_id,
                f"⚠️ {name} 데이터를 가져오지 못했습니다.\n"
                f"잠시 후 다시 시도해주세요.")
        return

    analysis = rule_based_analysis(price_data, financial, consensus)
    report   = build_report(name, code, mkt, price_data, financial, consensus, analysis)
    tg_send(chat_id, report)
    print(f"  [{name}] 리포트 전송 완료")


# ═══════════════════════════════════════
# MAIN
# ═══════════════════════════════════════

def main():
    if not TELEGRAM_TOKEN:
        print("[ERROR] TELEGRAM_TOKEN 없음")
        return

    offset = load_offset()
    print(f"[stock_bot] 시작 | offset={offset}")

    updates = tg_get_updates(offset)
    if not updates:
        print("[stock_bot] 새 메시지 없음")
        return

    new_offset = offset or 0
    for upd in updates:
        upd_id     = upd.get("update_id", 0)
        new_offset = max(new_offset, upd_id + 1)

        msg     = upd.get("message", {})
        chat_id = str(msg.get("chat", {}).get("id", ""))
        text    = msg.get("text", "")
        user    = msg.get("from", {}).get("first_name", "unknown")

        if chat_id and text:
            try:
                process_message(chat_id, text, user)
            except Exception as e:
                print(f"  [오류] {e}")
                tg_send(chat_id, f"⚠️ 처리 중 오류: {e}")

    save_offset(new_offset)
    print(f"[stock_bot] 완료 | offset={new_offset} | 처리={len(updates)}건")


if __name__ == "__main__":
    main()