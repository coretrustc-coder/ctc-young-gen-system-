"""
CoreTrust System (CTC) -- Visual Web Dashboard Generator
========================================================
Renders the whole system into a single self-contained HTML file: a boot/loading
sequence, a Matrix/"machine" animated background, a sidebar of loadable widgets,
a clickable logo that returns home, and panels for every module -- net worth,
health score, plays, product match, funding roadmap, credit, and reference.

Responsive for laptop and mobile. No external requests: all CSS/JS is inline and
the data is embedded. Generate it from the CLI (menu 18) to reflect YOUR data.
"""

from __future__ import annotations

import json
from datetime import date

from ctc_dashboard import compute_scorecard, generate_plays
from ctc_match import match
from ctc_roadmap import build_roadmap
from ctc_disputes import audit_reporting_periods
import ctc_reference as REF


def build_dashboard_data(db) -> dict:
    prof = db.get_user_profile()
    return {
        "generated": date.today().isoformat(),
        "profile": {"best_score": prof.best_score(), "us_foundation": prof.us_foundation()},
        "metrics": db.get_aggregate_metrics(),
        "net_worth": db.net_worth(),
        "scorecard": compute_scorecard(db),
        "plays": generate_plays(db),
        "matches": match(db),
        "roadmap": build_roadmap(db),
        "audit": audit_reporting_periods(db.get_credit_report_entries()),
        "portfolios": [{"type": p.portfolio_type, "room": p.remaining_room(), "value": p.market_value}
                       for p in db.get_portfolios()],
        "reference": {"crossborder": REF.CROSSBORDER_PLAYBOOK, "bureaus": REF.BUREAUS},
    }


