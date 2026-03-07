#!/usr/bin/env python3
"""
멀티 에이전트 주식 추천 시스템
에이전트들이 텔레그램 단체방에서 협의하며 오늘의 추천 종목 도출
"""

import os, json, time, requests, re
from datetime import datetime, timedelta

# ── 환경변수 ──────────────────────────────────────────
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
DART_API_KEY   = os.environ.get("DART_API_KEY", "")
KIS_APP_KEY    = os.environ.get("KIS_APP_KEY", "")
KIS_APP_SECRET = os.environ.get("KIS_APP_SECRET", "")

KIS_BASE  = "https://openapi.koreainvestment.com:9443"
DART_BASE = "https://opendart.fss.or.kr/api"
TG_BASE   = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

GROUP_CHAT_ID = "-5233725507"   # 단체방 ID

# ── 에이전트 페르소나 ─────────────────────────────────
AGENTS = {
    "orchestrator": {
        "name":  "🎯 오케스트레이터",
        "desc":  "분석 총괄 · 에이전트 조율",
    },
    "collector": {
        "name":  "📡 수집 에이전트",
        "desc":  "KIS API 데이터 수집 담당",
    },
    "supply": {
        "name":  "🔬 수급 분석 에이전트",
        "desc":  "외인/기관 수급 흐름 전문",
    },
    "fundamental": {
        "name":  "📊 펀더멘털 에이전트",
        "desc":  "실적/밸류에이션 전문",
    },
    "consensus": {
        "name":  "🏦 컨센서스 에이전트",
        "desc":  "증권사 리포트/목표주가 전문",
    },
    "recommender": {
        "name":  "⭐ 추천 에이전트",
        "desc":  "종합 스코어링 및 최종 추천",
    },
}

# ── 시총 1조 이상 종목 ────────────────────────────────
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
    ("066970","엘앤에프","KOSDAQ"),
    ("058470","리노공업","KOSDAQ"),
    ("336570","원텍","KOSDAQ"),
]


# ═══════════════════════════════════════
# 텔레그램
# ═══════════════════════════════════════

def agent_say(agent_key, message, delay=1.2):
    """에이전트가 단체방에 메시지 전송"""
    agent  = AGENTS[agent_key]
    header = f"<b>{agent['name']}</b>\n<i>{agent['desc']}</i>\n{'─'*24}\n"
    full   = header + message
    try:
        requests.post(
            f"{TG_BASE}/sendMessage",
            json={
                "chat_id":                  GROUP_CHAT_ID,
                "text":                     full,
                "parse_mode":               "HTML",
                "disable_web_page_preview": True,
            },
            timeout=15
        )
    except Exception as e:
        print(f"[tg] 전송 실패: {e}")
    time.sleep(delay)


def agent_typing(delay=1.5):
    """타이핑 중 표시"""
    try:
        requests.post(
            f"{TG_BASE}/sendChatAction",
            json={"chat_id": GROUP_CHAT_ID, "action": "typing"},
            timeout=5
        )
    except:
        pass
    time.sleep(delay)


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


