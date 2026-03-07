#!/usr/bin/env python3
"""
멀티 에이전트 주식 추천 시스템 v3
변경사항:
- 합병/상장폐지 7개 종목 제거
- 수급 분석: 시총 1조 미만 필터링 + 5조↑ 참고 TOP10 추가
- 펀더멘털: 25년 연간 + 26년 분기 실적 표시
- 컨센서스 에이전트 제거 (수집 실패로 삭제)
- 추천 스코어: 수급 + 펀더 2개 기준으로 변경
- 마지막 메시지에 인사말 추가
"""

import os, time, requests, re
from datetime import datetime, timedelta

# ── 환경변수 ──────────────────────────────────────────
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
DART_API_KEY   = os.environ.get("DART_API_KEY", "")
KIS_APP_KEY    = os.environ.get("KIS_APP_KEY", "")
KIS_APP_SECRET = os.environ.get("KIS_APP_SECRET", "")

KIS_BASE      = "https://openapi.koreainvestment.com:9443"
DART_BASE     = "https://opendart.fss.or.kr/api"
TG_BASE       = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
GROUP_CHAT_ID = "-5233725507"

# ── 에이전트 페르소나 ─────────────────────────────────
AGENTS = {
    "orchestrator": {"name": "🎯 오케스트레이터", "desc": "분석 총괄 · 에이전트 조율"},
    "collector":    {"name": "📡 수집 에이전트",  "desc": "KIS API 데이터 수집 담당"},
    "supply":       {"name": "🔬 수급 분석 에이전트", "desc": "외인/기관 수급 흐름 전문"},
    "fundamental":  {"name": "📊 펀더멘털 에이전트", "desc": "실적/밸류에이션 전문 (DART)"},
    "recommender":  {"name": "⭐ 추천 에이전트",   "desc": "종합 스코어링 및 최종 추천"},
}

# ── 종목 목록 (합병/상장폐지 7개 제거) ───────────────
# 제거: 현대미포조선(010620), 메리츠화재(000060), HD현대인프라코어(042670),
#       쌍용C&E(003410), 메리츠증권(008560), 셀트리온헬스케어(091990), 비올(335890)
MAJOR_STOCKS = [
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
    ("267250","HD현대","KOSPI"),
    ("004800","효성","KOSPI"),
    ("035250","강원랜드","KOSPI"),
    ("180640","한진칼","KOSPI"),
    ("071050","한국금융지주","KOSPI"),
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
    ("011790","SKC","KOSPI"),
    ("001680","대상","KOSPI"),
    ("007070","GS리테일","KOSPI"),
    ("010060","OCI","KOSPI"),
    ("382800","한화시스템","KOSPI"),
    ("000210","DL","KOSPI"),
    ("008770","호텔신라","KOSPI"),
    ("009540","HD한국조선해양","KOSPI"),
    ("000080","하이트진로","KOSPI"),
    ("307950","현대오토에버","KOSPI"),
    ("014680","한솔케미칼","KOSPI"),
    ("069620","대웅제약","KOSPI"),
    ("018880","한온시스템","KOSPI"),
    ("105630","한세실업","KOSPI"),
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
    ("039030","이오테크닉스","KOSDAQ"),
    ("240810","원익IPS","KOSDAQ"),
    ("131970","두산테스나","KOSDAQ"),
    ("348210","넥스틴","KOSDAQ"),
    ("039200","오스코텍","KOSDAQ"),
    ("067630","HLB생명과학","KOSDAQ"),
    ("048410","현대바이오","KOSDAQ"),
    ("237690","에스티팜","KOSDAQ"),
    ("108490","로보티즈","KOSDAQ"),
    ("053800","안랩","KOSDAQ"),
    ("200780","티에스이","KOSDAQ"),
    ("251970","펩트론","KOSDAQ"),
    ("066970","엘앤에프","KOSDAQ"),
    ("058470","리노공업","KOSDAQ"),
    ("336570","원텍","KOSDAQ"),
]

MKTCAP_1T  = 10000   # 1조 (억원 단위)
MKTCAP_5T  = 50000   # 5조


# ═══════════════════════════════════════
# 유틸
# ═══════════════════════════════════════

def first_reason(reasons, default="데이터 없음"):
    return reasons[0] if reasons else default