CSS = """
:root{
  --bg:#05080b; --panel:#0a1015cc; --panel2:#0b1218; --edge:#15201c; --edge2:#1d3830;
  --green:#35f5a0; --cyan:#38e1ff; --amber:#ffcc4d; --red:#ff5d6c;
  --text:#d6efe4; --muted:#728a82; --glow:0 0 14px rgba(53,245,160,.26);
}
*{box-sizing:border-box}
body,.ctc{margin:0;font-family:'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  color:var(--text);background:var(--bg);overflow-x:hidden}
.ctc{min-height:100vh;position:relative}
#matrix{position:fixed;inset:0;z-index:0;opacity:.06}
.scan{position:fixed;inset:0;z-index:1;pointer-events:none;
  background:repeating-linear-gradient(180deg,transparent 0 3px,rgba(0,0,0,.09) 3px 4px)}
.scan:after{content:'';position:fixed;left:0;right:0;height:120px;z-index:1;
  background:linear-gradient(180deg,transparent,rgba(53,245,160,.03),transparent);
  animation:sweep 6s linear infinite}
@keyframes sweep{0%{top:-120px}100%{top:100%}}
.hidden{display:none!important}

/* boot */
#boot{position:fixed;inset:0;z-index:50;background:radial-gradient(circle at 50% 40%,#08131a,#03060a 70%);
  display:flex;align-items:center;justify-content:center}
.boot-inner{width:min(560px,90vw);text-align:center}
.boot-logo{font-size:30px;letter-spacing:8px;color:var(--green);text-shadow:var(--glow);
  animation:flick 2.4s infinite}
@keyframes flick{0%,92%,100%{opacity:1}94%{opacity:.4}96%{opacity:1}}
#bootlog{white-space:pre-wrap;text-align:left;color:var(--cyan);font-size:12px;min-height:150px;
  margin:20px 0;text-shadow:0 0 8px rgba(56,225,255,.4)}
.boot-bar{height:8px;background:#0d1a16;border:1px solid var(--edge);border-radius:6px;overflow:hidden}
#bootfill{height:100%;width:0;background:linear-gradient(90deg,var(--green),var(--cyan));box-shadow:var(--glow)}
#bootpct{margin-top:8px;color:var(--muted);font-size:12px;letter-spacing:3px}

/* shell */
.topbar{position:sticky;top:0;z-index:5;display:flex;align-items:center;justify-content:space-between;
  padding:12px 20px;background:linear-gradient(180deg,#060c10,#060c10cc);border-bottom:1px solid var(--edge);
  backdrop-filter:blur(6px)}
.brand{display:flex;align-items:center;gap:10px;cursor:pointer;user-select:none}
.logo{font-size:24px;color:var(--green);text-shadow:var(--glow);animation:spin 12s linear infinite}
@keyframes spin{100%{transform:rotate(360deg)}}
.brandname{font-weight:700;letter-spacing:4px}
.brandsub{color:var(--muted);font-size:11px;letter-spacing:2px}
.status{font-size:11px;color:var(--muted);letter-spacing:1px;display:flex;align-items:center;gap:8px}
.dot{width:8px;height:8px;border-radius:50%;background:var(--green);box-shadow:var(--glow);animation:pulse 1.6s infinite}
@keyframes pulse{50%{opacity:.35}}
.layout{position:relative;z-index:2;display:flex;gap:22px;padding:22px 26px;max-width:1240px;margin:0 auto}
#sidebar{display:flex;flex-direction:column;gap:7px;min-width:190px;position:sticky;top:70px;align-self:flex-start}
.navbtn{display:flex;align-items:center;gap:10px;padding:11px 13px;border:1px solid var(--edge);
  border-radius:10px;background:#0a1116;color:var(--muted);cursor:pointer;font-size:13px;letter-spacing:1px;
  transition:.15s}
.navbtn:hover{color:var(--text);border-color:var(--green);transform:translateX(3px)}
.navbtn.active{color:var(--green);border-color:var(--green);box-shadow:var(--glow);background:#0c1a15}
.navbtn .ic{font-size:15px}
#content{flex:1;min-width:0}

/* panels */
.panel{background:var(--panel);border:1px solid var(--edge);border-radius:16px;padding:22px;margin-bottom:18px;
  backdrop-filter:blur(4px);animation:rise .4s ease}
@keyframes rise{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.h{font-size:11px;letter-spacing:2.5px;color:var(--muted);text-transform:uppercase;margin:0 0 14px;font-weight:600}
.grid{display:grid;gap:16px}
.g3{grid-template-columns:repeat(3,1fr)}
.g2{grid-template-columns:repeat(2,1fr)}
.tile{background:var(--panel2);border:1px solid var(--edge);border-radius:14px;padding:18px}
.tile .k{color:var(--muted);font-size:10px;letter-spacing:2px;text-transform:uppercase}
.tile .v{font-size:24px;font-weight:700;margin-top:8px;font-variant-numeric:tabular-nums}
.big{font-size:30px}
.green{color:var(--green)}.cyan{color:var(--cyan)}.amber{color:var(--amber)}.red{color:var(--red)}
/* stat cards (net-worth / trend hero) */
.statrow{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.stat{background:var(--panel2);border:1px solid var(--edge);border-radius:14px;padding:16px 18px;display:flex;flex-direction:column}
.stat .k{color:var(--muted);font-size:10px;letter-spacing:2px;text-transform:uppercase}
.stat .v{font-size:25px;font-weight:800;margin-top:7px;font-variant-numeric:tabular-nums;letter-spacing:.3px}
.stat .d{font-size:11px;margin-top:7px;display:inline-flex;align-items:center;gap:5px;font-variant-numeric:tabular-nums}
.d.up{color:var(--green)} .d.dn{color:var(--red)} .d.flat{color:var(--muted)}
.stat .spk{margin-top:auto;padding-top:10px}
@media(max-width:860px){.statrow{grid-template-columns:repeat(2,1fr)}}
.gauge-num{font-variant-numeric:tabular-nums}.bar-v{font-variant-numeric:tabular-nums}
/* goal progress cards */
.goalgrid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}
@media(max-width:860px){.goalgrid{grid-template-columns:1fr}}
.goalcard{background:var(--panel2);border:1px solid var(--edge);border-radius:14px;padding:16px 18px}
.gtop{display:flex;justify-content:space-between;align-items:center;margin-bottom:11px}
.gtop .t{font-weight:700}
.gpct{font-size:12px;font-weight:700;letter-spacing:.5px;font-variant-numeric:tabular-nums}
.gbar{height:8px;background:#0c1a15;border:1px solid var(--edge);border-radius:6px;overflow:hidden;margin-bottom:11px}
.gfill{height:100%;border-radius:6px;transition:width .6s ease}

/* gauge */
.gauge{width:150px;height:150px;border-radius:50%;display:flex;align-items:center;justify-content:center;
  box-shadow:var(--glow);margin:auto}
.gauge-inner{width:116px;height:116px;border-radius:50%;background:#06100c;display:flex;flex-direction:column;
  align-items:center;justify-content:center}
.gauge-num{font-size:38px;font-weight:800;color:var(--green)}
.gauge-grade{font-size:12px;color:var(--muted);letter-spacing:3px}

/* bars */
.bar{display:grid;grid-template-columns:120px 1fr 54px;align-items:center;gap:10px;margin:8px 0;font-size:12px}
.bar-l{color:var(--muted)}
.bar-t{height:12px;background:#0c1a15;border-radius:8px;overflow:hidden;border:1px solid var(--edge)}
.bar-f{height:100%;border-radius:8px;transition:width .6s ease}
.bar-v{text-align:right}

/* lists / rows */
.row{border:1px solid var(--edge);border-radius:11px;padding:13px;margin:9px 0;background:var(--panel2)}
.row .t{font-weight:700;margin-bottom:4px}
.row .s{color:var(--muted);font-size:12px;line-height:1.55}
.tag{display:inline-block;font-size:10px;letter-spacing:1px;padding:2px 8px;border-radius:20px;
  border:1px solid var(--edge);margin-right:6px}
.tag.ok{color:var(--green);border-color:var(--green)}
.tag.mid{color:var(--amber);border-color:var(--amber)}
.tag.no{color:var(--red);border-color:var(--red)}
.chip{cursor:pointer;background:#0a1116;border:1px solid var(--edge);color:var(--muted);
  padding:6px 12px;border-radius:20px;font-size:11px;letter-spacing:1px;margin:0 6px 8px 0;display:inline-block}
.chip.active{color:var(--green);border-color:var(--green);box-shadow:var(--glow)}
.risk{color:var(--amber);font-size:11px;margin-top:6px;border-left:2px solid var(--amber);padding-left:8px}
.phase{border-left:2px solid var(--green);padding:4px 0 4px 14px;margin:14px 0}
.phase .pt{color:var(--green);letter-spacing:2px;font-size:13px;font-weight:700;margin-bottom:8px}
.foot{color:var(--muted);font-size:10px;letter-spacing:.5px;margin-top:6px;line-height:1.5}
@media(max-width:860px){
  .layout{flex-direction:column;padding:12px}
  #sidebar{flex-direction:row;overflow-x:auto;min-width:0;position:sticky;top:56px;z-index:4;
    padding-bottom:4px}
  .navbtn{white-space:nowrap}
  .navbtn:hover{transform:none}
  .g3,.g2{grid-template-columns:1fr}
  .bar{grid-template-columns:96px 1fr 48px}
  .brandsub{display:none}
}
"""

