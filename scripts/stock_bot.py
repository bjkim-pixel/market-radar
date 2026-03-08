#!/usr/bin/env python3
"""
stock_bot.py v3
- 전체 수신 메시지 로그 출력 (디버깅)
- chat_id 유연하게 처리 (슈퍼그룹/채널 대응)
- 개인 채팅도 허용 (테스트용)
"""

import os, time, re, requests
from datetime import datetime, timedelta

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
KIS_APP_KEY    = os.environ.get("KIS_APP_KEY", "")
KIS_APP_SECRET = os.environ.get("KIS_APP_SECRET", "")

# 허용할 chat_id 목록 (단체방 + 개인 채팅 둘 다 허용)
ALLOWED_CHATS = {
    "-5233725507",   # 단체방
    "7156534633",    # 병주님 개인 (테스트용)
}

OFFSET_FILE = "data/bot_offset.txt"
TG_BASE     = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
KIS_BASE    = "https://openapi.koreainvestment.com:9443"

NAME_TO_CODE = {
    "삼성전자": "005930", "SK하이닉스": "000660", "하이닉스": "000660",
    "LG에너지솔루션": "373220", "삼성바이오로직스": "207940",
    "현대차": "005380", "셀트리온": "068270", "KB금융": "105560",
    "기아": "000270", "POSCO홀딩스": "005490", "포스코홀딩스": "005490",
    "신한지주": "055550", "삼성물산": "028260", "현대모비스": "012330",
    "LG화학": "051910", "삼성SDI": "006400", "LG": "003550",
    "하나금융지주": "086790", "SK텔레콤": "017670", "KT": "030200",
    "삼성전기": "009150", "삼성생명": "032830", "LG전자": "066570",
    "SK이노베이션": "096770", "고려아연": "010130", "S-Oil": "010950",
    "SK": "034730", "우리금융지주": "316140", "아모레퍼시픽": "002790",
    "현대제철": "004020", "한화에어로스페이스": "012450", "한국전력": "015760",
    "KT&G": "033780", "두산에너빌리티": "034020", "한화오션": "042660",
    "현대중공업": "329180", "HMM": "011200", "메리츠금융지주": "138040",
    "GS": "078930", "한화": "000880", "대한항공": "003490",
    "현대글로비스": "086280", "이마트": "139480", "CJ제일제당": "097950",
    "한미약품": "128940", "유한양행": "000100", "종근당": "185750",
    "삼성중공업": "010140", "HD현대": "267250", "한화시스템": "382800",
    "HD한국조선해양": "009540", "한국항공우주": "047810", "LIG넥스원": "079550",
    "현대로템": "064350", "에코프로비엠": "247540", "에코프로": "086520",
    "알테오젠": "196170", "HLB": "028300", "HPSP": "403870",
    "리가켐바이오": "141080", "휴젤": "145020", "클래시스": "214150",
    "파마리서치": "214450", "하이브": "352820", "에스엠": "041510",
    "JYP": "035900", "삼양식품": "003230", "오리온": "271560",
    "포스코인터내셔널": "047050", "삼성화재": "000810", "LG유플러스": "032640",
    "현대오토에버": "307950", "한화솔루션": "009830", "기업은행": "024110",
}

TRIGGER_WORDS = [
    "분석", "실적", "목표주가", "수급", "어때", "알려줘", "조회",
    "재무", "전망", "주가", "얼마", "어떻게", "봐줘", "분석해", "정보",
]


# ═══ 유틸 ═══════════════════════════════════════════

def sf(v):
    try:    return float(str(v).replace(",", ""))
    except: return 0.0

def si(v):
    try:    return int(float(str(v).replace(",", "")))
    except: return 0

def fmt_won(v):
    if v == 0: return "0"
    neg = v < 0; a = abs(v)
    if a >= 1e12:  s = f"{a/1e12:.1f}조"
    elif a >= 1e8: s = f"{a/1e8:.0f}억"
    elif a >= 1e4: s = f"{a/1e4:.0f}만"
    else:          s = f"{a:,.0f}"
    return ("-" if neg else "+") + s