def fetch_stock_data(code, token):
    """종목 현재가 + 수급 수집"""
    result = {"code": code}

    # 현재가
    d = kis_get(
        "/uapi/domestic-stock/v1/quotations/inquire-price",
        {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": code},
        "FHKST01010100", token
    )
    o = d.get("output", {})
    if not o:
        return None

    price  = si(o.get("stck_prpr", 0))
    high52 = si(o.get("d250_hgpr", 0))
    low52  = si(o.get("d250_lwpr", 0))
    mktcap = sf(o.get("hts_avls", 0))

    if not price:
        return None

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
    time.sleep(0.07)

    # 수급
    d2   = kis_get(
        "/uapi/domestic-stock/v1/quotations/inquire-investor",
        {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": code},
        "FHKST01010900", token
    )
    rows = d2.get("output", [])[:10]
    if rows:
        f5  = sum(sf(r.get("frgn_ntby_tr_pbmn", 0)) for r in rows[:5])  * 1e6
        i5  = sum(sf(r.get("orgn_ntby_tr_pbmn", 0)) for r in rows[:5])  * 1e6
        f10 = sum(sf(r.get("frgn_ntby_tr_pbmn", 0)) for r in rows)      * 1e6
        i10 = sum(sf(r.get("orgn_ntby_tr_pbmn", 0)) for r in rows)      * 1e6

        f_consec = i_consec = 0
        for row in rows:
            if si(row.get("frgn_ntby_qty", 0)) > 0: f_consec += 1
            else: break
        for row in rows:
            if si(row.get("orgn_ntby_qty", 0)) > 0: i_consec += 1
            else: break

        f_today = sf(rows[0].get("frgn_ntby_tr_pbmn", 0)) * 1e6
        i_today = sf(rows[0].get("orgn_ntby_tr_pbmn", 0)) * 1e6
        mktcap_won = mktcap * 1e8
        magic = round((f_today + i_today) / mktcap_won * 100, 4) if mktcap_won else 0

        result.update({
            "f_today":  f_today,
            "i_today":  i_today,
            "f5":       f5,
            "i5":       i5,
            "f10":      f10,
            "i10":      i10,
            "f_consec": f_consec,
            "i_consec": i_consec,
            "magic":    magic,
        })
    time.sleep(0.07)
    return result


# ═══════════════════════════════════════
# DART
# ═══════════════════════════════════════

def get_corp_code(stock_code):
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


def fetch_dart(corp_code):
    """연간 실적 2개년"""
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
                    if "매출액" in acnt and "영업" not in acnt and not annual.get("rev"):
                        try: annual["rev"] = int(val)
                        except: pass
                    if "영업이익" in acnt and "손실" not in acnt and not annual.get("op"):
                        try: annual["op"] = int(val)
                        except: pass
                if annual:
                    results[year] = annual
        except:
            pass
        time.sleep(0.15)

    return results


# ═══════════════════════════════════════
# 네이버 컨센서스
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
                prices   = [i.get("targetPrice", 0) for i in items if i.get("targetPrice", 0) > 0]
                opinions = [str(i.get("opinion", "")) for i in items]
                buy_cnt  = sum(1 for o in opinions
                               if "매수" in o or "BUY" in o.upper() or "Outperform" in o)
                avg_tp   = int(sum(prices) / len(prices)) if prices else 0
                return {
                    "avg_tp":    avg_tp,
                    "buy_cnt":   buy_cnt,
                    "total":     len(items),
                    "buy_ratio": round(buy_cnt / len(items) * 100) if items else 0,
                }
    except:
        pass
    return {}


# ═══════════════════════════════════════
# 스코어링 엔진
# ═══════════════════════════════════════

def calc_supply_score(s):
    """수급 점수 (0~40점)"""
    score    = 0
    reasons  = []
    f_consec = s.get("f_consec", 0)
    i_consec = s.get("i_consec", 0)
    magic    = s.get("magic", 0)
    f5       = s.get("f5", 0)
    i5       = s.get("i5", 0)
    nh_ratio = s.get("nh_ratio", 0)

    # 외인 연속 순매수
    if f_consec >= 7:   score += 15; reasons.append(f"외인 {f_consec}일 연속 ★★★")
    elif f_consec >= 5: score += 12; reasons.append(f"외인 {f_consec}일 연속 ★★")
    elif f_consec >= 3: score += 8;  reasons.append(f"외인 {f_consec}일 연속 ★")
    elif f_consec >= 2: score += 4;  reasons.append(f"외인 {f_consec}일 연속")

    # 기관 연속 순매수
    if i_consec >= 5:   score += 10; reasons.append(f"기관 {i_consec}일 연속 ★★")
    elif i_consec >= 3: score += 7;  reasons.append(f"기관 {i_consec}일 연속 ★")
    elif i_consec >= 2: score += 3;  reasons.append(f"기관 {i_consec}일 연속")

    # 매직지수
    if magic >= 0.05:   score += 10; reasons.append(f"매직 {magic:+.4f}% ★★★")
    elif magic >= 0.02: score += 7;  reasons.append(f"매직 {magic:+.4f}% ★★")
    elif magic >= 0.01: score += 4;  reasons.append(f"매직 {magic:+.4f}% ★")
    elif magic < -0.05: score -= 8;  reasons.append(f"매직 {magic:+.4f}% ⚠️")

    # 5일 수급 방향
    if f5 > 0 and i5 > 0:  score += 5; reasons.append("5일 외인+기관 동반매수")
    elif f5 < 0 and i5 < 0: score -= 5; reasons.append("5일 외인+기관 동반매도")

    # 신고가 근접
    if nh_ratio >= 100:  score += 5; reasons.append("신고가 돌파")
    elif nh_ratio >= 98: score += 3; reasons.append("신고가 근접")

    return min(max(score, 0), 40), reasons


def calc_fundamental_score(s, dart):
    """펀더멘털 점수 (0~30점)"""
    score   = 0
    reasons = []
    per     = s.get("per", 0)
    pbr     = s.get("pbr", 0)

    # PER
    if 0 < per <= 8:    score += 10; reasons.append(f"PER {per:.1f}배 저평가 ★★★")
    elif 8 < per <= 15: score += 7;  reasons.append(f"PER {per:.1f}배 적정")
    elif 15 < per <= 25:score += 4;  reasons.append(f"PER {per:.1f}배")
    elif per > 40:      score -= 3;  reasons.append(f"PER {per:.1f}배 고평가")

    # PBR
    if 0 < pbr <= 0.7:  score += 7;  reasons.append(f"PBR {pbr:.2f}배 자산저평가 ★★")
    elif 0.7 < pbr <= 1.5: score += 4; reasons.append(f"PBR {pbr:.2f}배 적정")

    # 실적 성장률
    if dart and len(dart) >= 2:
        years = sorted(dart.keys(), reverse=True)
        curr  = dart[years[0]].get("op", 0)
        prev  = dart[years[1]].get("op", 0)
        if prev and curr:
            growth = (curr - prev) / abs(prev) * 100
            if prev < 0 and curr > 0:
                score += 10; reasons.append("영업익 흑자전환 ★★★")
            elif growth >= 100:
                score += 10; reasons.append(f"영업익 +{growth:.0f}% ★★★")
            elif growth >= 30:
                score += 7;  reasons.append(f"영업익 +{growth:.0f}% ★★")
            elif growth >= 10:
                score += 4;  reasons.append(f"영업익 +{growth:.0f}% ★")
            elif growth <= -50:
                score -= 5;  reasons.append(f"영업익 {growth:.0f}% ⚠️")

    return min(max(score, 0), 30), reasons


def calc_consensus_score(s, cons):
    """컨센서스 점수 (0~30점)"""
    score    = 0
    reasons  = []
    avg_tp   = cons.get("avg_tp", 0)
    buy_ratio= cons.get("buy_ratio", 0)
    total    = cons.get("total", 0)
    price    = s.get("price", 0)

    if not avg_tp or not price:
        return 10, ["컨센서스 데이터 없음"]

    upside = (avg_tp - price) / price * 100

    # 상승여력
    if upside >= 40:    score += 15; reasons.append(f"목표주가 상승여력 {upside:.0f}% ★★★")
    elif upside >= 25:  score += 12; reasons.append(f"목표주가 상승여력 {upside:.0f}% ★★")
    elif upside >= 15:  score += 8;  reasons.append(f"목표주가 상승여력 {upside:.0f}% ★")
    elif upside >= 5:   score += 4;  reasons.append(f"목표주가 상승여력 {upside:.0f}%")
    elif upside < -10:  score -= 5;  reasons.append(f"목표주가 하회 {upside:.0f}% ⚠️")

    # 매수의견 비율
    if buy_ratio >= 90:  score += 15; reasons.append(f"매수의견 {buy_ratio:.0f}% ★★★")
    elif buy_ratio >= 75: score += 10; reasons.append(f"매수의견 {buy_ratio:.0f}% ★★")
    elif buy_ratio >= 60: score += 6;  reasons.append(f"매수의견 {buy_ratio:.0f}% ★")
    elif buy_ratio < 40:  score -= 3;  reasons.append(f"매수의견 {buy_ratio:.0f}% ⚠️")

    if total >= 10: score += 3; reasons.append(f"리포트 {total}개 (신뢰도 높음)")

    return min(max(score, 0), 30), reasons


def fmt_won(v):
    if v == 0: return "0"
    neg = v < 0
    a   = abs(v)
    if a >= 1e12:  s = f"{a/1e12:.1f}조"
    elif a >= 1e8: s = f"{a/1e8:.0f}억"
    elif a >= 1e4: s = f"{a/1e4:.0f}만"
    else:          s = f"{a:,.0f}"
    return ("-" if neg else "+") + s


# ═══════════════════════════════════════
# 메인 협의 프로세스
# ═══════════════════════════════════════

def run_agent_discussion():
    kst_now = datetime.utcnow() + timedelta(hours=9)
    now_str = kst_now.strftime("%Y-%m-%d %H:%M")
    total   = len(MAJOR_STOCKS)

    # ──────────────────────────────────────
    # 오케스트레이터: 시작
    # ──────────────────────────────────────
    agent_say("orchestrator",
        f"📅 <b>{now_str} KST</b>\n\n"
        f"장 마감 후 분석을 시작합니다.\n\n"
        f"오늘 분석 대상: <b>시총 1조 이상 {total}개 종목</b>\n\n"
        f"진행 순서:\n"
        f"1️⃣ 수집 에이전트 → 전체 KIS 데이터 수집\n"
        f"2️⃣ 수급 에이전트 → 외인/기관 수급 필터링\n"
        f"3️⃣ 펀더멘털 에이전트 → 실적/밸류 분석\n"
        f"4️⃣ 컨센서스 에이전트 → 증권사 의견 수집\n"
        f"5️⃣ 추천 에이전트 → 종합 스코어링 및 TOP5 발표\n\n"
        f"에이전트 여러분, 분석 시작해주세요! 🚀",
        delay=2
    )

    # ──────────────────────────────────────
    # 수집 에이전트: 전체 데이터 수집
    # ──────────────────────────────────────
    agent_typing(2)
    agent_say("collector",
        f"오케스트레이터로부터 지시 수신 ✅\n\n"
        f"KIS API 토큰 발급 중...\n"
        f"<b>{total}개 종목</b> 현재가 + 수급 데이터 수집을 시작합니다.\n\n"
        f"⏳ 수집 중... (약 3~4분 소요)",
        delay=1
    )

    # KIS 토큰 발급
    token = get_kis_token()
    if not token:
        agent_say("collector", "❌ KIS 토큰 발급 실패. 수집을 중단합니다.")
        return

    # 전체 수집
    all_stocks = []
    failed     = []
    for i, (code, name, mkt) in enumerate(MAJOR_STOCKS):
        data = fetch_stock_data(code, token)
        if data:
            data["name"] = name
            data["mkt"]  = mkt
            all_stocks.append(data)
        else:
            failed.append(name)

        if (i + 1) % 30 == 0:
            print(f"  수집 진행: {i+1}/{total}")

    success = len(all_stocks)
    agent_typing(1.5)
    agent_say("collector",
        f"✅ <b>데이터 수집 완료!</b>\n\n"
        f"• 수집 성공: <b>{success}개</b> 종목\n"
        f"• 수집 실패: {len(failed)}개\n\n"
        f"KOSPI {sum(1 for s in all_stocks if s['mkt']=='KOSPI')}개 / "
        f"KOSDAQ {sum(1 for s in all_stocks if s['mkt']=='KOSDAQ')}개\n\n"
        f"수급 분석 에이전트, 데이터 넘깁니다 📨",
        delay=2
    )

    # ──────────────────────────────────────
    # 수급 분석 에이전트
    # ──────────────────────────────────────
    agent_typing(2)
    agent_say("supply",
        f"수집 에이전트로부터 <b>{success}개 종목</b> 데이터 수신 ✅\n\n"
        f"수급 기준 분석을 시작합니다.\n"
        f"• 외인 연속 순매수 일수\n"
        f"• 기관 연속 순매수 일수\n"
        f"• 매직지수 (외인+기관 / 시총)\n"
        f"• 5일/10일 누적 수급 방향\n"
        f"• 52주 신고가 근접도",
        delay=2
    )

    # 수급 점수 계산
    for s in all_stocks:
        score, reasons = calc_supply_score(s)
        s["supply_score"]   = score
        s["supply_reasons"] = reasons

    # 상위 선별
    supply_top = sorted(all_stocks, key=lambda x: x["supply_score"], reverse=True)[:20]
    supply_gold= [s for s in all_stocks if s.get("f_consec", 0) >= 5 or s.get("magic", 0) >= 0.03]
    supply_warn= [s for s in all_stocks if s.get("f_consec", 0) == 0 and s.get("magic", 0) < -0.03]

    # 상위 10개 요약
    top_lines = ""
    for i, s in enumerate(supply_top[:10]):
        mk = "Q" if s["mkt"] == "KOSDAQ" else "K"
        top_lines += (
            f"  {i+1}. {s['name']}[{mk}]  "
            f"외인{s.get('f_consec',0)}일 기관{s.get('i_consec',0)}일  "
            f"매직{s.get('magic',0):+.4f}%  "
            f"<b>{s['supply_score']}점</b>\n"
        )

    agent_typing(2)
    agent_say("supply",
        f"✅ <b>수급 분석 완료!</b>\n\n"
        f"📊 수급 상위 10종목:\n{top_lines}\n"
        f"⭐ 골든 수급 ({len(supply_gold)}개): "
        + ", ".join(s['name'] for s in supply_gold[:5])
        + (f" 외 {len(supply_gold)-5}개" if len(supply_gold) > 5 else "") + "\n\n"
        f"⚠️ 수급 이탈 경고: {len(supply_warn)}개 종목\n\n"
        f"펀더멘털 에이전트, 상위 20개 종목 넘깁니다 📨",
        delay=2
    )

    # ──────────────────────────────────────
    # 펀더멘털 에이전트
    # ──────────────────────────────────────
    agent_typing(2)
    agent_say("fundamental",
        f"수급 에이전트로부터 <b>상위 20개 종목</b> 수신 ✅\n\n"
        f"DART API로 실적 데이터를 수집합니다.\n"
        f"• 최근 2개년 연간 매출/영업이익\n"
        f"• PER / PBR 밸류에이션\n"
        f"• 영업이익 성장률\n\n"
        f"⏳ DART 수집 중...",
        delay=1.5
    )

    # 상위 20개만 DART 수집
    for s in supply_top:
        corp_code = get_corp_code(s["code"])
        s["dart"]  = fetch_dart(corp_code) if corp_code else {}
        score, reasons = calc_fundamental_score(s, s["dart"])
        s["fundamental_score"]   = score
        s["fundamental_reasons"] = reasons

    fund_top = sorted(supply_top, key=lambda x: x["fundamental_score"], reverse=True)

    fund_lines = ""
    for i, s in enumerate(fund_top[:10]):
        mk = "Q" if s["mkt"] == "KOSDAQ" else "K"
        per_str = f"PER {s['per']:.1f}" if s.get("per", 0) > 0 else "PER -"
        fund_lines += (
            f"  {i+1}. {s['name']}[{mk}]  "
            f"{per_str}배  PBR {s.get('pbr',0):.2f}배  "
            f"<b>{s['fundamental_score']}점</b>\n"
        )

    agent_typing(2)
    agent_say("fundamental",
        f"✅ <b>펀더멘털 분석 완료!</b>\n\n"
        f"📊 펀더멘털 상위 10종목:\n{fund_lines}\n"
        f"컨센서스 에이전트, 동일 20개 종목 넘깁니다 📨",
        delay=2
    )

    # ──────────────────────────────────────
    # 컨센서스 에이전트
    # ──────────────────────────────────────
    agent_typing(2)
    agent_say("consensus",
        f"펀더멘털 에이전트로부터 <b>20개 종목</b> 수신 ✅\n\n"
        f"네이버 금융에서 증권사 컨센서스를 수집합니다.\n"
        f"• 평균 목표주가 (상승여력)\n"
        f"• 매수의견 비율\n"
        f"• 리포트 수 (신뢰도)\n\n"
        f"⏳ 컨센서스 수집 중...",
        delay=1.5
    )

    for s in supply_top:
        cons  = fetch_consensus(s["code"])
        s["consensus"] = cons
        score, reasons = calc_consensus_score(s, cons)
        s["consensus_score"]   = score
        s["consensus_reasons"] = reasons
        time.sleep(0.3)

    cons_top = sorted(supply_top, key=lambda x: x["consensus_score"], reverse=True)

    cons_lines = ""
    for i, s in enumerate(cons_top[:10]):
        mk     = "Q" if s["mkt"] == "KOSDAQ" else "K"
        avg_tp = s.get("consensus", {}).get("avg_tp", 0)
        price  = s.get("price", 0)
        upside = round((avg_tp - price) / price * 100, 1) if avg_tp and price else 0
        cons_lines += (
            f"  {i+1}. {s['name']}[{mk}]  "
            f"목표 {avg_tp:,}원  상승여력 {upside:+.1f}%  "
            f"<b>{s['consensus_score']}점</b>\n"
        )

    # 에이전트간 이견 감지
    disagreements = []
    for s in supply_top:
        sup = s.get("supply_score", 0)
        fun = s.get("fundamental_score", 0)
        con = s.get("consensus_score", 0)
        if sup >= 25 and (fun <= 8 or con <= 8):
            disagreements.append(
                f"• {s['name']}: 수급({sup}점) vs 펀더(fun)/{con}점) 괴리"
            )

    disagree_text = ""
    if disagreements:
        disagree_text = (
            f"\n⚡ <b>에이전트간 이견 종목</b> ({len(disagreements)}개):\n"
            + "\n".join(disagreements[:3]) + "\n"
            + "→ 추천 에이전트가 최종 판단 필요\n"
        )

    agent_typing(2)
    agent_say("consensus",
        f"✅ <b>컨센서스 분석 완료!</b>\n\n"
        f"📊 컨센서스 상위 10종목:\n{cons_lines}"
        f"{disagree_text}\n"
        f"추천 에이전트, 모든 데이터 넘깁니다 📨",
        delay=2
    )

    # ──────────────────────────────────────
    # 추천 에이전트: 종합 스코어링
    # ──────────────────────────────────────
    agent_typing(2)
    agent_say("recommender",
        f"수급/펀더멘털/컨센서스 에이전트로부터 데이터 수신 ✅\n\n"
        f"<b>종합 스코어링</b>을 계산합니다.\n\n"
        f"가중치:\n"
        f"• 수급 점수:      40점 만점 (40%)\n"
        f"• 펀더멘털 점수:  30점 만점 (30%)\n"
        f"• 컨센서스 점수:  30점 만점 (30%)\n"
        f"• 합계:           100점 만점\n\n"
        f"⏳ 스코어링 중...",
        delay=2
    )

    # 종합 점수 계산
    for s in supply_top:
        total_score = (
            s.get("supply_score",      0) +
            s.get("fundamental_score", 0) +
            s.get("consensus_score",   0)
        )
        s["total_score"] = total_score

    final_top = sorted(supply_top, key=lambda x: x["total_score"], reverse=True)

    # TOP 5 상세 리포트 작성
    medal  = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    top5_report = ""
    for i, s in enumerate(final_top[:5]):
        mk       = "KOSDAQ" if s["mkt"] == "KOSDAQ" else "KOSPI"
        price    = s.get("price", 0)
        change   = s.get("change", 0)
        avg_tp   = s.get("consensus", {}).get("avg_tp", 0)
        upside   = round((avg_tp - price) / price * 100, 1) if avg_tp and price else 0
        sup_pts  = s.get("supply_score", 0)
        fun_pts  = s.get("fundamental_score", 0)
        con_pts  = s.get("consensus_score", 0)
        total_pt = s.get("total_score", 0)

        # 핵심 근거 (각 에이전트에서 1개씩)
        sup_r = s.get("supply_reasons",      [""])[0]
        fun_r = s.get("fundamental_reasons", [""])[0]
        con_r = s.get("consensus_reasons",   [""])[0]

        top5_report += (
            f"\n{medal[i]} <b>{s['name']}</b> [{mk}]  "
            f"<b>{total_pt}점</b>\n"
            f"   {price:,}원  {'+' if change>=0 else ''}{change:.2f}%\n"
            f"   수급{sup_pts} + 펀더{fun_pts} + 컨센{con_pts}\n"
            f"   📡 {sup_r}\n"
            f"   📊 {fun_r}\n"
            f"   🏦 {con_r}\n"
            f"   목표주가 {avg_tp:,}원 (상승여력 {upside:+.1f}%)\n"
        )

    agent_typing(2.5)
    agent_say("recommender",
        f"✅ <b>종합 스코어링 완료!</b>\n\n"
        f"━━━ 오늘의 추천 종목 TOP5 ━━━\n"
        f"{top5_report}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"오케스트레이터, 분석 완료되었습니다 ✅",
        delay=2
    )

    # ──────────────────────────────────────
    # 오케스트레이터: 최종 요약
    # ──────────────────────────────────────

    # 시장 요약 계산
    up_cnt   = sum(1 for s in all_stocks if s.get("change", 0) >= 0)
    dn_cnt   = sum(1 for s in all_stocks if s.get("change", 0) < 0)
    avg_chg  = sum(s.get("change", 0) for s in all_stocks) / len(all_stocks) if all_stocks else 0
    f_net    = sum(s.get("f_today", 0) for s in all_stocks)
    i_net    = sum(s.get("i_today", 0) for s in all_stocks)

    # TOP3 한 줄 요약
    top3_line = " / ".join(
        f"{s['name']}({s['total_score']}점)" for s in final_top[:3]
    )

    agent_typing(2)
    agent_say("orchestrator",
        f"🎯 <b>전체 분석 완료!</b>  {now_str} KST\n\n"
        f"━━ 오늘의 시장 요약 ━━\n"
        f"수집 종목: {success}개  |  상승 {up_cnt} / 하락 {dn_cnt}\n"
        f"평균 등락: {avg_chg:+.2f}%\n"
        f"외국인 합산: {fmt_won(f_net)}\n"
        f"기관 합산:   {fmt_won(i_net)}\n\n"
        f"━━ 오늘의 추천 TOP3 ━━\n"
        f"🏆 {top3_line}\n\n"
        f"━━ 에이전트 협의 결과 ━━\n"
        f"📡 수집: {success}개 종목 수집\n"
        f"🔬 수급: 상위 {len(supply_top)}개 선별\n"
        f"📊 펀더: 실적/밸류 검증 완료\n"
        f"🏦 컨센: 증권사 의견 반영 완료\n"
        f"⭐ 추천: 종합 스코어링 완료\n\n"
        f"⚠️ <i>본 분석은 투자 참고용입니다.\n"
        f"투자 결정은 본인 판단으로 해주세요.</i>\n\n"
        f"🔗 마켓레이더: https://bjkim-pixel.github.io/market-radar/",
        delay=1
    )

    print(f"[recommend_bot] 완료 | TOP5: {top3_line}")


# ═══════════════════════════════════════
# MAIN
# ═══════════════════════════════════════

def main():
    if not TELEGRAM_TOKEN:
        print("[ERROR] TELEGRAM_TOKEN 없음")
        return
    if not KIS_APP_KEY:
        print("[ERROR] KIS_APP_KEY 없음")
        return

    print("[recommend_bot] 멀티 에이전트 추천 시스템 시작")
    run_agent_discussion()


if __name__ == "__main__":
    main()