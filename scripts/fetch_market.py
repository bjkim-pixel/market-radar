// renderTab1() 안에서 외국인/기관 수급 렌더링 교체
// 기존: stocks 배열에서 foreign_today로 정렬
// 변경: G.top_traders 전용 데이터 사용 (더 정확)

function renderTopTrader(elId, moreId, actor, label, stocks, date) {
  // ★ top_traders API 데이터 우선 사용 (FHPST01600000)
  const tt = G?.top_traders || {};
  const buyKey  = actor + '_buy';
  const sellKey = actor + '_sell';

  // top_traders가 있으면 그걸 사용, 없으면 기존 방식 fallback
  let buying, selling;
  if (actor !== 'indiv' && tt[buyKey]?.length) {
    // ★ 전용 API 데이터 (정확도 높음)
    buying  = tt[buyKey];
    selling = tt[sellKey] || [];
  } else {
    // Fallback: stocks 배열에서 추출 (기존 방식)
    const key = actor + '_today';
    buying  = stocks.filter(s => s[key] > 0).sort((a,b) => b[key]-a[key]);
    selling = stocks.filter(s => s[key] < 0).sort((a,b) => a[key]-b[key]);
  }

  // ntby_amt 필드 우선, 없으면 actor_today 사용
  function getAmt(s, isBuy) {
    if (s.ntby_amt !== undefined) return s.ntby_amt;
    const key = actor + '_today';
    return s[key] || 0;
  }

  function mkRow(s, i, isBuy) {
    const up  = s.change >= 0;
    const amt = getAmt(s, isBuy);
    const src = s._from_investor_api ? '★' : '';  // 전용API 표시
    return `<div class="list-item" onclick="openStockModal('${s.code}')">
      <div class="li-no">${i+1}</div>
      <div class="li-info">
        <div class="li-name">${s.name} ${mktBadge(s.market)} <span style="color:var(--go);font-size:9px">${src}</span></div>
        <div class="li-sub t3">종가 ${fmtN(s.price)}원 · ${date}</div>
      </div>
      <div class="li-r">
        <div class="li-amt ${isBuy?'up':'dn'}">${fmtAmt(amt)}</div>
        <div class="li-chg ${up?'up':'dn'}">${fmtP(s.change)}</div>
      </div>
    </div>`;
  }

  const hdrBuy  = `<div style="font-size:10px;font-weight:700;color:var(--up);padding:8px 0 4px;border-bottom:1px solid var(--bd)">${label} 상위 매수 ${tt[buyKey]?.length?'★전용API':''} (${date})</div>`;
  const hdrSell = `<div style="font-size:10px;font-weight:700;color:var(--dn);padding:8px 0 4px;border-bottom:1px solid var(--bd)">${label} 상위 매도 (${date})</div>`;

  document.getElementById(elId).innerHTML =
    hdrBuy  + (buying.slice(0,10).length  ? buying.slice(0,10).map((s,i)=>mkRow(s,i,true)).join('')  : '<div class="empty">데이터 없음</div>') +
    hdrSell + (selling.slice(0,10).length ? selling.slice(0,10).map((s,i)=>mkRow(s,i,false)).join('') : '<div class="empty">데이터 없음</div>');

  if (moreId)
    document.getElementById(moreId).innerHTML =
      (buying.slice(10).length  ? hdrBuy  + buying.slice(10).map((s,i)=>mkRow(s,i+10,true)).join('')  : '') +
      (selling.slice(10).length ? hdrSell + selling.slice(10).map((s,i)=>mkRow(s,i+10,false)).join('') : '');
}