# ═══ 오프셋 ══════════════════════════════════════════

def load_offset():
    try:
        with open(OFFSET_FILE) as f:
            return int(f.read().strip())
    except:
        return 0

def save_offset(offset):
    os.makedirs("data", exist_ok=True)
    with open(OFFSET_FILE, "w") as f:
        f.write(str(offset))


# ═══ 텔레그램 ═════════════════════════════════════════

def tg_get_updates(offset):
    try:
        r = requests.get(f"{TG_BASE}/getUpdates",
                         params={"offset": offset, "timeout": 5, "limit": 50},
                         timeout=20)
        data = r.json()
        if not data.get("ok"):
            print(f"[getUpdates 오류] {data.get('description','')}")
        return data.get("result", [])
    except Exception as e:
        print(f"[getUpdates 예외] {e}")
        return []

def tg_send(chat_id, text):
    try:
        r = requests.post(f"{TG_BASE}/sendMessage", json={
            "chat_id":    chat_id,
            "text":       text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }, timeout=15)
        resp = r.json()
        if resp.get("ok"):
            print(f"  [전송 성공] chat={chat_id}")
        else:
            print(f"  [전송 실패] {resp.get('description','')}")
    except Exception as e:
        print(f"  [전송 예외] {e}")

def tg_typing(chat_id):
    try:
        requests.post(f"{TG_BASE}/sendChatAction",
                      json={"chat_id": chat_id, "action": "typing"}, timeout=5)
    except: pass


# ═══ KIS API ══════════════════════════════════════════

def get_kis_token():
    try:
        r = requests.post(f"{KIS_BASE}/oauth2/tokenP", json={
            "grant_type": "client_credentials",
            "appkey": KIS_APP_KEY, "appsecret": KIS_APP_SECRET,
        }, timeout=10)
        d = r.json()
        token = d.get("access_token", "")
        print(f"[KIS 토큰] {'성공' if token else '실패: ' + d.get('msg1','')}")
        return token
    except Exception as e:
        print(f"[KIS 토큰 예외] {e}")
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
        print(f"  [KIS {tr_id}] rt_cd={d.get('rt_cd')} msg={d.get('msg1','')}")
    except Exception as e:
        print(f"  [KIS 예외] {e}")
    return {}