def fmt_won(v):
    if v == 0: return "0"
    neg = v < 0; a = abs(v)
    if a >= 1e12:  s = f"{a/1e12:.1f}조"
    elif a >= 1e8: s = f"{a/1e8:.0f}억"
    elif a >= 1e4: s = f"{a/1e4:.0f}만"
    else:          s = f"{a:,.0f}"
    return ("-" if neg else "+") + s

def sf(v):
    try:    return float(str(v).replace(",", ""))
    except: return 0.0

def si(v):
    try:    return int(float(str(v).replace(",", "")))
    except: return 0


# ═══════════════════════════════════════
# 텔레그램
# ═══════════════════════════════════════

def agent_say(agent_key, message, delay=1.5):
    agent  = AGENTS[agent_key]
    header = f"<b>{agent['name']}</b>\n<i>{agent['desc']}</i>\n{'─'*22}\n"
    try:
        requests.post(f"{TG_BASE}/sendMessage", json={
            "chat_id":                  GROUP_CHAT_ID,
            "text":                     header + message,
            "parse_mode":               "HTML",
            "disable_web_page_preview": True,
        }, timeout=15)
    except Exception as e:
        print(f"[tg] {e}")
    time.sleep(delay)

def agent_typing(delay=1.5):
    try:
        requests.post(f"{TG_BASE}/sendChatAction",
                      json={"chat_id": GROUP_CHAT_ID, "action": "typing"}, timeout=5)
    except: pass
    time.sleep(delay)


# ═══════════════════════════════════════
# KIS API
# ═══════════════════════════════════════

def get_kis_token():
    try:
        r = requests.post(f"{KIS_BASE}/oauth2/tokenP", json={
            "grant_type": "client_credentials",
            "appkey": KIS_APP_KEY, "appsecret": KIS_APP_SECRET,
        }, timeout=10)
        return r.json().get("access_token", "")
    except: return ""

def kis_get(path, params, tr_id, token):
    headers = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {token}",
        "appkey": KIS_APP_KEY, "appsecret": KIS_APP_SECRET,
        "tr_id": tr_id, "custtype": "P",
    }
    try:
        r = requests.get(f"{KIS_BASE}{path}", headers=headers,
                         params=params, timeout=15)
        d = r.json()
        if d.get("rt_cd") == "0": return d
    except: pass
    return {}

