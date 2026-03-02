<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#080C14">
<meta name="apple-mobile-web-app-capable" content="yes">
<title>마켓레이더</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Noto+Sans+KR:wght@400;500;700;900&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#080C14;--bg2:#0D1220;--bg3:#111827;
  --sf:rgba(255,255,255,.04);--bd:rgba(255,255,255,.07);--bd2:rgba(255,255,255,.14);
  --up:#10D98A;--dn:#FF4D6D;--fl:#6B7A99;--ac:#3B7BF6;--go:#F5A623;--pu:#9B6EFF;--or:#FF7A3D;
  --t1:#EFF3FA;--t2:#94A3B8;--t3:#4B5875;
  --mono:'DM Mono',monospace;--sans:'Noto Sans KR',sans-serif;
  --r8:8px;--r12:12px;--r16:16px;
}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:var(--sans);background:var(--bg);color:var(--t1);min-height:100dvh;overflow-x:hidden;-webkit-font-smoothing:antialiased}
::-webkit-scrollbar{width:3px;height:3px}
::-webkit-scrollbar-thumb{background:var(--bd2);border-radius:99px}
@keyframes fadeUp{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.2}}
@keyframes ticker{from{transform:translateX(0)}to{transform:translateX(-50%)}}
@keyframes spin{to{transform:rotate(360deg)}}
.fu{animation:fadeUp .35s ease both}
.wrap{max-width:500px;margin:0 auto;min-height:100dvh;display:flex;flex-direction:column}
.ticker-band{background:#060A10;border-bottom:1px solid var(--bd);overflow:hidden;height:26px;display:flex;align-items:center;flex-shrink:0}
.ticker-inner{display:flex;animation:ticker 36s linear infinite;white-space:nowrap}
.tk{display:inline-flex;align-items:center;gap:5px;padding:0 16px;font-family:var(--mono);font-size:10px;border-right:1px solid var(--bd)}
.tk-n{color:var(--t2)}.up{color:var(--up)}.dn{color:var(--dn)}
.hdr{position:sticky;top:0;z-index:200;background:rgba(8,12,20,.96);backdrop-filter:blur(20px);border-bottom:1px solid var(--bd);padding:10px 14px 0;flex-shrink:0}
.hdr-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
.logo{display:flex;align-items:center;gap:8px}
.logo-mark{width:28px;height:28px;border-radius:var(--r8);background:linear-gradient(135deg,var(--ac),var(--pu));display:flex;align-items:center;justify-content:center;font-size:13px}
.logo-nm{font-size:16px;font-weight:900;letter-spacing:-.3px}
.hdr-r{display:flex;align-items:center;gap:7px}
.live-pill{display:flex;align-items:center;gap:4px;padding:3px 8px;border-radius:99px;font-size:9px;font-weight:700;border:1px solid}
.live-dot{width:5px;height:5px;border-radius:50%}
.clk{font-family:var(--mono);font-size:10px;color:var(--t3)}
.tabs{display:flex;gap:0;overflow-x:auto;scrollbar-width:none}
.tabs::-webkit-scrollbar{display:none}
.tab{flex-shrink:0;padding:7px 11px;font-size:11px;font-weight:500;color:var(--t3);background:transparent;border:none;border-bottom:2px solid transparent;cursor:pointer;transition:all .2s;white-space:nowrap;font-family:var(--sans)}
.tab.on{color:var(--t1);border-bottom-color:var(--ac);font-weight:700}
.date-bar{display:flex;align-items:center;justify-content:space-between;padding:6px 14px;background:rgba(59,123,246,.04);border-bottom:1px solid var(--bd);flex-shrink:0}
.date-info{font-size:10px;color:var(--t3)}
.date-info strong{color:var(--ac);font-weight:600}
.date-refresh{font-size:10px;color:var(--ac);cursor:pointer;font-weight:600}
.main{flex:1;padding:10px 10px 90px;display:flex;flex-direction:column;gap:9px;overflow-y:auto}
.panel{display:none;flex-direction:column;gap:9px}
.panel.on{display:flex}
.card{background:var(--sf);border:1px solid var(--bd);border-radius:var(--r16);overflow:hidden}
.card-h{display:flex;justify-content:space-between;align-items:center;padding:10px 13px 8px;border-bottom:1px solid var(--bd)}
.card-t{font-size:10px;font-weight:700;color:var(--t2);letter-spacing:.5px;text-transform:uppercase}
.card-m{font-size:10px;color:var(--ac);cursor:pointer;font-weight:600}
.card-b{padding:10px 13px}
.idx-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:6px}
.idx-c{background:var(--sf);border:1px solid var(--bd);border-radius:var(--r12);padding:9px 10px;cursor:pointer;transition:border-color .2s;position:relative;overflow:hidden}
.idx-c:hover{border-color:var(--bd2)}
.idx-c::before{content:'';position:absolute;top:0;left:0;right:0;height:2px}
.idx-c.up::before{background:var(--up)}.idx-c.dn::before{background:var(--dn)}
.idx-nm{font-size:8px;font-weight:700;color:var(--t3);letter-spacing:.5px;text-transform:uppercase;margin-bottom:3px}
.idx-v{font-family:var(--mono);font-size:14px;font-weight:500;line-height:1}
.idx-ch{font-family:var(--mono);font-size:9.5px;margin-top:2px}
.idx-vol{font-size:8px;color:var(--t3);margin-top:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.summary-box{background:linear-gradient(135deg,rgba(59,123,246,.08),rgba(155,110,255,.05));border:1px solid rgba(59,123,246,.18);border-radius:var(--r12);padding:12px 13px}
.summary-label{font-size:9px;font-weight:700;color:var(--ac);letter-spacing:1px;text-transform:uppercase;margin-bottom:8px;display:flex;align-items:center;justify-content:space-between}
.summary-date{font-size:9px;color:var(--t3);font-weight:400}
.summary-line{font-size:12px;color:var(--t2);line-height:1.7;padding:2px 0;border-bottom:1px solid rgba(255,255,255,.04)}
.summary-line:last-child{border-bottom:none}
.sup-row{display:flex;align-items:center;gap:8px;padding:7px 0;border-bottom:1px solid var(--bd)}
.sup-row:last-child{border-bottom:none}
.sup-nm{width:38px;font-size:11px;font-weight:500;color:var(--t2);flex-shrink:0}
.sup-bw{flex:1;height:5px;background:rgba(255,255,255,.06);border-radius:99px;overflow:hidden}
.sup-bf{height:100%;border-radius:99px;transition:width .8s ease}
.sup-bf.up{background:linear-gradient(90deg,#0EA86B,var(--up))}
.sup-bf.dn{background:linear-gradient(90deg,#CC2244,var(--dn))}
.sup-val{width:70px;text-align:right;font-family:var(--mono);font-size:11px;font-weight:500;flex-shrink:0}
.period-tabs{display:flex;gap:4px}
.period-tab{flex:1;padding:6px;font-size:11px;font-weight:600;border-radius:var(--r8);border:1px solid var(--bd);background:transparent;color:var(--t3);cursor:pointer;transition:all .2s;font-family:var(--sans)}
.period-tab.on{background:rgba(59,123,246,.12);border-color:rgba(59,123,246,.3);color:var(--ac)}
.stat-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:6px}
.stat-c{background:var(--sf);border:1px solid var(--bd);border-radius:var(--r12);padding:11px 12px}
.stat-l{font-size:9.5px;color:var(--t3);margin-bottom:4px;font-weight:500}
.stat-v{font-size:26px;font-weight:900;line-height:1}
.stat-s{font-size:9.5px;color:var(--t3);margin-top:2px}
.list-item{display:flex;align-items:center;gap:8px;padding:9px 0;border-bottom:1px solid var(--bd);cursor:pointer;transition:background .15s}
.list-item:last-child{border-bottom:none}
.list-item:active{background:rgba(255,255,255,.03)}
.li-no{width:16px;font-size:9.5px;color:var(--t3);font-family:var(--mono);text-align:center;flex-shrink:0}
.li-info{flex:1;min-width:0}
.li-name{font-size:12.5px;font-weight:600;color:var(--t1);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.li-sub{font-size:10px;color:var(--t3);margin-top:1px;display:flex;align-items:center;gap:5px;flex-wrap:wrap}
.li-r{text-align:right;flex-shrink:0}
.li-price{font-family:var(--mono);font-size:12px;font-weight:500}
.li-chg{font-family:var(--mono);font-size:10px;margin-top:1px}
.li-amt{font-family:var(--mono);font-size:11px;font-weight:500}
.badge{font-size:8.5px;font-weight:700;padding:1.5px 5px;border-radius:3px;white-space:nowrap}
.mkt-k{background:rgba(59,123,246,.15);color:var(--ac)}
.mkt-q{background:rgba(155,110,255,.15);color:var(--pu)}
.more-btn{display:flex;align-items:center;justify-content:center;gap:5px;padding:9px;font-size:11.5px;color:var(--ac);cursor:pointer;border-top:1px solid var(--bd);font-weight:600}
.more-section{display:none;padding:0 13px 10px}
.more-section.open{display:block}
.p-chips{display:flex;gap:4px;overflow-x:auto;scrollbar-width:none;padding-bottom:2px}
.p-chips::-webkit-scrollbar{display:none}
.p-chip{flex-shrink:0;padding:5px 10px;font-size:10.5px;font-weight:600;border-radius:99px;border:1px solid var(--bd);background:transparent;color:var(--t3);cursor:pointer;transition:all .2s;font-family:var(--sans)}
.p-chip.on{color:var(--t1);border-color:var(--bd2);background:rgba(255,255,255,.07)}
.mkt-tabs{display:flex;gap:4px;margin-bottom:2px}
.mkt-tab{flex:1;padding:6px;font-size:11px;font-weight:600;border-radius:var(--r8);border:1px solid var(--bd);background:transparent;color:var(--t3);cursor:pointer;transition:all .2s;font-family:var(--sans)}
.mkt-tab.on{background:rgba(59,123,246,.12);border-color:rgba(59,123,246,.3);color:var(--ac)}
.hm-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:5px}
.hm-c{border-radius:var(--r8);padding:9px 8px;cursor:pointer;transition:opacity .2s,transform .15s}
.hm-c:active{opacity:.8;transform:scale(.97)}
.hm-n{font-size:10.5px;font-weight:700;color:#fff;line-height:1.2;margin-bottom:2px}
.hm-ch{font-family:var(--mono);font-size:12px;color:rgba(255,255,255,.9)}
.hm-vol{font-size:8.5px;color:rgba(255,255,255,.5);margin-top:2px}
.sec-item{display:flex;align-items:center;gap:6px;padding:8px 0;border-bottom:1px solid var(--bd);cursor:pointer}
.sec-item:last-child{border-bottom:none}
.sec-rk{width:14px;font-size:9.5px;color:var(--t3);font-family:var(--mono);flex-shrink:0}
.sec-nm{font-size:11px;color:var(--t1);flex-shrink:0;font-weight:500;width:65px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sec-bw{flex:1;height:5px;background:rgba(255,255,255,.05);border-radius:99px;overflow:hidden}
.sec-bf{height:100%;border-radius:99px}
.sec-pct{width:46px;text-align:right;font-family:var(--mono);font-size:11px;font-weight:600;flex-shrink:0}
.sec-tv{width:38px;text-align:right;font-size:9.5px;color:var(--t3);flex-shrink:0}
.nh-tabs{display:flex;gap:5px;margin-bottom:8px}
.nh-tab{flex:1;padding:7px;font-size:11px;font-weight:700;border:1px solid var(--bd);border-radius:var(--r8);background:transparent;color:var(--t3);cursor:pointer;transition:all .2s;font-family:var(--sans)}
.nh-tab.hi{background:rgba(16,217,138,.1);border-color:rgba(16,217,138,.28);color:var(--up)}
.nh-tab.lo{background:rgba(255,77,109,.1);border-color:rgba(255,77,109,.28);color:var(--dn)}
.modal-bg{position:fixed;inset:0;z-index:500;display:flex;align-items:flex-end;background:rgba(0,0,0,.65);backdrop-filter:blur(4px)}
.modal-bg.hidden{display:none}
.modal-sheet{background:var(--bg2);border-radius:22px 22px 0 0;padding:18px 15px calc(30px + env(safe-area-inset-bottom));width:100%;max-width:500px;margin:0 auto;max-height:88dvh;overflow-y:auto;border-top:1px solid var(--bd)}
.modal-handle{width:36px;height:4px;background:var(--bd2);border-radius:99px;margin:0 auto 14px}
.modal-title{font-size:16px;font-weight:700;margin-bottom:4px}
.modal-sub{font-size:10.5px;color:var(--t3);margin-bottom:14px}
.modal-close{display:block;text-align:center;padding:12px;font-size:12px;color:var(--t3);cursor:pointer;margin-top:10px;border-top:1px solid var(--bd)}
.modal-section{margin-bottom:16px}
.modal-section-t{font-size:9.5px;font-weight:700;color:var(--t3);letter-spacing:.5px;text-transform:uppercase;margin-bottom:8px;padding-bottom:5px;border-bottom:1px solid var(--bd)}
.chart-wrap{margin:8px 0;border-radius:var(--r8);overflow:hidden;background:rgba(255,255,255,.02)}
.chart-wrap svg{display:block;width:100%}
.loading{display:flex;flex-direction:column;align-items:center;justify-content:center;padding:48px;gap:12px}
.spinner{width:26px;height:26px;border:3px solid var(--bd);border-top-color:var(--ac);border-radius:50%;animation:spin .8s linear infinite}
.error-box{background:rgba(255,77,109,.08);border:1px solid rgba(255,77,109,.2);border-radius:var(--r12);padding:16px;text-align:center;color:var(--dn);font-size:13px}
.empty{padding:20px;text-align:center;color:var(--t3);font-size:12px}
.bot-nav{position:fixed;bottom:0;left:50%;transform:translateX(-50%);width:100%;max-width:500px;background:rgba(8,12,20,.97);backdrop-filter:blur(20px);border-top:1px solid var(--bd);display:flex;padding:5px 0 calc(5px + env(safe-area-inset-bottom));z-index:200}
.nav-btn{flex:1;display:flex;flex-direction:column;align-items:center;gap:2px;padding:5px 0;background:transparent;border:none;cursor:pointer;font-family:var(--sans)}
.nav-ic{font-size:17px;line-height:1}
.nav-lb{font-size:9px;font-weight:600;color:var(--t3);transition:color .2s}
.nav-btn.on .nav-lb{color:var(--ac)}
.mono{font-family:var(--mono)}.t2{color:var(--t2)}.t3{color:var(--t3)}.fs10{font-size:10px}
</style>
</head>
<body>
<div class="wrap">

<div class="ticker-band"><div class="ticker-inner" id="tickerEl"></div></div>

<header class="hdr">
  <div class="hdr-top">
    <div class="logo">
      <div class="logo-mark">📡</div>
      <div class="logo-nm">MARKET RADAR</div>
    </div>
    <div class="hdr-r">
      <div class="live-pill" id="livePill">
        <div class="live-dot" id="liveDot"></div>
        <span id="liveLabel">--</span>
      </div>
      <div class="clk" id="clockEl">--:--:--</div>
    </div>
  </div>
  <div class="tabs">
    <button class="tab on" data-t="0">종합</button>
    <button class="tab" data-t="1">수급</button>
    <button class="tab" data-t="2">섹터</button>
    <button class="tab" data-t="3">신고가</button>
    <button class="tab" data-t="4">Phase</button>
  </div>
</header>

<div class="date-bar">
  <div class="date-info">📅 데이터 기준: <strong id="dateBadgeText">로딩 중...</strong></div>
  <div class="date-refresh" onclick="loadData()">↻ 새로고침</div>
</div>

<main class="main" id="mainEl">
  <div class="loading" id="loadingEl">
    <div class="spinner"></div>
    <div style="font-size:12px;color:var(--t3)">데이터 불러오는 중...</div>
  </div>

  <!-- TAB 0: 종합 -->
  <div class="panel fu" data-p="0">
    <div class="idx-grid" id="idxGrid"></div>
    <div class="summary-box">
      <div class="summary-label">📋 오늘의 시장 요약<span class="summary-date" id="summaryDate"></span></div>
      <div id="summaryLines"></div>
    </div>
    <div class="card">
      <div class="card-h"><span class="card-t">시장 수급</span><span class="card-m" data-goto="1">자세히 →</span></div>
      <div class="card-b" id="supplyHome"></div>
    </div>
    <div class="stat-grid" id="statHome"></div>
    <div class="card">
      <div class="card-h"><span class="card-t">🔥 주목 종목</span><span class="card-m" data-goto="4">전체 →</span></div>
      <div class="card-b" style="padding:2px 13px 10px" id="hotStocks"></div>
    </div>
  </div>

  <!-- TAB 1: 수급 -->
  <div class="panel" data-p="1">
    <div class="period-tabs">
      <button class="period-tab on" onclick="setPeriod('day')">오늘</button>
      <button class="period-tab" onclick="setPeriod('week')">1주일</button>
      <button class="period-tab" onclick="setPeriod('month')">1개월</button>
    </div>
    <div class="card">
      <div class="card-h"><span class="card-t" id="supCardT">시장 전체 수급 (오늘)</span></div>
      <div class="card-b" id="mktSupply"></div>
    </div>
    <div class="card">
      <div class="card-h"><span class="card-t">💰 외국인 Top 매수·매도</span></div>
      <div class="card-b" style="padding:2px 13px 10px" id="topForeign"></div>
      <div class="more-btn" onclick="toggleMore('fMore')">▾ 더보기</div>
      <div class="more-section" id="fMore"></div>
    </div>
    <div class="card">
      <div class="card-h"><span class="card-t">🏛️ 기관 Top 매수·매도</span></div>
      <div class="card-b" style="padding:2px 13px 10px" id="topInst"></div>
      <div class="more-btn" onclick="toggleMore('iMore')">▾ 더보기</div>
      <div class="more-section" id="iMore"></div>
    </div>
    <div class="card">
      <div class="card-h"><span class="card-t">👤 개인 Top 매수·매도</span></div>
      <div class="card-b" style="padding:2px 13px 10px" id="topIndiv"></div>
    </div>
    <div class="card">
      <div class="card-h"><span class="card-t">🔵 외인 연속 순매수</span></div>
      <div class="card-b" style="padding:2px 13px 10px" id="fConsList"></div>
      <div class="more-btn" onclick="toggleMore('fcMore')">▾ 더보기</div>
      <div class="more-section" id="fcMore"></div>
    </div>
    <div class="card">
      <div class="card-h"><span class="card-t">🟡 기관 연속 순매수</span></div>
      <div class="card-b" style="padding:2px 13px 10px" id="iConsList"></div>
      <div class="more-btn" onclick="toggleMore('icMore')">▾ 더보기</div>
      <div class="more-section" id="icMore"></div>
    </div>
  </div>

  <!-- TAB 2: 섹터 -->
  <div class="panel" data-p="2">
    <div class="mkt-tabs">
      <button class="mkt-tab on" data-m="all"    onclick="setSectorMkt('all')">전체</button>
      <button class="mkt-tab"    data-m="KOSPI"  onclick="setSectorMkt('KOSPI')">KOSPI</button>
      <button class="mkt-tab"    data-m="KOSDAQ" onclick="setSectorMkt('KOSDAQ')">KOSDAQ</button>
    </div>
    <div class="card">
      <div class="card-h"><span class="card-t">업종 히트맵</span><span class="fs10 t3" id="sectorDateLabel"></span></div>
      <div class="card-b"><div class="hm-grid" id="hmGrid"></div></div>
    </div>
    <div class="card">
      <div class="card-h"><span class="card-t">업종별 등락률 · 거래대금</span></div>
      <div class="card-b" style="padding:4px 13px 12px" id="secList"></div>
    </div>
  </div>

  <!-- TAB 3: 신고가 -->
  <div class="panel" data-p="3">
    <div class="nh-tabs">
      <button class="nh-tab hi" id="nhHBtn" onclick="switchNH('h')">📍 신고가</button>
      <button class="nh-tab"    id="nhLBtn" onclick="switchNH('l')">📉 신저가</button>
    </div>
    <div class="card">
      <div class="card-h"><span class="card-t" id="nhCardT">52주 신고가 종목</span><span class="fs10 t3" id="nhDateLabel"></span></div>
      <div class="card-b" style="padding:2px 13px 10px" id="nhList"></div>
    </div>
  </div>

  <!-- TAB 4: Phase -->
  <div class="panel" data-p="4">
    <div class="stat-grid" id="phaseStatGrid"></div>
    <div class="p-chips" id="pChips"></div>
    <div class="card">
      <div class="card-h"><span class="card-t" id="phaseCardT">Phase 신호 종목</span><span class="fs10 t3" id="phaseDateLabel"></span></div>
      <div class="card-b" style="padding:2px 13px 10px" id="phaseList"></div>
    </div>
  </div>
</main>

<!-- 지수 모달 -->
<div class="modal-bg hidden" id="idxModal" onclick="closeModal('idxModal',event)">
  <div class="modal-sheet">
    <div class="modal-handle"></div>
    <div class="modal-title" id="idxModalTitle"></div>
    <div class="modal-sub"   id="idxModalSub"></div>
    <div id="idxModalBody"></div>
    <div class="modal-close" onclick="closeModalDirect('idxModal')">닫기</div>
  </div>
</div>

<!-- 종목 모달 -->
<div class="modal-bg hidden" id="stockModal" onclick="closeModal('stockModal',event)">
  <div class="modal-sheet">
    <div class="modal-handle"></div>
    <div class="modal-title" id="stkModalTitle"></div>
    <div class="modal-sub"   id="stkModalSub"></div>
    <div id="stkModalBody"></div>
    <div class="modal-close" onclick="closeModalDirect('stockModal')">닫기</div>
  </div>
</div>

<!-- 섹터 모달 -->
<div class="modal-bg hidden" id="secModal" onclick="closeModal('secModal',event)">
  <div class="modal-sheet">
    <div class="modal-handle"></div>
    <div class="modal-title" id="secModalTitle"></div>
    <div class="modal-sub"   id="secModalSub"></div>
    <div id="secModalBody"></div>
    <div class="modal-close" onclick="closeModalDirect('secModal')">닫기</div>
  </div>
</div>

<nav class="bot-nav">
  <button class="nav-btn on" data-n="0"><span class="nav-ic">📊</span><span class="nav-lb">종합</span></button>
  <button class="nav-btn"    data-n="1"><span class="nav-ic">💰</span><span class="nav-lb">수급</span></button>
  <button class="nav-btn"    data-n="2"><span class="nav-ic">🏭</span><span class="nav-lb">섹터</span></button>
  <button class="nav-btn"    data-n="3"><span class="nav-ic">🚀</span><span class="nav-lb">신고가</span></button>
  <button class="nav-btn"    data-n="4"><span class="nav-ic">📡</span><span class="nav-lb">신호</span></button>
</nav>
</div>

<script>
/* ═══════════════════════════════════════
   전역 상태
═══════════════════════════════════════ */
let G        = null;
let _period  = 'day';
let _nhMode  = 'h';
let _pFilter = 'all';
let _secMkt  = 'all';

/* ═══════════════════════════════════════
   유틸
═══════════════════════════════════════ */
const fmtN = n => Number(n||0).toLocaleString('ko');
const fmtP = n => (n>=0?'+':'')+Number(n).toFixed(2)+'%';

function fmtAmt(n) {
  const neg=n<0, a=Math.abs(n);
  let s;
  if(a>=1e12) s=(a/1e12).toFixed(1)+'조';
  else if(a>=1e8) s=(a/1e8).toFixed(0)+'억';
  else if(a>=1e4) s=(a/1e4).toFixed(0)+'만';
  else s=fmtN(a);
  return (neg?'-':'+')+s;
}

/* 섹터 tr_amt: API 반환이 백만원 단위 → 원으로 변환 후 표시 (부호 없음) */
function fmtSecAmt(trAmt) {
  const a=Math.abs((trAmt||0)*1_000_000);
  if(a>=1e12) return (a/1e12).toFixed(1)+'조';
  if(a>=1e8)  return (a/1e8).toFixed(0)+'억';
  if(a>=1e4)  return (a/1e4).toFixed(0)+'만';
  return fmtN(a);
}

function mktBadge(m) {
  return m==='KOSDAQ'
    ? '<span class="badge mkt-q">KOSDAQ</span>'
    : '<span class="badge mkt-k">KOSPI</span>';
}
function phaseColor(k) {
  return {golden:'#F5A623',p2:'#10D98A',p1:'#3B7BF6',p3:'#FF4D6D'}[k]||'#94A3B8';
}

function makeSVGChart(data, color='#3B7BF6', h=52) {
  if(!data||data.length<2)
    return `<div style="height:${h}px;display:flex;align-items:center;justify-content:center;font-size:10px;color:var(--t3)">데이터 없음</div>`;
  const w=400,pad=4;
  const vals=data.map(d=>typeof d==='object'?d.v:d);
  const mn=Math.min(...vals),mx=Math.max(...vals),rng=mx-mn||1;
  const pts=vals.map((v,i)=>{
    const x=pad+(i/(vals.length-1))*(w-pad*2);
    const y=pad+(1-(v-mn)/rng)*(h-pad*2);
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  });
  const lx=parseFloat(pts[pts.length-1].split(',')[0]);
  const ly=parseFloat(pts[pts.length-1].split(',')[1]);
  const fill=`${pts[0].split(',')[0]},${h} ${pts.join(' ')} ${pts[pts.length-1].split(',')[0]},${h}`;
  const gid='g'+color.replace('#','');
  return `<svg viewBox="0 0 ${w} ${h}" preserveAspectRatio="none" style="width:100%;height:${h}px">
    <defs><linearGradient id="${gid}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="${color}" stop-opacity="0.25"/>
      <stop offset="100%" stop-color="${color}" stop-opacity="0"/>
    </linearGradient></defs>
    <polygon points="${fill}" fill="url(#${gid})"/>
    <polyline points="${pts.join(' ')}" fill="none" stroke="${color}" stroke-width="1.5" stroke-linejoin="round"/>
    <circle cx="${lx}" cy="${ly}" r="3" fill="${color}"/>
  </svg>`;
}

/* ═══════════════════════════════════════
   데이터 로드
═══════════════════════════════════════ */
async function loadData() {
  try {
    const resp=await fetch(`data/market.json?t=${Date.now()}`);
    if(!resp.ok) throw new Error('없음');
    G=await resp.json();
    document.getElementById('loadingEl').style.display='none';
    const activeTab=document.querySelector('.tab.on');
    const tabIdx=activeTab?activeTab.dataset.t:'0';
    document.querySelectorAll('.panel').forEach(p=>p.classList.remove('on'));
    document.querySelector(`.panel[data-p="${tabIdx}"]`)?.classList.add('on');
    const dateText=G.date||G.updated_at?.split(' ')[0]||'-';
    document.getElementById('dateBadgeText').textContent=`${dateText} (업데이트: ${G.updated_at||'-'})`;
    renderAll();
  } catch(e) {
    document.getElementById('loadingEl').innerHTML=
      `<div class="error-box">⚠️ 데이터를 불러올 수 없습니다.<br>
       <small style="color:var(--t3);margin-top:6px;display:block">GitHub Actions에서 Run workflow를 실행해주세요</small></div>`;
  }
}

function renderAll() {
  if(!G) return;
  renderTicker(); renderTab0(); renderTab1(); renderTab2(); renderTab3(); renderTab4();
}

/* ═══════════════════════════════════════
   TAB 0: 종합
═══════════════════════════════════════ */
function renderTab0() {
  const date=G.date||'-';
  const indices=G.indices||[];
  document.getElementById('idxGrid').innerHTML=indices.length
    ? indices.map(idx=>{
        const up=idx.change>=0;
        const tv=idx.tr_amt>0?fmtSecAmt(idx.tr_amt/1_000_000)+' 거래':'';
        return `<div class="idx-c ${up?'up':'dn'}" onclick="openIdxModal('${idx.name}')">
          <div class="idx-nm">${idx.name}</div>
          <div class="idx-v ${up?'up':'dn'}">${fmtN(idx.value)}</div>
          <div class="idx-ch ${up?'up':'dn'}">${fmtP(idx.change)}</div>
          <div class="idx-vol">${tv}</div>
        </div>`;
      }).join('')
    : `<div class="error-box" style="grid-column:span 3;font-size:11px">지수 데이터 없음</div>`;

  document.getElementById('summaryDate').textContent=`${date} 기준`;
  const lines=G.summary_lines||[];
  document.getElementById('summaryLines').innerHTML=lines.length
    ? lines.map(l=>`<div class="summary-line">${l}</div>`).join('')
    : '<div class="summary-line t3">데이터 수집 중...</div>';

  renderSupplyBars('supplyHome', G.market_supply||{});

  const ps=G.phase_stats||{};
  document.getElementById('statHome').innerHTML=[
    {l:'⭐ GOLDEN',v:ps.golden||0,c:'#F5A623'},
    {l:'🚀 신고가',v:ps.new_high||0,c:'#F97316'},
    {l:'🔵 P1 매집',v:ps.p1||0,c:'#3B7BF6'},
    {l:'🔴 P3 경고',v:ps.p3||0,c:'#FF4D6D'},
  ].map(s=>`<div class="stat-c" style="border-color:${s.c}22">
    <div class="stat-l">${s.l}</div>
    <div class="stat-v" style="color:${s.c}">${s.v}</div>
    <div class="stat-s">종목 (${date})</div>
  </div>`).join('');

  const hot=(G.stocks||[]).filter(s=>s.phase).slice(0,5);
  document.getElementById('hotStocks').innerHTML=hot.length
    ? hot.map((s,i)=>{
        const up=s.change>=0,pc=phaseColor(s.phase_key);
        return `<div class="list-item" onclick="openStockModal('${s.code}')">
          <div class="li-no">${i+1}</div>
          <div class="li-info">
            <div class="li-name">${s.name} ${mktBadge(s.market)}</div>
            <div class="li-sub">
              <span class="badge" style="color:${pc};background:${pc}18">${s.phase}</span>
              ${s.nh_flag?`<span class="badge" style="color:#F97316;background:#F9731618">${s.nh_flag}</span>`:''}
            </div>
          </div>
          <div class="li-r">
            <div class="li-price ${up?'up':'dn'}">${fmtN(s.price)}원</div>
            <div class="li-chg ${up?'up':'dn'}">${fmtP(s.change)}</div>
          </div>
        </div>`;
      }).join('')
    : '<div class="empty">신호 종목 없음</div>';
}

/* ═══════════════════════════════════════
   TAB 1: 수급
═══════════════════════════════════════ */
function setPeriod(p) {
  _period=p;
  document.querySelectorAll('.period-tab').forEach((b,i)=>
    b.classList.toggle('on',['day','week','month'][i]===p)
  );
  const labels={day:'오늘',week:'1주일',month:'1개월'};
  document.getElementById('supCardT').textContent=`시장 전체 수급 (${labels[p]})`;
  renderTab1();
}

function renderTab1() {
  const ms=G?.market_supply||{}, stocks=G?.stocks||[], date=G?.date||'-';
  let fn=0,inn=0,iv=0;
  if(_period==='day'){fn=ms.foreign_net||0;inn=ms.inst_net||0;iv=ms.indiv_net||0;}
  else {
    stocks.forEach(s=>{
      const sp=(s.supply_periods||{})[_period]||{};
      fn+=sp.foreign||0; inn+=sp.inst||0; iv+=sp.indiv||0;
    });
  }
  renderSupplyBars('mktSupply',{foreign_net:fn,inst_net:inn,indiv_net:iv});
  renderTopTrader('topForeign','fMore','foreign','외국인',stocks,date);
  renderTopTrader('topInst','iMore','inst','기관',stocks,date);
  renderTopTrader('topIndiv',null,'indiv','개인',stocks,date);
  renderConsec('fConsList','fcMore','f_consec','foreign_today','외인',stocks);
  renderConsec('iConsList','icMore','i_consec','inst_today','기관',stocks);
}

function renderSupplyBars(elId,ms) {
  const rows=[{nm:'외국인',v:ms.foreign_net||0},{nm:'기관',v:ms.inst_net||0},{nm:'개인',v:ms.indiv_net||0}];
  const maxA=Math.max(...rows.map(r=>Math.abs(r.v)),1);
  document.getElementById(elId).innerHTML=rows.map(r=>{
    const up=r.v>=0,pct=Math.abs(r.v)/maxA*100;
    return `<div class="sup-row">
      <div class="sup-nm">${r.nm}</div>
      <div class="sup-bw"><div class="sup-bf ${up?'up':'dn'}" style="width:${pct}%"></div></div>
      <div class="sup-val ${up?'up':'dn'}">${fmtAmt(r.v)}</div>
    </div>`;
  }).join('');
}

function renderTopTrader(elId,moreId,actor,label,stocks,date) {
  const key=actor+'_today';
  const buying=stocks.filter(s=>s[key]>0).sort((a,b)=>b[key]-a[key]);
  const selling=stocks.filter(s=>s[key]<0).sort((a,b)=>a[key]-b[key]);
  function mkRow(s,i,isBuy) {
    const up=s.change>=0;
    return `<div class="list-item" onclick="openStockModal('${s.code}')">
      <div class="li-no">${i+1}</div>
      <div class="li-info">
        <div class="li-name">${s.name} ${mktBadge(s.market)}</div>
        <div class="li-sub t3">종가 ${fmtN(s.price)}원 · ${date}</div>
      </div>
      <div class="li-r">
        <div class="li-amt ${isBuy?'up':'dn'}">${fmtAmt(s[key])}</div>
        <div class="li-chg ${up?'up':'dn'}">${fmtP(s.change)}</div>
      </div>
    </div>`;
  }
  const t10B=buying.slice(0,10),t10S=selling.slice(0,10);
  const m50B=buying.slice(10,50),m50S=selling.slice(10,50);
  const hB=`<div style="font-size:10px;font-weight:700;color:var(--up);padding:8px 0 4px;border-bottom:1px solid var(--bd)">${label} 상위 매수 (${date})</div>`;
  const hS=`<div style="font-size:10px;font-weight:700;color:var(--dn);padding:8px 0 4px;border-bottom:1px solid var(--bd)">${label} 상위 매도 (${date})</div>`;
  document.getElementById(elId).innerHTML=
    hB+(t10B.length?t10B.map((s,i)=>mkRow(s,i,true)).join(''):'<div class="empty">데이터 없음</div>')+
    hS+(t10S.length?t10S.map((s,i)=>mkRow(s,i,false)).join(''):'<div class="empty">데이터 없음</div>');
  if(moreId) document.getElementById(moreId).innerHTML=
    (m50B.length?hB+m50B.map((s,i)=>mkRow(s,i+10,true)).join(''):'')+
    (m50S.length?hS+m50S.map((s,i)=>mkRow(s,i+10,false)).join(''):'');
}

function renderConsec(elId,moreId,consecKey,amtKey,label,stocks) {
  const sorted=stocks.filter(s=>s[consecKey]>0).sort((a,b)=>b[consecKey]-a[consecKey]);
  const color=label==='외인'?'#3B7BF6':'#F5A623';
  function mkRow(s,i) {
    const up=s.change>=0;
    return `<div class="list-item" onclick="openStockModal('${s.code}')">
      <div class="li-no">${i+1}</div>
      <div class="li-info">
        <div class="li-name">${s.name} ${mktBadge(s.market)}</div>
        <div class="li-sub">
          <span style="color:${color};font-weight:700;font-size:10px">${s[consecKey]}일 연속</span>
          <span class="t3">종가 ${fmtN(s.price)}원</span>
        </div>
      </div>
      <div class="li-r">
        <div class="li-amt up">${fmtAmt(s[amtKey]||0)}</div>
        <div class="li-chg ${up?'up':'dn'}">${fmtP(s.change)}</div>
      </div>
    </div>`;
  }
  document.getElementById(elId).innerHTML=sorted.slice(0,10).length
    ? sorted.slice(0,10).map((s,i)=>mkRow(s,i)).join('')
    : '<div class="empty">데이터 없음</div>';
  if(moreId) document.getElementById(moreId).innerHTML=sorted.slice(10,50).map((s,i)=>mkRow(s,i+10)).join('');
}

/* ═══════════════════════════════════════
   TAB 2: 섹터
   ★ G.sectors 직접 사용 (KIS FHKUP03500100)
   ★ 기존 groupBySector(stocks) 완전 제거
     → "기타 27조" 버그 원인이었음
   ★ tr_amt 단위: 백만원 → fmtSecAmt() 변환
   ★ KOSPI / KOSDAQ 시장 필터 추가
═══════════════════════════════════════ */
function setSectorMkt(m) {
  _secMkt=m;
  document.querySelectorAll('.mkt-tab').forEach(b=>b.classList.toggle('on',b.dataset.m===m));
  renderTab2();
}

function getSectorList() {
  const EXCL=new Set(['0001','1001','0002','0003','0004','0028']);
  let list=(G?.sectors||[]).filter(s=>!EXCL.has(s.iscd));
  if(_secMkt!=='all') list=list.filter(s=>s.mkt_type===_secMkt);
  return list;
}

function renderTab2() {
  const date=G?.date||'-';
  document.getElementById('sectorDateLabel').textContent=`${date} 기준`;
  const sectors=getSectorList();

  if(!sectors.length) {
    const hasAny=(G?.sectors||[]).length>0;
    document.getElementById('hmGrid').innerHTML=
      `<div class="empty" style="grid-column:span 3">${hasAny?_secMkt+' 업종 데이터 없음':'Run workflow 후 확인해주세요<br><span class="t3 fs10">섹터 데이터가 아직 없습니다</span>'}</div>`;
    document.getElementById('secList').innerHTML='';
    return;
  }

  /* 히트맵: 등락률 절댓값 상위 12개 */
  const hmTop=[...sectors].sort((a,b)=>Math.abs(b.change)-Math.abs(a.change)).slice(0,12);
  document.getElementById('hmGrid').innerHTML=hmTop.map(sec=>{
    const up=sec.change>=0,inten=Math.min(Math.abs(sec.change)/6,1);
    const base=up?'14,122,78':'180,30,50';
    const bg=`rgba(${base},${(0.22+inten*0.55).toFixed(2)})`;
    const idx=sectors.indexOf(sec);
    const mk=sec.mkt_type==='KOSDAQ'?' <span style="font-size:7.5px;opacity:.65">Q</span>':' <span style="font-size:7.5px;opacity:.65">K</span>';
    return `<div class="hm-c" style="background:${bg};border:1px solid rgba(${base},.35)" onclick="openSecModal(${idx})">
      <div class="hm-n">${sec.name}${mk}</div>
      <div class="hm-ch">${sec.change>=0?'+':''}${sec.change.toFixed(2)}%</div>
      <div class="hm-vol">${fmtSecAmt(sec.tr_amt)}</div>
    </div>`;
  }).join('');

  /* 섹터 바 리스트: 등락률 순 */
  const sorted=[...sectors].sort((a,b)=>b.change-a.change);
  const maxAbs=Math.max(...sorted.map(s=>Math.abs(s.change)),1);
  document.getElementById('secList').innerHTML=sorted.map((sec,i)=>{
    const up=sec.change>=0,pct=Math.abs(sec.change)/maxAbs*100,idx=sectors.indexOf(sec);
    const mk=sec.mkt_type==='KOSDAQ'
      ? '<span class="badge mkt-q" style="font-size:7px;padding:1px 3px">Q</span>'
      : '<span class="badge mkt-k" style="font-size:7px;padding:1px 3px">K</span>';
    return `<div class="sec-item" onclick="openSecModal(${idx})">
      <div class="sec-rk">${i+1}</div>
      <div class="sec-nm">${sec.name}</div>
      ${mk}
      <div class="sec-bw"><div class="sec-bf" style="width:${pct}%;background:${up?'linear-gradient(90deg,#0EA86B,var(--up))':'linear-gradient(90deg,#CC2244,var(--dn))'}"></div></div>
      <div class="sec-pct ${up?'up':'dn'}">${up?'+':''}${sec.change.toFixed(2)}%</div>
      <div class="sec-tv">${fmtSecAmt(sec.tr_amt)}</div>
    </div>`;
  }).join('');
}

/* ═══════════════════════════════════════
   TAB 3: 신고가
═══════════════════════════════════════ */
function switchNH(mode) {
  _nhMode=mode;
  document.getElementById('nhHBtn').className='nh-tab '+(mode==='h'?'hi':'');
  document.getElementById('nhLBtn').className='nh-tab '+(mode==='l'?'lo':'');
  renderTab3();
}

function renderTab3() {
  const stocks=G?.stocks||[], date=G?.date||'-';
  document.getElementById('nhDateLabel').textContent=`${date} 기준`;
  let data,title;
  if(_nhMode==='h'){
    data=stocks.filter(s=>s.nh_flag&&s.nh_flag!=='').sort((a,b)=>(b.nh_ratio||0)-(a.nh_ratio||0));
    title='52주 신고가 근접 종목';
  } else {
    data=stocks.filter(s=>s.low52>0&&s.price/s.low52*100<=110).sort((a,b)=>(a.price/a.low52)-(b.price/b.low52));
    title='52주 신저가 근접 종목';
  }
  document.getElementById('nhCardT').textContent=`${title} (${data.length}개)`;
  document.getElementById('nhList').innerHTML=data.length
    ? data.map((s,i)=>{
        const up=s.change>=0,pc=phaseColor(s.phase_key);
        const ratio=_nhMode==='h'?`고가 대비 ${s.nh_ratio||0}%`:`저가 대비 ${(s.price/s.low52*100).toFixed(1)}%`;
        return `<div class="list-item" onclick="openStockModal('${s.code}')">
          <div class="li-no">${i+1}</div>
          <div class="li-info">
            <div class="li-name">${s.name} ${mktBadge(s.market)}</div>
            <div class="li-sub">
              ${s.nh_flag?`<span class="badge" style="color:#F97316;background:#F9731618">${s.nh_flag}</span>`:''}
              ${s.phase?`<span class="badge" style="color:${pc};background:${pc}18">${s.phase}</span>`:''}
              <span class="t3">${ratio}</span>
            </div>
          </div>
          <div class="li-r">
            <div class="li-price ${up?'up':'dn'}">${fmtN(s.price)}원</div>
            <div class="li-chg ${up?'up':'dn'}">${fmtP(s.change)}</div>
          </div>
        </div>`;
      }).join('')
    : `<div class="empty">해당 종목 없음<br><span class="t3 fs10">${date} 기준 수집 종목 중</span></div>`;
}

/* ═══════════════════════════════════════
   TAB 4: Phase
═══════════════════════════════════════ */
const P_CHIPS=[{k:'all',l:'전체'},{k:'golden',l:'⭐ GOLDEN'},{k:'p2',l:'🟢 P2'},{k:'p1',l:'🔵 P1 매집'},{k:'p3',l:'🔴 P3 경고'}];

function renderTab4() {
  const stocks=G?.stocks||[], ps=G?.phase_stats||{}, date=G?.date||'-';
  document.getElementById('phaseDateLabel').textContent=`${date} 기준`;
  document.getElementById('phaseStatGrid').innerHTML=[
    {l:'⭐ GOLDEN',v:ps.golden||0,c:'#F5A623'},
    {l:'🟢 P2 상승',v:ps.p2||0,c:'#10D98A'},
    {l:'🔵 P1 매집',v:ps.p1||0,c:'#3B7BF6'},
    {l:'🔴 P3 경고',v:ps.p3||0,c:'#FF4D6D'},
  ].map(s=>`<div class="stat-c" style="border-color:${s.c}22">
    <div class="stat-l">${s.l}</div>
    <div class="stat-v" style="color:${s.c}">${s.v}</div>
    <div class="stat-s">종목 (${date})</div>
  </div>`).join('');
  document.getElementById('pChips').innerHTML=P_CHIPS.map(c=>
    `<button class="p-chip ${c.k===_pFilter?'on':''}" onclick="setPF('${c.k}')">${c.l}</button>`
  ).join('');
  const filtered=_pFilter==='all'?stocks.filter(s=>s.phase):stocks.filter(s=>s.phase_key===_pFilter);
  const lbl=P_CHIPS.find(c=>c.k===_pFilter)?.l||'';
  document.getElementById('phaseCardT').textContent=(_pFilter==='all'?'전체 Phase 신호':lbl)+` (${filtered.length}개)`;
  document.getElementById('phaseList').innerHTML=filtered.length
    ? filtered.map((s,i)=>{
        const up=s.change>=0,pc=phaseColor(s.phase_key);
        return `<div class="list-item" onclick="openStockModal('${s.code}')">
          <div class="li-no">${i+1}</div>
          <div class="li-info">
            <div class="li-name">${s.name} ${mktBadge(s.market)}</div>
            <div class="li-sub">
              <span class="badge" style="color:${pc};background:${pc}18">${s.phase}</span>
              <span class="t3">외인 ${s.f_consec||0}일 · 거래량 ${(s.vol_ratio||1).toFixed(1)}x</span>
            </div>
          </div>
          <div class="li-r">
            <div class="li-price ${up?'up':'dn'}">${fmtN(s.price)}원</div>
            <div class="li-chg ${up?'up':'dn'}">${fmtP(s.change)}</div>
          </div>
        </div>`;
      }).join('')
    : `<div class="empty">해당 신호 없음<br><span class="t3 fs10">${date} 기준</span></div>`;
}

function setPF(k){_pFilter=k;renderTab4();}

/* ═══════════════════════════════════════
   모달: 지수 상세
═══════════════════════════════════════ */
function openIdxModal(name) {
  const idx=(G?.indices||[]).find(i=>i.name===name);
  if(!idx) return;
  const up=idx.change>=0, date=G?.date||'-';
  document.getElementById('idxModalTitle').textContent=`${name} 상세`;
  document.getElementById('idxModalSub').textContent=`${date} 기준 · 거래대금 ${fmtSecAmt((idx.tr_amt||0)/1_000_000)}`;
  const mktStocks=(G?.stocks||[]).filter(s=>name==='KSP200'?true:s.market===name);
  const fn=mktStocks.reduce((a,s)=>a+(s.foreign_today||0),0);
  const inn=mktStocks.reduce((a,s)=>a+(s.inst_today||0),0);
  const iv=mktStocks.reduce((a,s)=>a+(s.indiv_today||0),0);
  const relStocks=[...mktStocks].sort((a,b)=>(b.tr_val||0)-(a.tr_val||0)).slice(0,5);
  document.getElementById('idxModalBody').innerHTML=`
    <div class="modal-section">
      <div class="modal-section-t">지수 현황</div>
      <div style="display:flex;align-items:center;gap:12px;padding:8px 0">
        <div style="font-size:28px;font-weight:700;font-family:var(--mono);color:var(--${up?'up':'dn'})">${fmtN(idx.value)}</div>
        <div>
          <div style="font-family:var(--mono);font-size:13px;color:var(--${up?'up':'dn'})">${fmtP(idx.change)}</div>
          <div style="font-size:10px;color:var(--t3)">${up?'+':''}${fmtN(idx.diff)} pt</div>
        </div>
        <div style="margin-left:auto;text-align:right">
          <div style="font-size:9px;color:var(--t3)">상승</div>
          <div style="font-family:var(--mono);font-size:13px;color:var(--up)">${idx.ascn||'-'}개</div>
          <div style="font-size:9px;color:var(--t3);margin-top:4px">하락</div>
          <div style="font-family:var(--mono);font-size:13px;color:var(--dn)">${idx.down||'-'}개</div>
        </div>
      </div>
    </div>
    <div class="modal-section">
      <div class="modal-section-t">투자자별 수급 (수집 종목 합산)</div>
      ${(fn||inn||iv)?(() => {
        const rows=[{nm:'외국인',v:fn},{nm:'기관',v:inn},{nm:'개인',v:iv}];
        const maxA=Math.max(...rows.map(r=>Math.abs(r.v)),1);
        return rows.map(r=>{
          const ru=r.v>=0,pct=Math.abs(r.v)/maxA*100;
          return `<div class="sup-row">
            <div class="sup-nm">${r.nm}</div>
            <div class="sup-bw"><div class="sup-bf ${ru?'up':'dn'}" style="width:${pct}%"></div></div>
            <div class="sup-val ${ru?'up':'dn'}">${fmtAmt(r.v)}</div>
          </div>`;
        }).join('');
      })():'<div class="empty fs10">수급 데이터 없음</div>'}
    </div>
    <div class="modal-section">
      <div class="modal-section-t">거래대금 상위 종목</div>
      ${relStocks.map((s,i)=>{
        const su=s.change>=0;
        return `<div class="list-item" onclick="closeModalDirect('idxModal');openStockModal('${s.code}')">
          <div class="li-no">${i+1}</div>
          <div class="li-info">
            <div class="li-name">${s.name}</div>
            <div class="li-sub t3">${s.sector||''} · ${fmtAmt(s.tr_val||0)}</div>
          </div>
          <div class="li-r">
            <div class="li-price ${su?'up':'dn'}">${fmtN(s.price)}원</div>
            <div class="li-chg ${su?'up':'dn'}">${fmtP(s.change)}</div>
          </div>
        </div>`;
      }).join('')}
    </div>`;
  document.getElementById('idxModal').classList.remove('hidden');
}

/* ═══════════════════════════════════════
   모달: 종목 상세
═══════════════════════════════════════ */
function openStockModal(code) {
  const s=(G?.stocks||[]).find(s=>s.code===code);
  if(!s) return;
  const up=s.change>=0,pc=phaseColor(s.phase_key),date=G?.date||'-';
  document.getElementById('stkModalTitle').textContent=s.name;
  document.getElementById('stkModalSub').textContent=`${s.market} · ${s.sector||'-'} · ${date} 기준`;

  function spRow(label,key) {
    const d=(s.supply_periods||{})[key]||{};
    return `<div style="padding:7px 0;border-bottom:1px solid var(--bd)">
      <div style="font-size:9.5px;color:var(--t3);margin-bottom:4px;font-weight:600">${label}</div>
      <div style="display:flex;gap:10px;font-family:var(--mono);font-size:11px;flex-wrap:wrap">
        <span>외인 <strong class="${(d.foreign||0)>=0?'up':'dn'}">${fmtAmt(d.foreign||0)}</strong></span>
        <span>기관 <strong class="${(d.inst||0)>=0?'up':'dn'}">${fmtAmt(d.inst||0)}</strong></span>
        <span>개인 <strong class="${(d.indiv||0)>=0?'up':'dn'}">${fmtAmt(d.indiv||0)}</strong></span>
      </div>
    </div>`;
  }

  const phaseHtml=s.phase?`
    <div class="modal-section">
      <div class="modal-section-t">📡 Phase 신호 분석</div>
      <div style="display:inline-block;padding:5px 12px;border-radius:99px;font-size:12px;font-weight:700;color:${pc};background:${pc}18;border:1px solid ${pc}35;margin-bottom:10px">${s.phase}</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
        ${[
          {l:'무게수 비율',v:(s.muges_ratio||1).toFixed(2),d:s.muges_ratio<0.7?'매집중':s.muges_ratio>2?'분산위험':'보통'},
          {l:'SMP',v:(s.smp>=0?'+':'')+s.smp+'%',d:s.smp>0?'기관+외인 순매수':'순매도'},
          {l:'거래량 배수',v:(s.vol_ratio||1).toFixed(1)+'x',d:s.vol_ratio>=2?'거래 폭발':'보통'},
          {l:'외인 연속',v:(s.f_consec||0)+'일',d:s.f_consec>=5?'강한 매집':s.f_consec>=3?'매집 진행':''},
          {l:'기관 연속',v:(s.i_consec||0)+'일',d:''},
          {l:'OBV',v:s.obv_above_ma?'MA 상향돌파':'MA 하향',d:''},
        ].map(m=>`<div style="background:rgba(255,255,255,.04);border-radius:var(--r8);padding:8px 10px">
          <div style="font-size:9.5px;color:var(--t3);margin-bottom:3px">${m.l}</div>
          <div style="font-family:var(--mono);font-size:13px;font-weight:600;color:var(--t1)">${m.v}</div>
          ${m.d?`<div style="font-size:9px;color:var(--t2);margin-top:2px">${m.d}</div>`:''}
        </div>`).join('')}
      </div>
    </div>`:'';

  document.getElementById('stkModalBody').innerHTML=`
    <div class="modal-section">
      <div style="display:flex;align-items:flex-start;justify-content:space-between;padding:4px 0 10px">
        <div>
          <div style="font-size:28px;font-weight:700;font-family:var(--mono);color:var(--${up?'up':'dn'})">${fmtN(s.price)}원</div>
          <div style="font-family:var(--mono);font-size:12px;color:var(--${up?'up':'dn'})">${fmtP(s.change)} (${up?'+':''}${fmtN(s.diff)})</div>
          ${s.nh_flag?`<div style="display:inline-block;margin-top:6px;padding:3px 10px;border-radius:99px;font-size:11px;font-weight:700;color:#F97316;background:#F9731618;border:1px solid #F9731630">${s.nh_flag}</div>`:''}
        </div>
        <div style="text-align:right;flex-shrink:0">
          <div style="font-size:9.5px;color:var(--t3)">52주 고가</div>
          <div style="font-family:var(--mono);font-size:12px">${fmtN(s.high52)}원</div>
          <div style="font-size:9.5px;color:var(--t3);margin-top:5px">고가 대비</div>
          <div style="font-family:var(--mono);font-size:13px;font-weight:600;color:${(s.nh_ratio||0)>=99?'var(--go)':'var(--t2)'}">${s.nh_ratio||0}%</div>
          <div style="font-size:9.5px;color:var(--t3);margin-top:5px">52주 저가</div>
          <div style="font-family:var(--mono);font-size:12px">${fmtN(s.low52)}원</div>
        </div>
      </div>
    </div>
    ${phaseHtml}
    <div class="modal-section">
      <div class="modal-section-t">투자자별 수급</div>
      ${spRow('오늘','day')}${spRow('1주일','week')}${spRow('1개월','month')}
    </div>
    <div class="modal-section">
      <div class="modal-section-t">종목 정보</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:11px">
        <div class="t3">시장</div><div style="text-align:right">${mktBadge(s.market)}</div>
        <div class="t3">업종</div><div style="text-align:right">${s.sector||'-'}</div>
        <div class="t3">시가총액</div><div style="text-align:right;font-family:var(--mono)">${s.mktcap?fmtAmt(s.mktcap*1e8):'-'}</div>
        <div class="t3">거래량</div><div style="text-align:right;font-family:var(--mono)">${fmtN(s.volume)}</div>
        <div class="t3">거래대금</div><div style="text-align:right;font-family:var(--mono)">${fmtAmt(s.tr_val||0)}</div>
      </div>
    </div>`;
  document.getElementById('stockModal').classList.remove('hidden');
}

/* ═══════════════════════════════════════
   모달: 섹터 상세
   ★ G.sectors 기반 (업종 지수 + 30일 차트)
═══════════════════════════════════════ */
function openSecModal(idx) {
  const sectors=getSectorList();
  const sec=sectors[idx];
  if(!sec) return;
  const up=sec.change>=0, date=G?.date||'-', cc=up?'#10D98A':'#FF4D6D';
  document.getElementById('secModalTitle').textContent=sec.name;
  document.getElementById('secModalSub').textContent=`${sec.mkt_type} 업종 · ${date} 기준 · ${sec.change>=0?'+':''}${sec.change.toFixed(2)}%`;

  const history=sec.history||[];
  const chartHtml=history.length>=2
    ? `<div class="chart-wrap">${makeSVGChart(history.map(h=>({v:h.close})),cc,60)}</div>
       <div style="display:flex;justify-content:space-between;font-size:9px;color:var(--t3);margin-top:2px;padding:0 2px">
         <span>${(history[0]?.date||'').replace(/(\d{4})(\d{2})(\d{2})/,'$1-$2-$3')}</span>
         <span>${(history[history.length-1]?.date||'').replace(/(\d{4})(\d{2})(\d{2})/,'$1-$2-$3')}</span>
       </div>`
    : '<div class="empty fs10">차트 데이터 없음</div>';

  const sn=(sec.name||'').replace(/\s/g,'');
  const relStocks=(G?.stocks||[])
    .filter(s=>{const n=(s.sector||'').replace(/\s/g,'');return n.includes(sn.slice(0,4))||sn.includes(n.slice(0,4));})
    .sort((a,b)=>(b.tr_val||0)-(a.tr_val||0)).slice(0,10);

  document.getElementById('secModalBody').innerHTML=`
    <div class="modal-section">
      <div class="modal-section-t">업종 지수 현황 (${date})</div>
      <div style="display:flex;align-items:center;gap:14px;padding:8px 0 4px">
        <div style="font-size:26px;font-weight:700;font-family:var(--mono);color:var(--${up?'up':'dn'})">${fmtN(sec.value)}</div>
        <div style="font-family:var(--mono);font-size:13px;color:var(--${up?'up':'dn'})">${sec.change>=0?'+':''}${sec.change.toFixed(2)}%</div>
      </div>
      <div style="display:flex;gap:14px;font-size:10px;color:var(--t3)">
        <span>거래대금 ${fmtSecAmt(sec.tr_amt)}</span><span>${sec.mkt_type}</span>
      </div>
    </div>
    <div class="modal-section">
      <div class="modal-section-t">30일 업종 지수 추이</div>${chartHtml}
    </div>
    <div class="modal-section">
      <div class="modal-section-t">거래대금 상위 종목 (${date})</div>
      ${relStocks.length
        ? relStocks.map((s,i)=>{
            const su=s.change>=0;
            return `<div class="list-item" onclick="closeModalDirect('secModal');openStockModal('${s.code}')">
              <div class="li-no">${i+1}</div>
              <div class="li-info">
                <div class="li-name">${s.name} ${mktBadge(s.market)}</div>
                <div class="li-sub t3">거래대금 ${fmtAmt(s.tr_val||0)} · 종가 ${fmtN(s.price)}원</div>
              </div>
              <div class="li-r">
                <div class="li-price ${su?'up':'dn'}">${fmtN(s.price)}원</div>
                <div class="li-chg ${su?'up':'dn'}">${fmtP(s.change)}</div>
              </div>
            </div>`;
          }).join('')
        : '<div class="empty fs10">매칭 종목 없음</div>'}
    </div>`;
  document.getElementById('secModal').classList.remove('hidden');
}

/* ═══════════════════════════════════════
   모달 공통
═══════════════════════════════════════ */
function closeModal(id,e){if(e?.target===document.getElementById(id))document.getElementById(id).classList.add('hidden');}
function closeModalDirect(id){document.getElementById(id).classList.add('hidden');}

/* ═══════════════════════════════════════
   탭 전환
═══════════════════════════════════════ */
function switchTab(idx) {
  document.querySelectorAll('.tab').forEach(b=>b.classList.toggle('on',b.dataset.t===idx));
  document.querySelectorAll('.nav-btn').forEach(b=>b.classList.toggle('on',b.dataset.n===idx));
  document.querySelectorAll('.panel').forEach(p=>{
    const on=p.dataset.p===idx;
    p.classList.toggle('on',on);
    if(on) p.classList.add('fu');
  });
  document.getElementById('mainEl').scrollTop=0;
}
document.querySelectorAll('.tab').forEach(b=>b.addEventListener('click',()=>switchTab(b.dataset.t)));
document.querySelectorAll('.nav-btn').forEach(b=>b.addEventListener('click',()=>switchTab(b.dataset.n)));
document.querySelectorAll('[data-goto]').forEach(el=>el.addEventListener('click',()=>switchTab(el.dataset.goto)));

function toggleMore(id){
  const el=document.getElementById(id);
  const open=el.classList.toggle('open');
  el.previousElementSibling.textContent=open?'▴ 접기':'▾ 더보기';
}

/* ═══════════════════════════════════════
   티커
═══════════════════════════════════════ */
function renderTicker() {
  const items=[
    ...(G?.indices||[]).map(i=>({n:i.name,v:fmtN(i.value),c:i.change,up:i.change>=0})),
    ...(G?.stocks||[]).slice(0,15).map(s=>({n:s.name,v:fmtN(s.price)+'원',c:s.change,up:s.change>=0})),
  ];
  document.getElementById('tickerEl').innerHTML=items.concat(items).map(t=>
    `<div class="tk"><span class="tk-n">${t.n}</span>&nbsp;<span class="${t.up?'up':'dn'}">${t.v} ${fmtP(t.c)}</span></div>`
  ).join('');
}

/* ═══════════════════════════════════════
   시계 & 장중 상태
═══════════════════════════════════════ */
function updateClock() {
  const kst=new Date(Date.now()+9*3600000);
  const hh=String(kst.getUTCHours()).padStart(2,'0');
  const mm=String(kst.getUTCMinutes()).padStart(2,'0');
  const ss=String(kst.getUTCSeconds()).padStart(2,'0');
  document.getElementById('clockEl').textContent=`${hh}:${mm}:${ss}`;
  const t=kst.getUTCHours()*60+kst.getUTCMinutes(), dow=kst.getUTCDay();
  const open=t>=545&&t<=930&&dow>0&&dow<6;
  const dot=document.getElementById('liveDot'),lbl=document.getElementById('liveLabel'),pill=document.getElementById('livePill');
  if(open){
    dot.style.cssText='background:var(--up);animation:pulse 1.8s infinite';
    lbl.textContent='LIVE';lbl.style.color='var(--up)';
    pill.style.cssText='background:rgba(16,217,138,.1);border-color:rgba(16,217,138,.25)';
  } else {
    dot.style.cssText='background:var(--fl)';
    lbl.textContent='마감';lbl.style.color='var(--fl)';
    pill.style.cssText='background:rgba(107,122,153,.1);border-color:rgba(107,122,153,.2)';
  }
}
setInterval(updateClock,1000); updateClock();

setInterval(()=>{
  const kst=new Date(Date.now()+9*3600000);
  const t=kst.getUTCHours()*60+kst.getUTCMinutes(), dow=kst.getUTCDay();
  if(t>=545&&t<=935&&dow>0&&dow<6) loadData();
},5*60*1000);

loadData();
</script>
</body>
</html>