def get_stock_info(code, token):
    d = kis_get("/uapi/domestic-stock/v1/quotations/inquire-price",
                {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": code},
                "FHKST01010100", token)
    o = d.get("output", {})
    if not o:
        print(f"  [KIS] {code} 현재가 응답 없음")
        return None

    price  = si(o.get("stck_prpr", 0))
    if not price:
        print(f"  [KIS] {code} 가격 0")
        return None

    info = {
        "price":    price,
        "change":   sf(o.get("prdy_ctrt", 0)),
        "diff":     si(o.get("prdy_vrss", 0)),
        "high52":   si(o.get("d250_hgpr", 0)),
        "low52":    si(o.get("d250_lwpr", 0)),
        "mktcap":   sf(o.get("hts_avls", 0)),
        "per":      sf(o.get("per", 0)),
        "pbr":      sf(o.get("pbr", 0)),
        "volume":   si(o.get("acml_vol", 0)),
    }
    h52 = info["high52"]
    info["nh_ratio"] = round(price / h52 * 100, 1) if h52 else 0
    time.sleep(0.1)

    d2   = kis_get("/uapi/domestic-stock/v1/quotations/inquire-investor",
                   {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": code},
                   "FHKST01010900", token)
    rows = d2.get("output", [])[:10]
    if rows:
        f_today = sf(rows[0].get("frgn_ntby_tr_pbmn", 0)) * 1e6
        i_today = sf(rows[0].get("orgn_ntby_tr_pbmn", 0)) * 1e6
        f5  = sum(sf(r.get("frgn_ntby_tr_pbmn", 0)) for r in rows[:5]) * 1e6
        i5  = sum(sf(r.get("orgn_ntby_tr_pbmn", 0)) for r in rows[:5]) * 1e6
        f_consec = i_consec = 0
        for row in rows:
            if si(row.get("frgn_ntby_qty", 0)) > 0: f_consec += 1
            else: break
        for row in rows:
            if si(row.get("orgn_ntby_qty", 0)) > 0: i_consec += 1
            else: break
        mktcap_won = info["mktcap"] * 1e8
        magic = round((f_today + i_today) / mktcap_won * 100, 4) if mktcap_won else 0
        info.update({
            "f_today": f_today, "i_today": i_today,
            "f5": f5, "i5": i5,
            "f_consec": f_consec, "i_consec": i_consec, "magic": magic,
        })
    return info

def build_report(name, code, info):
    price    = info.get("price", 0)
    change   = info.get("change", 0)
    diff     = info.get("diff", 0)
    mktcap   = info.get("mktcap", 0)
    per      = info.get("per", 0)
    pbr      = info.get("pbr", 0)
    high52   = info.get("high52", 0)
    low52    = info.get("low52", 0)
    nh       = info.get("nh_ratio", 0)
    f_consec = info.get("f_consec", 0)
    i_consec = info.get("i_consec", 0)
    magic    = info.get("magic", 0)
    f_today  = info.get("f_today", 0)
    i_today  = info.get("i_today", 0)
    f5       = info.get("f5", 0)
    i5       = info.get("i5", 0)

    arrow = "🔺" if change >= 0 else "🔻"
    sign  = "+" if change >= 0 else ""

    if f_consec >= 5 and i_consec >= 5:
        signal = "⭐ 골든수급! 외인+기관 동시 매집"
    elif f_consec >= 5:
        signal = f"📈 외인 {f_consec}일 연속 순매수 ★★"
    elif f_consec >= 3:
        signal = f"📈 외인 {f_consec}일 연속 순매수"
    elif i_consec >= 3:
        signal = f"📈 기관 {i_consec}일 연속 순매수"
    elif f_consec == 0 and i_consec == 0 and magic < 0:
        signal = "⚠️ 수급 이탈 경고"
    else:
        signal = f"외인 {f_consec}일  기관 {i_consec}일"

    now_str = (datetime.utcnow() + timedelta(hours=9)).strftime("%m/%d %H:%M")

    return (
        f"📊 <b>{name}</b>  ({code})\n"
        f"{'─'*22}\n"
        f"{arrow} <b>{price:,}원</b>  {sign}{diff:,}원  ({sign}{change:.2f}%)\n"
        f"시총 {fmt_won(mktcap*1e8)}  |  {now_str} KST\n\n"
        f"<b>📈 밸류에이션</b>  <i>(KIS 실시간)</i>\n"
        f"  PER {per:.1f}배  |  PBR {pbr:.2f}배\n"
        f"  52주 고가 {high52:,}원  ({nh:.1f}%)\n"
        f"  52주 저가 {low52:,}원\n\n"
        f"<b>💰 수급</b>  <i>(KIS 10일)</i>\n"
        f"  외인  오늘 {fmt_won(f_today)}  5일 {fmt_won(f5)}\n"
        f"  기관  오늘 {fmt_won(i_today)}  5일 {fmt_won(i5)}\n"
        f"  매직지수 {magic:+.4f}%\n"
        f"  {signal}"
    )


# ═══ 메시지 파싱 ══════════════════════════════════════

def extract_stock(text):
    text = text.strip()

    # 명령어
    if text.startswith("/"):
        parts = text.split(maxsplit=1)
        if parts[0].lower() in ["/도움말", "/help"]:
            return "help", None
        text = parts[1].strip() if len(parts) > 1 else ""

    if text.lower() in ["도움말", "help"]:
        return "help", None

    # 6자리 코드
    m = re.search(r'\b(\d{6})\b', text)
    if m:
        code = m.group(1)
        name = next((n for n, c in NAME_TO_CODE.items() if c == code), code)
        return name, code

    # 종목명 (긴 이름 우선)
    for name in sorted(NAME_TO_CODE.keys(), key=len, reverse=True):
        if name in text:
            return name, NAME_TO_CODE[name]

    return None, None

def is_stock_query(text):
    if any(w in text for w in TRIGGER_WORDS):
        return True
    if any(name in text for name in NAME_TO_CODE):
        return True
    if re.search(r'\b\d{6}\b', text):
        return True
    return False


# ═══ 메인 ════════════════════════════════════════════

def run_bot():
    if not TELEGRAM_TOKEN:
        print("[오류] TELEGRAM_TOKEN 없음"); return
    if not KIS_APP_KEY:
        print("[오류] KIS_APP_KEY 없음"); return

    offset = load_offset()
    print(f"[stock_bot v3] 시작  offset={offset}")
    print(f"  허용 chat_id: {ALLOWED_CHATS}")

    updates = tg_get_updates(offset)
    print(f"  수신 업데이트: {len(updates)}개")

    # offset이 너무 앞서 메시지가 없으면 → 최근 10개 기준으로 리셋
    if not updates and offset > 0:
        print(f"  ※ 메시지 없음 → offset 자동 리셋 시도")
        fresh = tg_get_updates(0)
        if fresh:
            latest_id = max(u.get("update_id", 0) for u in fresh)
            offset    = max(0, latest_id - 9)
            updates   = [u for u in fresh if u.get("update_id", 0) >= offset]
            print(f"  → offset 리셋 완료: {offset} (최신={latest_id}, 대상={len(updates)}개)")
        else:
            print("  → 새 메시지 없음")

    new_offset = offset
    processed  = 0

    # ── 전체 메시지 로그 출력 (디버깅) ──
    for upd in updates:
        upd_id = upd.get("update_id", 0)
        new_offset = max(new_offset, upd_id + 1)

        # 모든 타입 탐색
        msg = (upd.get("message")
               or upd.get("channel_post")
               or upd.get("edited_message")
               or upd.get("edited_channel_post")
               or {})
        if not msg:
            print(f"  upd_id={upd_id} 알 수 없는 타입: {list(upd.keys())}")
            continue

        chat    = msg.get("chat", {})
        chat_id = str(chat.get("id", ""))
        c_type  = chat.get("type", "")
        text    = msg.get("text", "").strip()
        sender  = msg.get("from", {}).get("username", "익명")

        # 디버깅: 모든 메시지 출력
        print(f"  upd={upd_id} chat_id={chat_id} type={c_type} from={sender} text='{text[:40]}'")

        if not text:
            continue

        # chat_id 체크
        if chat_id not in ALLOWED_CHATS:
            print(f"  → 허용되지 않은 채팅 (chat_id={chat_id}) 무시")
            continue

        if not is_stock_query(text):
            print(f"  → 종목 조회 아님, 무시")
            continue

        # KIS 토큰 (첫 조회 시 한 번만 발급)
        if processed == 0:
            token = get_kis_token()
            if not token:
                print("  → KIS 토큰 실패, 중단")
                break

        name, code = extract_stock(text)
        print(f"  → 종목 감지: name={name} code={code}")

        if name == "help":
            tg_send(chat_id,
                "📊 <b>마켓레이더 종목 조회</b>\n\n"
                "종목명이나 코드를 입력하면 현재가·수급을 알려드려요!\n\n"
                "예시:\n"
                "  삼성전자\n"
                "  삼성전자 분석해줘\n"
                "  005930\n"
                "  /분석 SK하이닉스"
            )
            processed += 1
            continue

        if not code:
            tg_send(chat_id,
                f"❓ <b>{text[:20]}</b> 종목을 찾지 못했어요.\n"
                "종목명 또는 6자리 코드로 입력해주세요."
            )
            processed += 1
            continue

        tg_typing(chat_id)
        info = get_stock_info(code, token)

        if not info:
            tg_send(chat_id, f"⚠️ <b>{name}</b>({code}) 데이터를 가져오지 못했어요.")
        else:
            tg_send(chat_id, build_report(name, code, info))

        processed += 1
        time.sleep(0.5)

    save_offset(new_offset)
    print(f"[stock_bot] 완료  processed={processed}  새 offset={new_offset}")


if __name__ == "__main__":
    run_bot()