def fetch_stock_data(code, token):
    result = {"code": code}
    d = kis_get("/uapi/domestic-stock/v1/quotations/inquire-price",
                {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": code},
                "FHKST01010100", token)
    o = d.get("output", {})
    if not o: return None
    price  = si(o.get("stck_prpr", 0))
    high52 = si(o.get("d250_hgpr", 0))
    mktcap = sf(o.get("hts_avls", 0))
    if not price: return None
    result.update({
        "price":    price,
        "change":   sf(o.get("prdy_ctrt", 0)),
        "high52":   high52,
        "low52":    si(o.get("d250_lwpr", 0)),
        "per":      sf(o.get("per", 0)),
        "pbr":      sf(o.get("pbr", 0)),
        "mktcap":   mktcap,
        "sector":   o.get("bstp_kor_isnm", "").strip(),
        "nh_ratio": round(price / high52 * 100, 1) if high52 else 0,
        "volume":   si(o.get("acml_vol", 0)),
    })
    time.sleep(0.07)

    d2   = kis_get("/uapi/domestic-stock/v1/quotations/inquire-investor",
                   {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": code},
                   "FHKST01010900", token)
    rows = d2.get("output", [])[:10]
    if rows:
        f_today = sf(rows[0].get("frgn_ntby_tr_pbmn", 0)) * 1e6
        i_today = sf(rows[0].get("orgn_ntby_tr_pbmn", 0)) * 1e6
        f5  = sum(sf(r.get("frgn_ntby_tr_pbmn", 0)) for r in rows[:5]) * 1e6
        i5  = sum(sf(r.get("orgn_ntby_tr_pbmn", 0)) for r in rows[:5]) * 1e6
        f10 = sum(sf(r.get("frgn_ntby_tr_pbmn", 0)) for r in rows) * 1e6
        i10 = sum(sf(r.get("orgn_ntby_tr_pbmn", 0)) for r in rows) * 1e6
        f_consec = i_consec = 0
        for row in rows:
            if si(row.get("frgn_ntby_qty", 0)) > 0: f_consec += 1
            else: break
        for row in rows:
            if si(row.get("orgn_ntby_qty", 0)) > 0: i_consec += 1
            else: break
        mktcap_won = mktcap * 1e8
        magic = round((f_today + i_today) / mktcap_won * 100, 4) if mktcap_won else 0
        result.update({
            "f_today": f_today, "i_today": i_today,
            "f5": f5, "i5": i5, "f10": f10, "i10": i10,
            "f_consec": f_consec, "i_consec": i_consec, "magic": magic,
        })
    time.sleep(0.07)
    return result


# ═══════════════════════════════════════
# DART (25년 연간 + 26년 분기)
# ═══════════════════════════════════════

def get_corp_code(stock_code):
    try:
        r = requests.get(f"{DART_BASE}/company.json",
                         params={"crtfc_key": DART_API_KEY, "stock_code": stock_code},
                         timeout=10)
        d = r.json()
        if d.get("status") == "000": return d.get("corp_code", "")
    except: pass
    return ""

def parse_financial_items(item_list):
    """재무제표 항목 리스트에서 매출/영업이익/순이익 추출"""
    result = {}
    for item in item_list:
        acnt = item.get("account_nm", "")
        val  = item.get("thstrm_amount", "").replace(",", "")
        if "매출액" in acnt and "영업" not in acnt and not result.get("rev"):
            try: result["rev"] = int(val)
            except: pass
        if "영업이익" in acnt and "손실" not in acnt and not result.get("op"):
            try: result["op"] = int(val)
            except: pass
        if "당기순이익" in acnt and not result.get("net"):
            try: result["net"] = int(val)
            except: pass
    if result.get("rev") and result.get("op"):
        result["op_margin"] = round(result["op"] / result["rev"] * 100, 1)
    return result

def fetch_dart_full(corp_code):
    """
    25년 연간 실적 + 26년 발표된 최근 분기 실적
    반환: {
        "annual_2025": {rev, op, net, op_margin},
        "annual_2024": {rev, op, net, op_margin},
        "quarter_2026": {"label": "26년 Q1", rev, op, op_margin}  # 있으면
    }
    """
    data     = {}
    kst_year = (datetime.utcnow() + timedelta(hours=9)).year  # 2026

    # 연간: 25년, 24년
    for year in [kst_year - 1, kst_year - 2]:
        try:
            r = requests.get(f"{DART_BASE}/fnlttSinglAcnt.json", params={
                "crtfc_key": DART_API_KEY, "corp_code": corp_code,
                "bsns_year": str(year), "reprt_code": "11011", "fs_div": "CFS",
            }, timeout=15)
            d = r.json()
            if d.get("status") == "000":
                parsed = parse_financial_items(d.get("list", []))
                if parsed:
                    data[f"annual_{year}"] = parsed
        except: pass
        time.sleep(0.2)

    # 26년 분기: Q1(11013) → Q2(11012) → Q3(11014) 순서로 있는 것 가져오기
    quarter_map = {"11013": "Q1", "11012": "Q2", "11014": "Q3"}
    for reprt_code, label in quarter_map.items():
        try:
            r = requests.get(f"{DART_BASE}/fnlttSinglAcnt.json", params={
                "crtfc_key": DART_API_KEY, "corp_code": corp_code,
                "bsns_year": str(kst_year), "reprt_code": reprt_code, "fs_div": "CFS",
            }, timeout=15)
            d = r.json()
            if d.get("status") == "000":
                parsed = parse_financial_items(d.get("list", []))
                if parsed:
                    parsed["label"] = f"{str(kst_year)[2:]}년 {label}"
                    data["quarter_latest"] = parsed
                    break  # 가장 최근 분기 하나만
        except: pass
        time.sleep(0.2)

    return data


# ═══════════════════════════════════════
# 스코어링
# ═══════════════════════════════════════

def calc_supply_score(s):
    """
    수급 점수 (0~42점)
    외인 연속 순매수  최대 15점  (7일↑★★★ / 5일12 / 3일8 / 2일4)
    기관 연속 순매수  최대 10점  (5일↑★★ / 3일7 / 2일3)
    매직지수          최대 10점  (≥0.05%★★★ / ≥0.02%7 / ≥0.01%4)
    5일 외인+기관 동반매수   5점
    신고가 근접/돌파          5점
    시총 보너스 (대형주)     최대 2점
    """
    score, reasons = 0, []
    f_consec = s.get("f_consec", 0)
    i_consec = s.get("i_consec", 0)
    magic    = s.get("magic", 0)
    f5       = s.get("f5", 0)
    i5       = s.get("i5", 0)
    nh_ratio = s.get("nh_ratio", 0)
    mktcap   = s.get("mktcap", 0)

    if f_consec >= 7:   score += 15; reasons.append(f"외인 {f_consec}일 연속 ★★★")
    elif f_consec >= 5: score += 12; reasons.append(f"외인 {f_consec}일 연속 ★★")
    elif f_consec >= 3: score += 8;  reasons.append(f"외인 {f_consec}일 연속 ★")
    elif f_consec >= 2: score += 4;  reasons.append(f"외인 {f_consec}일 연속")

    if i_consec >= 5:   score += 10; reasons.append(f"기관 {i_consec}일 연속 ★★")
    elif i_consec >= 3: score += 7;  reasons.append(f"기관 {i_consec}일 연속 ★")
    elif i_consec >= 2: score += 3;  reasons.append(f"기관 {i_consec}일 연속")

    if magic >= 0.05:   score += 10; reasons.append(f"매직 {magic:+.4f}% ★★★")
    elif magic >= 0.02: score += 7;  reasons.append(f"매직 {magic:+.4f}% ★★")
    elif magic >= 0.01: score += 4;  reasons.append(f"매직 {magic:+.4f}% ★")
    elif magic < -0.05: score -= 8;  reasons.append(f"매직 {magic:+.4f}% ⚠️")

    if f5 > 0 and i5 > 0:   score += 5; reasons.append("5일 외인+기관 동반매수")
    elif f5 < 0 and i5 < 0: score -= 5; reasons.append("5일 동반매도 ⚠️")

    if nh_ratio >= 100:  score += 5; reasons.append("신고가 돌파 🚀")
    elif nh_ratio >= 98: score += 3; reasons.append("신고가 근접")

    if mktcap >= 100000:  score += 2; reasons.append(f"대형주({fmt_won(mktcap*1e8)})")
    elif mktcap >= 50000: score += 1; reasons.append(f"중대형주({fmt_won(mktcap*1e8)})")

    if not reasons:
        reasons.append(f"외인{f_consec}일 기관{i_consec}일 매직{magic:+.4f}%")

    return min(max(score, 0), 42), reasons


def calc_fundamental_score(s, dart):
    """
    펀더멘털 점수 (0~30점)
    PER  ≤8배 10점 / ≤15배 7점 / ≤25배 4점 / >40배 -3점
    PBR  ≤0.7배 7점 / ≤1.5배 4점
    영업익 성장률  흑전/+100%↑ 10점 / +30%↑ 7점 / +10%↑ 4점
    출처: KIS(PER/PBR) + DART(영업이익)
    """
    score, reasons = 0, []
    per = s.get("per", 0)
    pbr = s.get("pbr", 0)

    if 0 < per <= 8:      score += 10; reasons.append(f"PER {per:.1f}배 저평가 ★★★")
    elif 8 < per <= 15:   score += 7;  reasons.append(f"PER {per:.1f}배 적정")
    elif 15 < per <= 25:  score += 4;  reasons.append(f"PER {per:.1f}배")
    elif per > 40:        score -= 3;  reasons.append(f"PER {per:.1f}배 고평가 ⚠️")

    if 0 < pbr <= 0.7:    score += 7;  reasons.append(f"PBR {pbr:.2f}배 자산저평가 ★★")
    elif 0.7 < pbr <= 1.5:score += 4;  reasons.append(f"PBR {pbr:.2f}배 적정")

    # 25년 vs 24년 영업이익 성장률
    a25 = dart.get("annual_2025", {})
    a24 = dart.get("annual_2024", {})
    if a25 and a24:
        curr = a25.get("op", 0)
        prev = a24.get("op", 0)
        if prev and curr:
            g = (curr - prev) / abs(prev) * 100
            if prev < 0 and curr > 0: score += 10; reasons.append("영업익 흑자전환 ★★★")
            elif g >= 100:            score += 10; reasons.append(f"영업익 +{g:.0f}% ★★★")
            elif g >= 30:             score += 7;  reasons.append(f"영업익 +{g:.0f}% ★★")
            elif g >= 10:             score += 4;  reasons.append(f"영업익 +{g:.0f}% ★")
            elif g <= -50:            score -= 5;  reasons.append(f"영업익 {g:.0f}% ⚠️")

    if not reasons:
        reasons.append(f"PER {per:.1f}배 PBR {pbr:.2f}배")

    return min(max(score, 0), 30), reasons


def fmt_dart_summary(dart):
    """
    DART 실적 요약 문자열 생성
    25년 연간 + 26년 최근 분기
    """
    lines = []
    a25 = dart.get("annual_2025", {})
    a24 = dart.get("annual_2024", {})
    q   = dart.get("quarter_latest", {})

    if a25:
        rev = fmt_won(a25.get("rev", 0))
        op  = fmt_won(a25.get("op",  0))
        opm = a25.get("op_margin", 0)
        g_str = ""
        if a24 and a24.get("op") and a25.get("op"):
            g = (a25["op"] - a24["op"]) / abs(a24["op"]) * 100
            g_str = f"  전년比 {g:+.0f}%"
        lines.append(f"  📋 <b>25년 연간</b>  매출 {rev}  영업익 {op} ({opm}%){g_str}")

    if a24:
        rev = fmt_won(a24.get("rev", 0))
        op  = fmt_won(a24.get("op",  0))
        opm = a24.get("op_margin", 0)
        lines.append(f"  📋 <b>24년 연간</b>  매출 {rev}  영업익 {op} ({opm}%)")

    if q:
        label = q.get("label", "26년 분기")
        rev   = fmt_won(q.get("rev", 0))
        op    = fmt_won(q.get("op",  0))
        opm   = q.get("op_margin", 0)
        lines.append(f"  📋 <b>{label}</b>  매출 {rev}  영업익 {op} ({opm}%)")

    return "\n".join(lines) if lines else "  DART 실적 미수집"


# ═══════════════════════════════════════
# 메인 협의 프로세스
# ═══════════════════════════════════════

def run_agent_discussion():
    kst_now = datetime.utcnow() + timedelta(hours=9)
    now_str = kst_now.strftime("%Y-%m-%d %H:%M")
    total   = len(MAJOR_STOCKS)

    # ━━━ 오케스트레이터 ━━━
    agent_say("orchestrator",
        f"📅 <b>{now_str} KST  |  장 마감</b>\n\n"
        f"오늘 분석 시작합니다.\n"
        f"대상: <b>{total}개</b> (KOSPI+KOSDAQ, 시총 1조↑)\n\n"
        f"┌ 1️⃣ 수집  → KIS API 현재가+수급 (전 종목)\n"
        f"├ 2️⃣ 수급  → 연속매수·매직지수 (시총 1조↑ 필터)\n"
        f"├ 3️⃣ 펀더  → DART 25년 연간 + 26년 분기 (상위 15개)\n"
        f"└ 4️⃣ 추천  → 수급+펀더 종합 스코어링 TOP5\n\n"
        f"<b>배점:</b> 수급 42 + 펀더 30 = 72점 만점\n\n"
        f"📡 수집 에이전트, 시작!",
        delay=2
    )

    # ━━━ 수집 에이전트 ━━━
    agent_typing(2)
    agent_say("collector",
        f"지시 수신 ✅\n\n"
        f"<b>데이터 출처:</b> 한국투자증권 KIS Open API\n"
        f"  현재가/PER/PBR: TR FHKST01010100\n"
        f"  외인·기관 수급: TR FHKST01010900\n\n"
        f"<b>{total}개 종목</b> 수집 시작 ⏳",
        delay=1
    )

    token = get_kis_token()
    if not token:
        agent_say("collector", "❌ KIS 토큰 발급 실패. 중단합니다.")
        return

    all_stocks, failed = [], []
    for i, (code, name, mkt) in enumerate(MAJOR_STOCKS):
        data = fetch_stock_data(code, token)
        if data:
            data["name"] = name
            data["mkt"]  = mkt
            all_stocks.append(data)
        else:
            failed.append(f"{name}({code})")
        if (i + 1) % 30 == 0:
            print(f"  수집: {i+1}/{total}")

    success = len(all_stocks)
    k_cnt   = sum(1 for s in all_stocks if s["mkt"] == "KOSPI")
    q_cnt   = sum(1 for s in all_stocks if s["mkt"] == "KOSDAQ")
    up_cnt  = sum(1 for s in all_stocks if s.get("change", 0) >= 0)
    dn_cnt  = success - up_cnt
    avg_chg = sum(s.get("change", 0) for s in all_stocks) / success if success else 0
    f_total = sum(s.get("f_today", 0) for s in all_stocks)
    i_total = sum(s.get("i_today", 0) for s in all_stocks)

    fail_msg = ""
    if failed:
        fail_msg = (f"\n\n⚠️ <b>수집 실패 {len(failed)}개</b>\n"
                    + ", ".join(failed[:10]))

    agent_typing(1.5)
    agent_say("collector",
        f"✅ <b>수집 완료!</b>\n\n"
        f"• 성공: <b>{success}개</b>  (KOSPI {k_cnt} / KOSDAQ {q_cnt})\n"
        f"• 상승 {up_cnt}개  /  하락 {dn_cnt}개\n"
        f"• 평균 등락: {avg_chg:+.2f}%\n"
        f"• 외국인 합산: {fmt_won(f_total)}\n"
        f"• 기관 합산: {fmt_won(i_total)}"
        f"{fail_msg}\n\n"
        f"🔬 수급 에이전트, 넘깁니다!",
        delay=2
    )

    # ━━━ 수급 분석 에이전트 ━━━
    agent_typing(2)
    agent_say("supply",
        f"<b>{success}개 종목</b> 수신 ✅\n\n"
        f"<b>필터:</b> 시총 1조 미만 제외\n\n"
        f"<b>배점 기준 (42점 만점):</b>\n"
        f"  외인 연속 순매수  최대 15점\n"
        f"  기관 연속 순매수  최대 10점\n"
        f"  매직지수          최대 10점\n"
        f"  5일 외인+기관 동반매수  5점\n"
        f"  신고가 근접/돌파        5점\n"
        f"  시총 보너스 (대형주)   최대 2점\n\n"
        f"<b>골든수급:</b> 외인 5일↑ AND 기관 5일↑\n"
        f"<b>이탈경고:</b> 외인 0일 AND 기관 0일 AND 매직 음수\n\n"
        f"⏳ 분석 중...",
        delay=2
    )

    for s in all_stocks:
        sc, rs = calc_supply_score(s)
        s["supply_score"]   = sc
        s["supply_reasons"] = rs

    # 시총 1조 이상만 필터링
    filtered = [s for s in all_stocks if s.get("mktcap", 0) >= MKTCAP_1T]
    filtered_out = success - len(filtered)

    supply_top = sorted(filtered, key=lambda x: x["supply_score"], reverse=True)[:20]

    # 골든수급: 외인 5일↑ AND 기관 5일↑
    golden = [s for s in filtered
              if s.get("f_consec", 0) >= 5 and s.get("i_consec", 0) >= 5]
    # 이탈경고: 외인+기관 모두 0일 AND 매직 음수
    warn   = [s for s in filtered
              if s.get("f_consec", 0) == 0 and s.get("i_consec", 0) == 0
              and s.get("magic", 0) < 0]

    # 시총 5조↑ 참고 TOP10
    large_top = sorted(
        [s for s in filtered if s.get("mktcap", 0) >= MKTCAP_5T],
        key=lambda x: x["supply_score"], reverse=True
    )[:10]

    top_lines = "\n".join(
        f"  {i+1}. <b>{s['name']}</b>[{'Q' if s['mkt']=='KOSDAQ' else 'K'}]"
        f"  시총{fmt_won(s.get('mktcap',0)*1e8)}"
        f"  외인{s.get('f_consec',0)}일 기관{s.get('i_consec',0)}일"
        f"  매직{s.get('magic',0):+.4f}%"
        f"  <b>{s['supply_score']}점</b>"
        for i, s in enumerate(supply_top[:10])
    )

    large_lines = "\n".join(
        f"  {i+1}. <b>{s['name']}</b>"
        f"  시총{fmt_won(s.get('mktcap',0)*1e8)}"
        f"  외인{s.get('f_consec',0)}일 기관{s.get('i_consec',0)}일"
        f"  매직{s.get('magic',0):+.4f}%"
        f"  {s['supply_score']}점"
        for i, s in enumerate(large_top)
    )

    golden_list = ", ".join(s["name"] for s in golden[:10]) + (f" 외 {len(golden)-10}개" if len(golden) > 10 else "")
    warn_list   = ", ".join(s["name"] for s in warn[:10])   + (f" 외 {len(warn)-10}개"   if len(warn)   > 10 else "")

    agent_typing(2)
    agent_say("supply",
        f"✅ <b>수급 분석 완료!</b>\n\n"
        f"<i>시총 1조 미만 {filtered_out}개 제외 → {len(filtered)}개 분석</i>\n\n"
        f"📊 <b>수급 상위 10종목 (전체):</b>\n{top_lines}\n\n"
        f"🏢 <b>시총 5조↑ 수급 TOP10 (참고):</b>\n{large_lines}\n\n"
        f"⭐ <b>골든수급</b> {len(golden)}개  (외인+기관 동시 5일↑)\n"
        f"  {golden_list if golden_list else '해당 없음'}\n\n"
        f"⚠️ <b>수급 이탈 경고</b> {len(warn)}개  (외인+기관 동시 0일+매직음수)\n"
        f"  {warn_list if warn_list else '해당 없음'}\n\n"
        f"📊 펀더멘털 에이전트, 상위 20개 넘깁니다!",
        delay=2
    )

    # ━━━ 펀더멘털 에이전트 ━━━
    agent_typing(2)
    agent_say("fundamental",
        f"상위 20개 종목 수신 ✅\n\n"
        f"<b>데이터 출처:</b>\n"
        f"  PER/PBR → KIS API (실시간)\n"
        f"  실적 → DART 금융감독원 전자공시 (연결재무제표)\n\n"
        f"<b>수집 범위:</b>\n"
        f"  25년 연간 매출·영업이익·영업이익률\n"
        f"  24년 연간 (전년 비교용)\n"
        f"  26년 최근 발표 분기 (있으면)\n\n"
        f"<b>배점 기준 (30점 만점):</b>\n"
        f"  PER ≤8배 10점 / ≤15배 7점 / ≤25배 4점\n"
        f"  PBR ≤0.7배 7점 / ≤1.5배 4점\n"
        f"  영업익 성장 흑전/+100%↑ 10점 / +30%↑ 7점\n\n"
        f"⏳ DART 수집 중 (상위 15개)...",
        delay=1.5
    )

    # DART 상위 15개 수집
    for s in supply_top[:15]:
        corp = get_corp_code(s["code"])
        s["dart"] = fetch_dart_full(corp) if corp else {}
        sc, rs = calc_fundamental_score(s, s["dart"])
        s["fundamental_score"]   = sc
        s["fundamental_reasons"] = rs

    for s in supply_top[15:]:
        s["dart"] = {}
        sc, rs = calc_fundamental_score(s, {})
        s["fundamental_score"]   = sc
        s["fundamental_reasons"] = rs

    fund_top = sorted(supply_top, key=lambda x: x["fundamental_score"], reverse=True)

    fund_lines = ""
    for i, s in enumerate(fund_top[:8]):
        mk = "Q" if s["mkt"] == "KOSDAQ" else "K"
        dart_summary = fmt_dart_summary(s.get("dart", {}))
        fund_lines += (
            f"\n  {i+1}. <b>{s['name']}</b>[{mk}]  "
            f"PER {s.get('per',0):.1f}배  PBR {s.get('pbr',0):.2f}배  "
            f"<b>{s['fundamental_score']}점</b>\n"
            f"{dart_summary}\n"
        )

    agent_typing(2)
    agent_say("fundamental",
        f"✅ <b>펀더멘털 분석 완료!</b>\n\n"
        f"📊 <b>펀더멘털 상위 8종목:</b>\n{fund_lines}\n"
        f"⭐ 추천 에이전트, 최종 판단 부탁드립니다!",
        delay=2
    )

    # ━━━ 추천 에이전트 ━━━
    agent_typing(2)
    agent_say("recommender",
        f"수급·펀더멘털 에이전트 데이터 수신 ✅\n\n"
        f"<b>종합 스코어링 (72점 만점):</b>\n"
        f"  수급      42점  (외인·기관 연속·매직·시총)\n"
        f"  펀더멘털  30점  (PER·PBR·영업익 성장)\n\n"
        f"⏳ 스코어링 중...",
        delay=2
    )

    for s in supply_top:
        s["total_score"] = (
            s.get("supply_score",      0) +
            s.get("fundamental_score", 0)
        )

    final = sorted(supply_top, key=lambda x: x["total_score"], reverse=True)

    medal = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    top5  = ""
    for i, s in enumerate(final[:5]):
        mk     = "KOSDAQ" if s["mkt"] == "KOSDAQ" else "KOSPI"
        price  = s.get("price", 0)
        change = s.get("change", 0)
        sup_r  = first_reason(s.get("supply_reasons",      []), "수급 데이터 없음")
        fun_r  = first_reason(s.get("fundamental_reasons", []), "펀더 데이터 없음")
        dart_s = fmt_dart_summary(s.get("dart", {}))

        top5 += (
            f"\n{medal[i]} <b>{s['name']}</b> [{mk}]  <b>{s['total_score']}점</b>\n"
            f"   {price:,}원  {'+' if change>=0 else ''}{change:.2f}%"
            f"  시총 {fmt_won(s.get('mktcap',0)*1e8)}\n"
            f"   수급{s.get('supply_score',0)} + 펀더{s.get('fundamental_score',0)}\n"
            f"   📡 {sup_r}\n"
            f"   📊 {fun_r}\n"
            f"{dart_s}\n"
        )

    agent_typing(2.5)
    agent_say("recommender",
        f"✅ <b>종합 스코어링 완료!</b>\n\n"
        f"━━━━ 오늘의 추천 TOP5 ━━━━"
        f"{top5}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎯 오케스트레이터, 분석 완료 보고드립니다!",
        delay=2
    )

    # ━━━ 오케스트레이터 마무리 ━━━
    up_cnt  = sum(1 for s in all_stocks if s.get("change", 0) >= 0)
    dn_cnt  = len(all_stocks) - up_cnt
    avg_chg = sum(s.get("change", 0) for s in all_stocks) / len(all_stocks) if all_stocks else 0
    f_net   = sum(s.get("f_today", 0) for s in all_stocks)
    i_net   = sum(s.get("i_today", 0) for s in all_stocks)
    top3    = " / ".join(f"{s['name']}({s['total_score']}점)" for s in final[:3])

    agent_typing(2)
    agent_say("orchestrator",
        f"🎯 <b>전체 분석 완료!</b>  {now_str} KST\n\n"
        f"━━ 오늘의 시장 ━━\n"
        f"상승 {up_cnt} / 하락 {dn_cnt}  |  평균 {avg_chg:+.2f}%\n"
        f"외국인: {fmt_won(f_net)}  기관: {fmt_won(i_net)}\n\n"
        f"━━ 에이전트 협의 결과 ━━\n"
        f"📡 수집: {success}개 완료\n"
        f"🔬 수급: 시총1조↑ {len(filtered)}개 분석 (골든 {len(golden)}개)\n"
        f"📊 펀더: DART 실적 검증 (상위 15개)\n"
        f"⭐ 추천: TOP5 도출\n\n"
        f"🏆 <b>오늘의 TOP3</b>\n{top3}\n\n"
        f"⚠️ <i>투자 참고용 · 본인 판단으로 결정하세요</i>\n"
        f"🔗 https://bjkim-pixel.github.io/market-radar/\n\n"
        f"병주, 화선님 오늘도 행복한 하루 보내세요~ 😊",
        delay=1
    )

    print(f"[recommend_bot] 완료 | TOP3: {top3}")


# ═══════════════════════════════════════
# MAIN
# ═══════════════════════════════════════

def main():
    if not TELEGRAM_TOKEN:
        print("[ERROR] TELEGRAM_TOKEN 없음"); return
    if not KIS_APP_KEY:
        print("[ERROR] KIS_APP_KEY 없음"); return
    print("[recommend_bot] 멀티 에이전트 추천 시스템 v3 시작")
    run_agent_discussion()


if __name__ == "__main__":
    main()