BODY = """
<div class="ctc">
<canvas id="matrix"></canvas>
<div class="scan"></div>

<div id="boot">
  <div class="boot-inner">
    <div class="boot-logo">&#9672; CORETRUST</div>
    <pre id="bootlog"></pre>
    <div class="boot-bar"><div id="bootfill"></div></div>
    <div id="bootpct">0%</div>
  </div>
</div>

<div id="app" class="hidden">
  <header class="topbar">
    <div class="brand" onclick="go('overview')" title="Back to overview">
      <span class="logo">&#9672;</span>
      <span class="brandname">CORETRUST</span>
      <span class="brandsub">// financial core</span>
    </div>
    <div class="status"><span class="dot"></span><span>SYSTEM ONLINE</span> &middot; <span id="gen"></span></div>
  </header>
  <div class="layout">
    <nav id="sidebar"></nav>
    <main id="content"></main>
  </div>
</div>
</div>
"""

JS = """
const D = window.DATA;
const money = n => '$'+Number(n||0).toLocaleString('en-CA',{maximumFractionDigits:0});
const pct = n => (n===null||n===undefined)?'n/a':(Number(n).toFixed(1)+'%');
const gcol = s => s>=70?'var(--green)':s>=55?'var(--amber)':'var(--red)';

/* ---- matrix rain ---- */
(function(){
  const c=document.getElementById('matrix'), x=c.getContext('2d');
  const chars='01<>{}[]$#%&+=/\\\\ABCDEF0123456789¥€£₿アカサタナ'.split('');
  let cols,drops;
  function size(){c.width=innerWidth;c.height=innerHeight;cols=Math.floor(c.width/14);
    drops=Array(cols).fill(1);}
  size(); addEventListener('resize',size);
  function draw(){
    x.fillStyle='rgba(5,8,11,0.08)'; x.fillRect(0,0,c.width,c.height);
    x.font='13px monospace';
    for(let i=0;i<cols;i++){
      const ch=chars[Math.floor(Math.random()*chars.length)];
      x.fillStyle=Math.random()>0.975?'#8fffd0':'#1fae7a';
      x.fillText(ch,i*14,drops[i]*14);
      if(drops[i]*14>c.height && Math.random()>0.975) drops[i]=0;
      drops[i]++;
    }
  }
  setInterval(draw,55);
})();

/* ---- boot sequence ---- */
(function(){
  const lines=['> initializing CORETRUST core ...','> mounting local ledger [OK]',
   '> loading credit bureaus // Equifax·TransUnion [OK]','> computing net worth & health score ...',
   '> ranking product matches (CA/US · personal/business) ...','> compiling funding roadmap ...',
   '> digital-asset module armed [OK]','> SYSTEM READY'];
  const log=document.getElementById('bootlog'), fill=document.getElementById('bootfill'),
        pctEl=document.getElementById('bootpct');
  let i=0;
  function step(){
    if(i<lines.length){
      log.textContent += lines[i]+'\\n';
      const p=Math.round(((i+1)/lines.length)*100);
      fill.style.width=p+'%'; pctEl.textContent=p+'%';
      i++; setTimeout(step, 260+Math.random()*180);
    } else {
      setTimeout(()=>{document.getElementById('boot').classList.add('hidden');
        document.getElementById('app').classList.remove('hidden'); go('overview');}, 500);
    }
  }
  document.getElementById('gen').textContent = 'build '+D.generated;
  step();
})();

/* ---- nav ---- */
const NAV=[['overview','&#9673;','Overview'],['networth','&#9636;','Net Worth'],
 ['health','&#10084;','Health'],['plays','&#9889;','Plays'],['matches','&#9672;','Product Match'],
 ['roadmap','&#9656;','Roadmap'],['credit','&#10022;','Credit'],['reference','&#9731;','Reference']];
(function(){
  document.getElementById('sidebar').innerHTML = NAV.map(n=>
    `<div class="navbtn" data-v="${n[0]}" onclick="go('${n[0]}')"><span class="ic">${n[1]}</span>${n[2]}</div>`).join('');
})();

function bar(label,val,max,col){
  const w=Math.max(0,Math.min(100,(val/max)*100));
  return `<div class="bar"><div class="bar-l">${label}</div>
    <div class="bar-t"><div class="bar-f" style="width:${w}%;background:${col||'var(--green)'}"></div></div>
    <div class="bar-v">${typeof val==='number'?Math.round(val):val}</div></div>`;
}
function gauge(s,g){
  return `<div class="gauge" style="background:conic-gradient(${gcol(s)} ${s*3.6}deg,#12201a 0)">
    <div class="gauge-inner"><div class="gauge-num" style="color:${gcol(s)}">${s}</div>
    <div class="gauge-grade">GRADE ${g}</div></div></div>`;
}
function tile(k,v,cls){return `<div class="tile"><div class="k">${k}</div><div class="v ${cls||''}">${v}</div></div>`;}
const DISC='Educational tool. Not legal, tax, or investment advice. Figures use your inputs and 2026 default rates; verify before acting.';

/* ---- views ---- */
const V={};
V.overview=()=>{
  const s=D.scorecard, nw=D.net_worth, m=D.metrics;
  const plays=D.plays.slice(0,3).map(p=>`<div class="row"><div class="t">${p.title}</div>
    <div class="s">${p.estimated_benefit}</div></div>`).join('')||'<div class="s">Add data to surface plays.</div>';
  const ready=D.matches.filter(x=>x.readiness_pct>=100).slice(0,4).map(x=>
    `<div class="row"><span class="tag ok">${x.country}/${x.segment}</span><span class="t">${x.name}</span></div>`).join('')
    ||'<div class="s">No ready matches yet.</div>';
  const ph=D.roadmap.phases[0];
  return `<div class="panel"><div class="h">Command Overview</div>
    <div class="grid g3" style="align-items:center">
      <div>${gauge(s.composite_score,s.grade)}<div class="foot" style="text-align:center">Financial health</div></div>
      ${tile('Net worth',money(nw.net_worth),'big green')}
      ${tile('Best credit score',D.profile.best_score||'—','big cyan')}
    </div></div>
  <div class="grid g2">
    <div class="panel"><div class="h">Signals</div>
      ${tile('Utilization',pct(s.utilization_pct))}
      ${tile('Debt-to-income',pct(s.dti_pct))}
      ${tile('Liquid assets',money(nw.liquid_assets))}
      ${tile('Emergency fund',(s.emergency_fund_months??'—')+' mo')}</div>
    <div class="panel"><div class="h">Top plays</div>${plays}
      <div class="h" style="margin-top:14px">Ready to apply</div>${ready}</div>
  </div>
  <div class="panel"><div class="h">Next: ${ph?('Phase '+ph.n+' · '+ph.title):'—'}</div>
    <div class="s">Open the Roadmap widget for the full ordered plan.</div>
    <div class="foot">${DISC}</div></div>`;
};
V.networth=()=>{
  const a=D.net_worth.assets,l=D.net_worth.liabilities,mx=Math.max(a.total,l.total,1);
  return `<div class="panel"><div class="h">Net Worth &middot; ${money(D.net_worth.net_worth)}</div>
    <div class="grid g2"><div>
      <div class="h">Assets ${money(a.total)}</div>
      ${bar('Cash',a.cash_accounts,mx,'var(--green)')}
      ${bar('Business cash',a.business_cash,mx,'var(--green)')}
      ${bar('Registered',a.registered_value,mx,'var(--cyan)')}
      ${bar('Other assets',a.other_assets,mx,'var(--cyan)')}
    </div><div>
      <div class="h">Liabilities ${money(l.total)}</div>
      ${bar('Credit cards',l.credit_cards,mx,'var(--red)')}
      ${bar('Installment',l.installment_debts,mx,'var(--red)')}
      ${bar('Secured',l.secured_on_assets,mx,'var(--amber)')}
    </div></div>
    <div class="grid g3" style="margin-top:8px">
      ${tile('Assets',money(a.total),'green')}${tile('Liabilities',money(l.total),'red')}
      ${tile('Liquid',money(D.net_worth.liquid_assets),'cyan')}</div></div>`;
};
V.health=()=>{
  const s=D.scorecard,c=s.components,w=s.weights;
  const rows=Object.keys(c).map(k=>bar(k+' ('+Math.round(w[k]*100)+'%)',c[k],100,gcol(c[k]))).join('');
  return `<div class="panel" style="text-align:center">${gauge(s.composite_score,s.grade)}
    <div class="foot">Composite financial-health score</div></div>
  <div class="panel"><div class="h">Component scores</div>${rows}</div>`;
};
V.plays=()=>{
  const rows=D.plays.map(p=>`<div class="row"><div class="t">[${p.priority}] ${p.title}</div>
    <div class="s"><b>Why:</b> ${p.why}<br><b>Benefit:</b> ${p.estimated_benefit}<br><b>Do:</b> ${p.action}</div></div>`).join('')
    ||'<div class="s">Add cards, savings, registered room and assets to unlock plays.</div>';
  return `<div class="panel"><div class="h">Opportunity Plays</div>${rows}<div class="foot">${DISC}</div></div>`;
};
let MF='all';
window.mf=f=>{MF=f;go('matches');};
V.matches=()=>{
  const chips=[['all','ALL'],['CA','CANADA'],['US','USA'],['personal','PERSONAL'],['business','BUSINESS']]
    .map(c=>`<span class="chip ${MF===c[0]?'active':''}" onclick="mf('${c[0]}')">${c[1]}</span>`).join('');
  let list=D.matches.filter(x=> MF==='all'||x.country===MF||x.segment===MF);
  const rows=list.map(x=>{
    const cls=x.readiness_pct>=100?'ok':x.readiness_pct>=60?'mid':'no';
    const gap=x.gaps&&x.gaps.length?`<br><b>Next:</b> ${x.gaps[0].criterion} — ${x.gaps[0].fix}`:'';
    const risk=x.risk?`<div class="risk">RISK: ${x.risk}</div>`:'';
    return `<div class="row"><span class="tag ${cls}">${x.readiness_pct}%</span>
      <span class="tag">${x.country}/${x.segment}</span><span class="t">${x.name}</span>
      <div class="s"><b>${x.verdict}.</b> Who: ${x.providers.join(', ')}${gap}</div>${risk}</div>`;
  }).join('');
  return `<div class="panel"><div class="h">Product Match &middot; readiest first</div>${chips}
    <div style="margin-top:6px">${rows}</div><div class="foot">Ranks categories, not a guarantee any lender approves you. ${DISC}</div></div>`;
};
V.roadmap=()=>{
  const ph=D.roadmap.phases.map(p=>`<div class="phase"><div class="pt">PHASE ${p.n} · ${p.title}</div>`+
    p.steps.map(s=>`<div class="row"><div class="t">${s.action}</div>
      <div class="s">${s.why}${s.unlocks&&s.unlocks.length?'<br><b>Unlocks:</b> '+s.unlocks.join(', '):''}</div></div>`).join('')
    +`</div>`).join('');
  return `<div class="panel"><div class="h">Funding Roadmap · ordered game plan</div>${ph}
    <div class="foot">${D.roadmap.note}</div></div>`;
};
V.credit=()=>{
  const au=D.audit.map(a=>{const bad=a.disputable_as_outdated;
    return `<div class="row"><span class="tag ${bad?'no':'ok'}">${bad?'DISPUTABLE':'OK'}</span>
      <span class="t">${a.creditor} (${a.entry_type})</span><div class="s">${a.note||''}</div></div>`;}).join('')
    ||'<div class="s">No credit-report entries tracked yet.</div>';
  const pf=D.portfolios.map(p=>`<div class="row"><span class="t">${p.type}</span>
    <div class="s">Room ${money(p.room)} · value ${money(p.value)}</div></div>`).join('')||'<div class="s">No registered accounts tracked.</div>';
  return `<div class="panel"><div class="h">Reporting-Period Audit (Ontario)</div>${au}</div>
    <div class="panel"><div class="h">Registered Accounts</div>${pf}</div>`;
};
V.reference=()=>{
  const cb=D.reference.crossborder.map(s=>`<div class="row"><div class="s">${s}</div></div>`).join('');
  const bu=Object.keys(D.reference.bureaus).map(k=>`<div class="row"><div class="t">${k}</div>
    <div class="s">${D.reference.bureaus[k].join(' · ')}</div></div>`).join('');
  return `<div class="panel"><div class="h">Credit Bureaus (CA + US, personal & business)</div>${bu}</div>
    <div class="panel"><div class="h">Canada → US Credit Playbook</div>${cb}</div>`;
};

function go(v){
  document.querySelectorAll('.navbtn').forEach(b=>b.classList.toggle('active',b.dataset.v===v));
  const c=document.getElementById('content');
  c.innerHTML=(V[v]||V.overview)();
  c.scrollIntoView({behavior:'smooth',block:'start'});
}
window.go=go;
"""


def render_page_content(data: dict) -> str:
    """Body + inline CSS/JS, WITHOUT <html>/<head>/<body> — for the Artifact wrapper."""
    return ("<style>\n" + CSS + "\n</style>\n" + BODY +
            "\n<script>\nwindow.DATA = " + json.dumps(data) + ";\n</script>\n" +
            "<script>\n" + JS + "\n</script>\n")


def render_standalone(data: dict) -> str:
    """A complete HTML document for saving/opening locally."""
    return ("<!doctype html><html lang='en'><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width, initial-scale=1'>"
            "<title>CoreTrust — Financial Core</title></head><body>"
            + render_page_content(data) + "</body></html>")


def write_dashboard(db, path: str = "dashboard.html") -> str:
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(render_standalone(build_dashboard_data(db)))
    return path
