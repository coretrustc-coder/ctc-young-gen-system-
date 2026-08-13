"""
CoreTrust System (CTC) -- Live Editable Web Dashboard
=====================================================
Same Matrix/machine dashboard, but editable: type your balances, limits, scores
and everything recomputes in the browser -- health score, net worth, plays,
CA/US product matches, and the funding roadmap -- because the whole compute
engine is ported to JavaScript. Then:

  * SAVE writes back to your local SQLite database when the page is served by the
    CLI live server (menu 19). The database mirrors the editor exactly.
  * EXPORT downloads a coretrust_profile.json you can import via menu 13 -> g.
    (Used automatically as a fallback when no local server is present, e.g. the
    published artifact.)

The JS calculations mirror the Python modules (ctc_models / ctc_dashboard /
ctc_match / ctc_roadmap / ctc_rates) so the numbers match.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import date

from ctc_dashboard_web import CSS as BASE_CSS, BODY
from ctc_match import PRODUCTS
from ctc_disputes import ONTARIO_MAX_PERIODS
from ctc_models import CRA_2026_LIMITS
from ctc_rates import (FEDERAL_BRACKETS_2026, ONTARIO_BRACKETS_2026, ONTARIO_SURTAX_T1,
                       ONTARIO_SURTAX_T2, BPA_FEDERAL_2026, BPA_ONTARIO_2026)
import ctc_reference as REF
from ctc_history import get_snapshots, list_goals, deadline_radar
from ctc_compliance import list_dispute_cases, get_audit_log, get_consent, statute_currency
from ctc_entities import business_credit_readiness, list_entities
from ctc_access import ACCESS_CATALOG
from ctc_rates_watch import get as rate_watch_get


def _br(b):
    return [[1e12 if up == float("inf") else up, rate] for up, rate in b]


def _catalog() -> dict:
    return {
        "products": PRODUCTS,
        "ontario_periods": {k: list(v) for k, v in ONTARIO_MAX_PERIODS.items()},
        "cra_limits": CRA_2026_LIMITS,
        "rates": {"fed": _br(FEDERAL_BRACKETS_2026), "on": _br(ONTARIO_BRACKETS_2026),
                  "surtax_t1": ONTARIO_SURTAX_T1, "surtax_t2": ONTARIO_SURTAX_T2,
                  "bpa_fed": BPA_FEDERAL_2026, "bpa_on": BPA_ONTARIO_2026},
        "reference": {"crossborder": REF.CROSSBORDER_PLAYBOOK, "bureaus": REF.BUREAUS},
    }


def build_editable_payload(db) -> dict:
    raw = {
        "personal_accounts": [asdict(a) for a in db.get_personal_accounts()],
        "credit_cards": [asdict(c) for c in db.get_credit_cards()],
        "installment_debts": [asdict(d) for d in db.get_installment_debts()],
        "portfolios": [asdict(p) for p in db.get_portfolios()],
        "income": [asdict(i) for i in db.get_income_sources()],
        "business_accounts": [asdict(b) for b in db.get_business_accounts()],
        "assets": [asdict(a) for a in db.get_assets()],
        "credit_report_entries": [asdict(e) for e in db.get_credit_report_entries()],
        "user_profile": asdict(db.get_user_profile()),
    }
    audit = {
        "snapshots": get_snapshots(db),
        "goals": list_goals(db),
        "deadlines": deadline_radar(db),
        "cases": list_dispute_cases(db),
        "audit_log": get_audit_log(db, 25),
        "consent": get_consent(db),
        "statute_currency": statute_currency(),
        "business_credit": business_credit_readiness(db),
        "entities": list_entities(db),
    }
    return {"generated": date.today().isoformat(), "raw": raw, "catalog": _catalog(),
            "audit": audit, "access": ACCESS_CATALOG, "rate_watch": rate_watch_get(db)}


EDITOR_CSS = """
.editbtns{display:flex;gap:10px;flex-wrap:wrap;margin:10px 0}
.ebtn{font-family:inherit;background:#0c1a15;color:var(--green);border:1px solid var(--green);
  border-radius:9px;padding:9px 14px;cursor:pointer;font-size:12px;letter-spacing:1px;box-shadow:var(--glow)}
.ebtn:hover{background:#12271f}
.ebtn.sm{padding:3px 9px;font-size:11px;box-shadow:none;color:var(--cyan);border-color:var(--edge)}
.ebtn.rm{color:var(--red);border-color:#3a1620}
#liveSummary{font-size:13px;color:var(--text);letter-spacing:1px;padding:10px 12px;border:1px dashed var(--edge);
  border-radius:10px;background:#0a1410}
#liveSummary b{color:var(--green)}
.etable{display:flex;flex-direction:column;gap:8px;margin-top:8px;overflow-x:auto}
.erow{display:flex;gap:8px;align-items:flex-end;flex-wrap:wrap}
.cell{display:flex;flex-direction:column;gap:3px}
.cell label{font-size:10px;color:var(--muted);letter-spacing:1px}
.cell input{font-family:inherit;background:#06100c;color:var(--text);border:1px solid var(--edge);
  border-radius:7px;padding:7px 8px;font-size:12px;min-width:90px}
.cell input:focus{outline:none;border-color:var(--green);box-shadow:0 0 8px rgba(53,245,160,.25)}
.cell input[type=checkbox]{min-width:auto;width:18px;height:18px;accent-color:#35f5a0}
#toast{position:fixed;left:50%;bottom:26px;transform:translateX(-50%);z-index:60;background:#0c1a15;
  border:1px solid var(--green);color:var(--text);padding:12px 18px;border-radius:10px;box-shadow:var(--glow);
  font-size:13px;max-width:90vw;opacity:0;transition:.3s;pointer-events:none}
#toast.show{opacity:1}
.jarvis{border:1px solid var(--green);border-radius:12px;padding:15px 18px;background:linear-gradient(90deg,#0c1a15,#0a1410);box-shadow:var(--glow);margin-bottom:16px;overflow:hidden}
.jarvis .greet{font-size:15px;letter-spacing:2px;color:var(--green);white-space:nowrap;overflow:hidden;border-right:2px solid var(--green);width:0;animation:jtype 1.6s steps(46) forwards, jblink .7s step-end infinite;text-shadow:var(--glow)}
@keyframes jtype{to{width:100%}}
@keyframes jblink{50%{border-color:transparent}}
.jarvis .sub{color:var(--muted);font-size:11px;margin-top:8px;letter-spacing:1px;opacity:0;animation:jfade .6s ease 1.6s forwards}
@keyframes jfade{to{opacity:1}}
.advlog{max-height:340px;overflow-y:auto;display:flex;flex-direction:column;gap:8px;padding-right:4px}
.advmsg{border:1px solid var(--edge);border-radius:10px;padding:10px 12px;background:var(--panel2);font-size:13px;line-height:1.5}
.advmsg.you{border-color:#1c3a4a;background:#0a141a}
.advmsg b{font-size:10px;letter-spacing:1px;color:var(--muted);display:block;margin-bottom:4px}
.advmsg.you b{color:var(--cyan)}.advmsg.advisor b{color:var(--green)}
.advrow{display:flex;gap:8px;margin-top:6px}
.advrow input{flex:1;font-family:inherit;background:#06100c;color:var(--text);border:1px solid var(--edge);border-radius:8px;padding:11px 12px;font-size:13px}
.advrow input:focus{outline:none;border-color:var(--green);box-shadow:0 0 8px rgba(53,245,160,.25)}
.advchips .chip{cursor:pointer}
"""


JS_LIVE = r"""
const PL=window.PAYLOAD, CAT=PL.catalog, R=CAT.rates;
let STATE=PL.raw, D={};
const sum=a=>a.reduce((x,y)=>x+(Number(y)||0),0);
const r2=x=>Math.round(x*100)/100, r1=x=>Math.round(x*10)/10;
const money=n=>'$'+Number(n||0).toLocaleString('en-CA',{maximumFractionDigits:0});
const pct=n=>(n===null||n===undefined)?'n/a':(Number(n).toFixed(1)+'%');
const clamp=(x,lo=0,hi=100)=>Math.max(lo,Math.min(hi,x));
const gcol=s=>s>=70?'var(--green)':s>=55?'var(--amber)':'var(--red)';
const DISC='Educational tool. Not legal, tax, or investment advice. Verify before acting.';

/* ---- element helpers matching Python ---- */
const estMin=c=>{const b=+c.current_balance||0,m=+c.min_payment||0; if(m>0)return r2(m); if(b<=0)return 0; return r2(Math.max(10,0.03*b));};
const estInt=c=>{const b=+c.current_balance||0; if(b<=0)return 0; const rt=(+c.apr>0)?+c.apr:0.1999; return r2(b*rt);};
const utl=c=>{const l=+c.limit_amt||0; return l>0?(+c.current_balance||0)/l:0;};

/* ---- tax (mirror ctc_rates) ---- */
function prog(inc,br){let t=0,lo=0;for(const [up,rate] of br){if(inc<=lo)break;t+=(Math.min(inc,up)-lo)*rate;lo=up;}return t;}
const fedTax=x=>Math.max(0,prog(x,R.fed)-R.bpa_fed*R.fed[0][1]);
const onBasic=x=>Math.max(0,prog(x,R.on)-R.bpa_on*R.on[0][1]);
function surtax(b){let s=0;if(b>R.surtax_t1)s+=0.20*(b-R.surtax_t1);if(b>R.surtax_t2)s+=0.36*(b-R.surtax_t2);return s;}
function totalTax(x){if(x<=0)return 0;const b=onBasic(x);return fedTax(x)+b+surtax(b);}

/* ---- metrics / net worth / cash flow ---- */
function metrics(){
  const cards=STATE.credit_cards,debts=STATE.installment_debts,inc=STATE.income;
  const tb=sum(cards.map(c=>+c.current_balance)),tl=sum(cards.map(c=>+c.limit_amt));
  const u=tl>0?r2(tb/tl*100):0, gross=sum(inc.map(i=>+i.gross_monthly));
  const md=sum(cards.map(estMin))+sum(debts.map(d=>+d.monthly_payment));
  const dti=gross>0?r2(md/gross*100):null;
  return {total_card_balance:r2(tb),total_card_limit:r2(tl),aggregate_utilization_pct:u,
    gross_monthly_income:r2(gross),monthly_debt_obligations:r2(md),estimated_dti_pct:dti};
}
function netWorth(){
  const cash=sum(STATE.personal_accounts.map(a=>+a.balance)),
        bcash=sum(STATE.business_accounts.map(b=>+b.balance)),
        reg=sum(STATE.portfolios.map(p=>+p.market_value)),
        oth=sum(STATE.assets.map(a=>+a.market_value)), ta=cash+bcash+reg+oth,
        cd=sum(STATE.credit_cards.map(c=>+c.current_balance)),
        il=sum(STATE.installment_debts.map(d=>+d.balance)),
        sec=sum(STATE.assets.map(a=>+a.associated_debt)), tl=cd+il+sec,
        liq=sum(STATE.personal_accounts.filter(a=>a.liquid).map(a=>+a.balance))
            +sum(STATE.assets.filter(a=>a.liquid).map(a=>+a.market_value));
  return {assets:{cash_accounts:r2(cash),business_cash:r2(bcash),registered_value:r2(reg),
    other_assets:r2(oth),total:r2(ta)},liabilities:{credit_cards:r2(cd),installment_debts:r2(il),
    secured_on_assets:r2(sec),total:r2(tl)},liquid_assets:r2(liq),net_worth:r2(ta-tl)};
}
function cashFlow(t){
  if(!t||!t.length)return{savings_rate_pct:null};
  const i=sum(t.filter(x=>x.type==='credit').map(x=>x.amount)),
        o=sum(t.filter(x=>x.type==='debit').map(x=>x.amount));
  return {savings_rate_pct:i>0?r2((i-o)/i*100):null};
}

/* ---- scorecard (mirror ctc_dashboard) ---- */
function scorecard(){
  const m=metrics(),nw=netWorth(),p=STATE.user_profile;
  const u=m.aggregate_utilization_pct,dti=m.estimated_dti_pct;
  const us=u<=10?100:clamp(100-(u-10)*1.25);
  const ds=dti==null?50:(dti<=20?100:clamp(100-(dti-20)*2.5));
  const srs=STATE.business_accounts.map(b=>cashFlow(b.transaction_history).savings_rate_pct).filter(s=>s!=null);
  let sr=null,ss=50; if(srs.length){sr=sum(srs)/srs.length;ss=clamp(40+sr*3);}
  const need=(+p.monthly_expenses||m.monthly_debt_obligations);
  let months=null,ef=50; if(need>0){months=nw.liquid_assets/need;ef=clamp(months*(100/6));}
  let reg=50; const usedP=STATE.portfolios.filter(p=>+p.contribution_limit>0);
  if(STATE.portfolios.length){const used=usedP.map(p=>Math.min(1,(+p.contributed_ytd)/(+p.contribution_limit)));
    if(used.length)reg=clamp(sum(used)/used.length*100);}
  let cr=STATE.credit_report_entries.length?100:70;
  const pen={collection:20,judgment:25,bankruptcy_first:30,bankruptcy_second:30,late_payment:10,secured_chargeoff:15};
  STATE.credit_report_entries.forEach(e=>{cr-=(pen[e.entry_type]!==undefined?pen[e.entry_type]:5);});
  cr=clamp(cr);
  const w={utilization:.20,dti:.20,savings:.15,emergency:.15,registered:.10,credit:.20};
  const parts={utilization:us,dti:ds,savings:ss,emergency:ef,registered:reg,credit:cr};
  let comp=0; for(const k in w)comp+=parts[k]*w[k]; comp=r1(comp);
  const grade=comp>=85?'A':comp>=70?'B':comp>=55?'C':comp>=40?'D':'F';
  const co={}; for(const k in parts)co[k]=r1(parts[k]);
  return {composite_score:comp,grade,components:co,weights:w,utilization_pct:u,dti_pct:dti,
    avg_savings_rate_pct:sr==null?null:r1(sr),emergency_fund_months:months==null?null:r1(months)};
}

/* ---- reporting-period audit ---- */
function yrs(iso){const d=new Date(iso+'T00:00:00');return (Date.now()-d.getTime())/(1000*3600*24*365.25);}
function audit(){
  return STATE.credit_report_entries.map(e=>{
    const rule=CAT.ontario_periods[e.entry_type];
    if(!rule)return{creditor:e.creditor,entry_type:e.entry_type,disputable_as_outdated:false,
      note:'No maximum-period rule mapped; review manually.'};
    const maxY=rule[0],age=yrs(e.date_of_last_activity),out=age>maxY;
    return {creditor:e.creditor,entry_type:e.entry_type,age_years:r2(age),max_years:maxY,
      disputable_as_outdated:out,
      note:out?('Appears to exceed the '+maxY+'-year Ontario limit; disputable as outdated.')
              :('Within the '+maxY+'-year Ontario reporting window.')};
  });
}

/* ---- match (mirror ctc_match) ---- */
function matchCtx(){
  const m=metrics(),p=STATE.user_profile,nw=netWorth();
  const gross=m.gross_monthly_income,housing=(+p.monthly_housing_cost||0),md=m.monthly_debt_obligations;
  const need=(+p.monthly_expenses||md),surplus=Math.max(0,nw.liquid_assets-need*3);
  const crypto=sum(STATE.assets.filter(a=>(a.category||'').toLowerCase()==='crypto').map(a=>+a.market_value));
  return {score:Math.max(+p.equifax_score||0,+p.transunion_score||0),
    utilization_pct:m.aggregate_utilization_pct,dti_pct:m.estimated_dti_pct,
    gds_pct:gross>0?r1(housing/gross*100):null,tds_pct:gross>0?r1((housing+md)/gross*100):null,
    open_collections:STATE.credit_report_entries.filter(e=>e.entry_type==='collection').length,
    liquid:nw.liquid_assets,surplus_cash:surplus,crypto_value:crypto,
    business_exists:STATE.business_accounts.length>0||(+p.business_bank_months||0)>0||(+p.business_revenue_monthly||0)>0,
    us_foundation:!!(p.us_bank_account&&p.us_tax_id&&p.us_address),
    time_in_business_years:+p.time_in_business_years||0,business_bank_months:+p.business_bank_months||0,
    revenue_monthly:+p.business_revenue_monthly||0};
}
function evaluate(prod,ctx){
  const c=[]; const cr=(l,m,a,t,f)=>c.push({criterion:l,met:m,actual:a,target:t,fix:f});
  if(prod.us){const m=ctx.us_foundation;cr('US foundation (US bank + ITIN/SSN + US address)',m,m?'yes':'not set','established','Build the cross-border foundation first (reference).');}
  if(prod.needs_business){const m=ctx.business_exists;cr('Registered business + account',m,m?'yes':'no','yes','Register the business and open a dedicated business account.');}
  if(prod.min_score){const s=ctx.score,m=s>0?(s>=prod.min_score):null;cr('Credit score',m,s>0?String(s):'not set','>= '+prod.min_score,'Raise score: on-time payments, low utilization, aging accounts, dispute genuine errors.');}
  if(prod.max_util!=null){const u=ctx.utilization_pct;cr('Card utilization',u<prod.max_util,u.toFixed(1)+'%','< '+prod.max_util+'%','Pay balances down (ideally <10% before statement).');}
  if(prod.max_dti!=null){const d=ctx.dti_pct;cr('Debt-to-income',(d!=null&&d<prod.max_dti),d==null?'n/a':d.toFixed(1)+'%','< '+prod.max_dti+'%','Increase documented income or reduce monthly debt.');}
  if(prod.max_gds!=null){const g=ctx.gds_pct;cr('Gross debt service (GDS)',(g!=null&&g<=prod.max_gds),g==null?'n/a':g.toFixed(1)+'%','<= '+prod.max_gds+'%','Lower housing cost, raise income, or add down payment.');}
  if(prod.max_tds!=null){const t=ctx.tds_pct;cr('Total debt service (TDS)',(t!=null&&t<=prod.max_tds),t==null?'n/a':t.toFixed(1)+'%','<= '+prod.max_tds+'%','Pay down debts or raise documented income.');}
  if(prod.clear_collections){const col=ctx.open_collections;cr('No open collections',col===0,String(col),'0','Resolve, validate, or dispute genuinely inaccurate/outdated collections.');}
  if(prod.min_time_in_business){const y=ctx.time_in_business_years;cr('Time in business',y>=prod.min_time_in_business,y.toFixed(1)+' yr','>= '+prod.min_time_in_business+' yr','Build operating history and steady revenue.');}
  if(prod.min_business_months){const mo=ctx.business_bank_months;cr('Business account seasoning',mo>=prod.min_business_months,mo+' mo','>= '+prod.min_business_months+' mo','Keep the business account active and funded.');}
  if(prod.needs_revenue){const rev=ctx.revenue_monthly;cr('Documented revenue',rev>0,'$'+Math.round(rev)+'/mo','documented (6-12 mo)','Keep clean statements/financials showing steady revenue.');}
  if(prod.needs_liquid){cr('Cash available',ctx.liquid>0,'$'+Math.round(ctx.liquid)+' liquid','some (deploy / down payment)','Build liquid savings.');}
  if(prod.needs_crypto){const cv=ctx.crypto_value;cr('Digital-asset collateral',cv>0,'$'+Math.round(cv),'> $0 held on a regulated platform','Hold digital assets on a regulated platform to use as collateral.');}
  if(!c.length)cr('Eligibility',true,'open','KYC only','Complete standard KYC/onboarding.');
  const met=c.filter(x=>x.met===true).length,tot=c.length,rd=tot?Math.round(met/tot*100*10)/10:0;
  return {id:prod.id,country:prod.country,segment:prod.segment,category:prod.category,name:prod.name,
    providers:prod.providers||[],risk:prod.risk||'',readiness_pct:rd,
    verdict:rd>=100?'Ready now':rd>=60?'Close -- close the gaps':'Build first',
    criteria:c,gaps:c.filter(x=>x.met!==true)};
}
function matchAll(country,segment){
  const ctx=matchCtx();
  let res=CAT.products.filter(p=>(!country||p.country===country)&&(!segment||p.segment===segment)).map(p=>evaluate(p,ctx));
  res.sort((a,b)=>b.readiness_pct-a.readiness_pct||a.country.localeCompare(b.country)||a.segment.localeCompare(b.segment)||a.category.localeCompare(b.category));
  return res;
}

/* ---- plays (mirror ctc_dashboard) ---- */
function plays(){
  const out=[],m=metrics(),nw=netWorth(),p=STATE.user_profile,cards=STATE.credit_cards;
  const ports={}; STATE.portfolios.forEach(x=>ports[x.portfolio_type]=x);
  const rem=x=>x?((+x.contribution_limit||0)-(+x.contributed_ytd||0)):0;
  const need=(+p.monthly_expenses||m.monthly_debt_obligations),buf=need*3,surp=Math.max(0,nw.liquid_assets-buf);
  const carry=cards.filter(c=>+c.current_balance>0);
  if(carry.length&&surp>0){
    const worst=carry.reduce((a,b)=>estInt(b)>estInt(a)?b:a);
    const pay=Math.min(surp,+worst.current_balance),rt=(+worst.apr>0)?+worst.apr:0.1999;
    out.push({priority:1,title:'Pay down '+worst.institution+' card with surplus cash',
      why:'You have ~'+money(surp)+' above a 3-month buffer, and this card carries a balance at ~'+(rt*100).toFixed(1)+'%. Paying it is a guaranteed, risk-free return equal to the interest rate.',
      estimated_benefit:'~'+money(pay*rt)+'/yr interest avoided on '+money(pay),
      action:'Move surplus cash to the highest-rate balance first; keep the buffer intact.'});
  }
  const hi=cards.filter(c=>utl(c)>0.10);
  if(hi.length)out.push({priority:2,title:'Report lower utilization by paying before statement dates',
    why:'Bureaus see the balance on your statement date. Paying a card down before that date reports lower utilization, which helps your score.',
    estimated_benefit:'Score/utilization improvement (no cash cost)',
    action:'For '+hi.map(c=>c.institution).join(', ')+': pay down 1-3 days before the statement date.'});
  const fhsa=ports['FHSA'],tfsa=ports['TFSA'];
  if(surp>0&&((fhsa&&rem(fhsa)>0)||(tfsa&&rem(tfsa)>0))){
    const tgt=(fhsa&&rem(fhsa)>0)?fhsa:tfsa,room=rem(tgt);
    out.push({priority:3,title:'Move idle cash into '+tgt.portfolio_type+' room',
      why:'You have '+money(room)+' of '+tgt.portfolio_type+' room and surplus cash in taxable accounts. Registered accounts shelter growth from tax'+(tgt.portfolio_type==='FHSA'?' and FHSA contributions are also deductible.':'.'),
      estimated_benefit:'Tax-sheltered growth on up to '+money(Math.min(room,surp)),
      action:'Confirm room in CRA MyAccount, then contribute within the '+tgt.portfolio_type+' limit.'});
  }
  const rrsp=ports['RRSP'],ga=m.gross_monthly_income*12;
  if(rrsp&&rem(rrsp)>0&&ga>0){
    let s=Math.min(rem(rrsp),surp>0?surp:rem(rrsp)); s=Math.min(s,ga);
    if(s>0){const ben=Math.round(totalTax(ga)-totalTax(Math.max(0,ga-s)));
      out.push({priority:4,title:"Use RRSP room to reduce this year's income tax",
        why:'With '+money(rem(rrsp))+' of RRSP room, a '+money(s)+' contribution could cut this year\'s tax by ~'+money(ben)+' (estimate).',
        estimated_benefit:'~'+money(ben)+' estimated tax reduction',
        action:'Discuss timing/amount with a CPA; contributions reduce taxable income now.'});}
  }
  if(need>0){const mo=nw.liquid_assets/need; if(mo<3){const gap=Math.round(buf-nw.liquid_assets);
    out.push({priority:5,title:'Build your emergency fund to 3+ months',
      why:'Liquid savings cover ~'+mo.toFixed(1)+' months. A thin buffer forces high-interest borrowing when something breaks.',
      estimated_benefit:'Resilience; avoids costly borrowing (~'+money(gap)+' gap)',
      action:'Automate transfers to a HISA until you reach ~3 months of costs.'});}}
  const eq=sum(STATE.assets.map(a=>(+a.market_value||0)-(+a.associated_debt||0)));
  if(carry.length&&eq>5000)out.push({priority:6,title:'Consider secured credit to lower interest on existing debt',
    why:'You hold ~'+money(eq)+' of asset equity. Secured credit (HELOC or GIC-secured LOC) usually carries a much lower rate than cards, so consolidating high-interest balances can cut interest cost.',
    estimated_benefit:'Lower interest rate on consolidated balances',
    action:'RISK: this moves unsecured debt onto an asset -- missing payments can put the asset at risk, and volatile assets (e.g. crypto) can trigger margin calls. Model it and consult a licensed advisor first.'});
  if(STATE.business_accounts.length&&(+p.business_bank_months||0)<6)out.push({priority:7,
    title:'Season your business banking and build business credit',
    why:'Lenders want a dedicated, seasoned business account and a business credit history separate from your personal file.',
    estimated_benefit:'Improves business funding readiness',
    action:'Keep the business account active 6+ months; pay any net-30 vendors early.'});
  const od=audit().filter(a=>a.disputable_as_outdated);
  if(od.length)out.push({priority:8,title:'Dispute '+od.length+' outdated credit entr'+(od.length===1?'y':'ies'),
    why:"These appear to exceed Ontario's maximum reporting period and are legitimately disputable as outdated.",
    estimated_benefit:'Potential score improvement from removing outdated items',
    action:'Verify dates on your report, then use the dispute letter tool (aged_item).'});
  out.sort((a,b)=>a.priority-b.priority); return out;
}

/* ---- roadmap (mirror ctc_roadmap) ---- */
function roadmap(){
  const ctx=matchCtx(),res=matchAll(),by={}; res.forEach(r=>by[r.id]=r);
  const near=res.filter(r=>r.readiness_pct>=60&&r.readiness_pct<100),ph=[];
  let st=[]; const od=audit().filter(a=>a.disputable_as_outdated);
  if(ctx.open_collections>0)st.push({action:'Resolve or dispute the open collection(s) on your file',why:'An open collection is the main gap holding back your personal loan, line of credit, and mortgage.',unlocks:['Personal loan','Personal LOC','Mortgage']});
  if(od.length)st.push({action:'Dispute '+od.length+' outdated entry(ies) past the Ontario limit',why:'Removing outdated items can lift your score.',unlocks:['Higher score across products']});
  if(ctx.utilization_pct>30)st.push({action:'Bring card utilization under 30% (ideally <10% before statement dates)',why:'Lower reported utilization improves your score and approvals.',unlocks:['Better cards','Lines of credit']});
  if(st.length)ph.push({n:ph.length+1,title:'Clear the blockers',steps:st});
  const ord=['ca_p_hisa','ca_b_bank','ca_p_card','ca_b_card','ca_p_secured','ca_b_merchant'];
  const picks=ord.filter(i=>by[i]&&by[i].readiness_pct>=100).map(i=>by[i]);
  if(picks.length)ph.push({n:ph.length+1,title:"Activate what you're ready for (Canada)",steps:picks.map(p=>({action:'Open: '+p.name,why:'Ready now via '+p.providers.slice(0,3).join(', ')+'.',unlocks:[p.category]}))});
  if(near.length)ph.push({n:ph.length+1,title:'Close the gaps on near-ready facilities',steps:near.slice(0,6).map(r=>{const g=r.gaps[0];return{action:'Get ready for '+r.name+' ('+Math.round(r.readiness_pct)+'%)',why:g?g.fix:'Close the remaining criteria.',unlocks:[r.category]};})});
  if(!ctx.us_foundation)ph.push({n:ph.length+1,title:'Build the US cross-border foundation',steps:[
    {action:"Open a US account via your Canadian bank's US affiliate (RBC Bank, TD, BMO, CIBC Bank USA, Natbank, Desjardins)",why:'Typically no SSN required; it anchors your US foundation.',unlocks:['US banking']},
    {action:'Establish a US mailing address',why:'Required for US applications.',unlocks:['US applications']},
    {action:'Get your first US card — Amex Global Transfer or an ITIN-friendly secured card',why:'Starts a US credit file; Canadian history does not transfer.',unlocks:['US credit history']},
    {action:"Apply for an ITIN (IRS Form W-7) if you'll file/earn in the US",why:'Several issuers accept an ITIN in place of an SSN.',unlocks:['US cards & loans']}]});
  ph.push({n:ph.length+1,title:'Scale into US personal & business credit',steps:[
    {action:'Pay the US card in full, on time, for 6-12 months',why:'US FICO reaches usable (~640) in 4-6 months and good (670+) in 9-12.',unlocks:['US HYSA','US cards','US auto loan']},
    {action:'For US business: form a US LLC/Corp, get an EIN, open a US business account, and get a US D-U-N-S number',why:'Builds a US business credit file (PAYDEX).',unlocks:['US business banking, cards, loans/SBA']}]});
  st=[{action:'Keep any crypto on a regulated platform (Wealthsimple, Bitbuy, Kraken, Coinbase) with clean records for the CRA',why:'KYC-compliant custody and accurate tax reporting.',unlocks:['Digital-asset tracking']}];
  if(ctx.crypto_value>0)st.push({action:'Only consider a crypto-backed loan with a large safety margin',why:'RISK: volatility can trigger margin calls and forced liquidation; not a tax-avoidance strategy.',unlocks:['Liquidity without selling (high risk)']});
  ph.push({n:ph.length+1,title:'Digital assets (optional, risk-managed)',steps:st});
  return {phases:ph};
}

/* ---- recompute ---- */
function recompute(){
  const p=STATE.user_profile;
  D={generated:PL.generated,
    profile:{best_score:Math.max(+p.equifax_score||0,+p.transunion_score||0),
             us_foundation:!!(p.us_bank_account&&p.us_tax_id&&p.us_address)},
    metrics:metrics(),net_worth:netWorth(),scorecard:scorecard(),plays:plays(),
    matches:matchAll(),roadmap:roadmap(),audit:audit(),
    portfolios:STATE.portfolios.map(p=>({type:p.portfolio_type,room:r2((+p.contribution_limit||0)-(+p.contributed_ytd||0)),value:+p.market_value||0})),
    reference:CAT.reference};
  window.DATA=D;
}

/* ---- matrix + boot ---- */
(function(){const c=document.getElementById('matrix'),x=c.getContext('2d');
  const ch='01<>{}[]$#%&+=/\\ABCDEF0123456789¥€£₿アカサタナ'.split('');let cols,dr;
  function sz(){c.width=innerWidth;c.height=innerHeight;cols=Math.floor(c.width/14);dr=Array(cols).fill(1);}
  sz();addEventListener('resize',sz);
  setInterval(function(){x.fillStyle='rgba(5,8,11,0.08)';x.fillRect(0,0,c.width,c.height);x.font='13px monospace';
    for(let i=0;i<cols;i++){x.fillStyle=Math.random()>0.975?'#8fffd0':'#1fae7a';
      x.fillText(ch[Math.floor(Math.random()*ch.length)],i*14,dr[i]*14);
      if(dr[i]*14>c.height&&Math.random()>0.975)dr[i]=0;dr[i]++;}},55);})();
(function(){const L=['> initializing CORETRUST core ...','> mounting local ledger [OK]',
  '> loading credit bureaus // Equifax·TransUnion [OK]','> arming live compute engine [OK]',
  '> ranking product matches (CA/US · personal/business) ...','> compiling funding roadmap ...',
  '> editor online — type to recompute','> SYSTEM READY'];
  const lg=document.getElementById('bootlog'),f=document.getElementById('bootfill'),pe=document.getElementById('bootpct');
  let i=0;document.getElementById('gen').textContent='build '+PL.generated;
  (function st(){if(i<L.length){lg.textContent+=L[i]+'\n';const p=Math.round((i+1)/L.length*100);
    f.style.width=p+'%';pe.textContent=p+'%';i++;setTimeout(st,230+Math.random()*160);}
   else setTimeout(function(){document.getElementById('boot').classList.add('hidden');
     document.getElementById('app').classList.remove('hidden');recompute();go('advisor');},450);})();})();

/* ---- nav (6 consolidated widgets) ---- */
const NAV=[['advisor','&#9673;','Advisor'],['wealth','&#9636;','Wealth'],['credit','&#10084;','Credit'],
 ['funding','&#9672;','Funding'],['access','&#9731;','Access'],['vault','&#9998;','Vault']];
document.getElementById('sidebar').innerHTML=NAV.map(n=>`<div class="navbtn" data-v="${n[0]}" onclick="go('${n[0]}')"><span class="ic">${n[1]}</span>${n[2]}</div>`).join('');

/* ---- ui helpers ---- */
function bar(l,v,mx,col){const w=clamp((v/mx)*100);return `<div class="bar"><div class="bar-l">${l}</div><div class="bar-t"><div class="bar-f" style="width:${w}%;background:${col||'var(--green)'}"></div></div><div class="bar-v">${typeof v==='number'?Math.round(v):v}</div></div>`;}
function gauge(s,g){return `<div class="gauge" style="background:conic-gradient(${gcol(s)} ${s*3.6}deg,#12201a 0)"><div class="gauge-inner"><div class="gauge-num" style="color:${gcol(s)}">${s}</div><div class="gauge-grade">GRADE ${g}</div></div></div>`;}
function tile(k,v,cls){return `<div class="tile"><div class="k">${k}</div><div class="v ${cls||''}">${v}</div></div>`;}
const SPK='▁▂▃▄▅▆▇█';
function spark(a){a=a.filter(v=>v!=null&&!isNaN(v));if(!a.length)return '';const lo=Math.min(...a),hi=Math.max(...a);if(hi===lo)return SPK[3].repeat(a.length);return a.map(v=>SPK[Math.round((v-lo)/(hi-lo)*(SPK.length-1))]).join('');}

/* ---- payoff + tax (client-side) ---- */
function debtRecords(){const d=[];
  STATE.installment_debts.forEach(x=>d.push({name:(x.lender||'loan')+' ('+(x.debt_type||'')+')',balance:+x.balance||0,rate:+x.interest_rate||0,min:+x.monthly_payment||0}));
  STATE.credit_cards.forEach(c=>{if(+c.current_balance>0)d.push({name:(c.institution||'card')+' card',balance:+c.current_balance,rate:(+c.apr>0)?(+c.apr*100):19.99,min:estMin(c)});});
  return d;}
function payoffPlan(budget,method){let debts=debtRecords();if(!debts.length)return{empty:true};
  const totalMin=sum(debts.map(d=>d.min));if(budget<totalMin)return{under:true,totalMin:r2(totalMin)};
  debts=debts.slice().sort((a,b)=>method==='snowball'?a.balance-b.balance:b.rate-a.rate);
  const bals=debts.map(d=>d.balance),rates=debts.map(d=>d.rate/100/12),mins=debts.map(d=>d.min),payoff={};
  let months=0,interest=0;
  while(bals.some(b=>b>0)&&months<1200){months++;
    for(let i=0;i<bals.length;i++)if(bals[i]>0){const it=bals[i]*rates[i];bals[i]+=it;interest+=it;}
    let bud=budget;
    for(let i=0;i<bals.length;i++)if(bals[i]>0){const p=Math.min(mins[i],bals[i]);bals[i]-=p;bud-=p;}
    for(let i=0;i<bals.length;i++)if(bals[i]>0&&bud>0){const p=Math.min(bud,bals[i]);bals[i]-=p;bud-=p;}
    for(let i=0;i<bals.length;i++)if(bals[i]<=0&&!(i in payoff)){payoff[i]=months;bals[i]=0;}}
  return {months,interest:r2(interest),totalMin:r2(totalMin),budget:r2(budget),
    order:debts.map((d,i)=>({name:d.name,balance:r2(d.balance),rate:d.rate,payoff:payoff[i]}))};}
function taxSnapshot(inc){const t=totalTax(inc);return {tax:Math.round(t),avg:inc>0?r1(t/inc*100):0,marg:r1((totalTax(inc+100)-t)/100*100)};}

/* ---- editor schema ---- */
const rid=()=>Math.random().toString(36).slice(2,8);
const SCHEMA=[
 ['wealth','personal_accounts','Cash accounts',[['institution','Institution','text'],['account_type','Type','text'],['balance','Balance','num'],['liquid','Liquid','bool']],()=>({id:'acc_'+rid(),institution:'',account_type:'Chequing',balance:0,liquid:true,last_updated:''})],
 ['wealth','installment_debts','Loans',[['lender','Lender','text'],['debt_type','Type','text'],['balance','Balance','num'],['monthly_payment','Monthly','num'],['interest_rate','Rate %','num']],()=>({id:'debt_'+rid(),lender:'',debt_type:'',balance:0,monthly_payment:0,interest_rate:0})],
 ['wealth','portfolios','Registered (TFSA/RRSP/FHSA)',[['portfolio_type','Type','text'],['contribution_limit','Room','num'],['contributed_ytd','Contributed','num'],['market_value','Value','num']],()=>({portfolio_type:'TFSA',contribution_limit:0,contributed_ytd:0,last_contribution:'',market_value:0})],
 ['wealth','income','Income',[['source','Source','text'],['gross_monthly','Gross/mo','num'],['net_monthly','Net/mo','num']],()=>({source:'',gross_monthly:0,net_monthly:0,next_pay_date:''})],
 ['wealth','assets','Assets (incl. crypto/IP)',[['name','Name','text'],['category','Category','text'],['market_value','Value','num'],['associated_debt','Debt','num'],['liquid','Liquid','bool']],()=>({id:'asset_'+rid(),name:'',category:'Other',market_value:0,associated_debt:0,liquid:false})],
 ['wealth','business_accounts','Business accounts',[['institution','Institution','text'],['account_type','Type','text'],['balance','Balance','num']],()=>({institution:'',account_type:'Business Operating',balance:0,transaction_history:[]})],
 ['credit','credit_cards','Credit cards',[['institution','Institution','text'],['limit_amt','Limit','num'],['current_balance','Balance','num'],['apr','APR (0.19)','num'],['min_payment','Min pay','num']],()=>({id:'card_'+rid(),institution:'',secured:false,limit_amt:0,current_balance:0,statement_date:'',utilization_history:[],last_limit_increase:'',min_payment:0,apr:0})],
 ['credit','credit_report_entries','Credit-file entries',[['creditor','Creditor','text'],['entry_type','Type','text'],['status','Status','text'],['reported_balance','Balance','num'],['date_of_last_activity','Last activity','date']],()=>({id:'cre_'+rid(),bureau:'Equifax',creditor:'',entry_type:'collection',status:'',reported_balance:0,date_of_last_activity:'2020-01-01'})]
];
const PROFILE_FIELDS=[['equifax_score','Equifax score','num'],['transunion_score','TransUnion score','num'],['monthly_housing_cost','Housing/mo','num'],['monthly_expenses','Living exp/mo','num'],['time_in_business_years','Yrs in business','num'],['business_revenue_monthly','Biz rev/mo','num'],['business_bank_months','Biz acct months','num'],['us_bank_account','US bank acct','bool'],['us_tax_id','US ITIN/SSN','bool'],['us_address','US address','bool']];
function cell(sec,i,f,lab,typ,val){
  if(typ==='bool')return `<div class="cell"><label>${lab}</label><input type="checkbox" ${val?'checked':''} oninput="upd('${sec}',${i},'${f}','bool',this.checked)"></div>`;
  const it=typ==='num'?'number':(typ==='date'?'date':'text');
  return `<div class="cell"><label>${lab}</label><input type="${it}" value="${val==null?'':String(val).replace(/"/g,'&quot;')}" oninput="upd('${sec}',${i},'${f}','${typ}',this.value)"></div>`;}
function liveSummary(){return `<b>SCORE</b> ${D.scorecard.composite_score} (${D.scorecard.grade}) &nbsp;&middot;&nbsp; <b>NET WORTH</b> ${money(D.net_worth.net_worth)} &nbsp;&middot;&nbsp; <b>UTIL</b> ${pct(D.metrics.aggregate_utilization_pct)} &nbsp;&middot;&nbsp; <b>DTI</b> ${pct(D.metrics.estimated_dti_pct)} &nbsp;&middot;&nbsp; <b>READY</b> ${D.matches.filter(x=>x.readiness_pct>=100).length}/${D.matches.length}`;}
function editorHeader(){return `<div class="panel"><div class="h">Live Editor — type to recompute</div><div class="liveSummary" id="liveSummary">${liveSummary()}</div><div class="editbtns"><button class="ebtn" onclick="save()">&#11015; SAVE TO DATABASE</button><button class="ebtn" onclick="exportJson()">&#8681; EXPORT JSON</button></div><div class="foot">SAVE writes back to your local database via the CLI live server (menu 19); otherwise it downloads a JSON to import (menu 13 &rarr; g).</div></div>`;}
function editorTables(group){let h='';for(const rowdef of SCHEMA){const g=rowdef[0],key=rowdef[1],label=rowdef[2],fields=rowdef[3];if(g!==group)continue;
  h+=`<div class="panel"><div class="h">${label} <button class="ebtn sm" onclick="addRow('${key}')">+ add</button></div><div class="etable">`;
  STATE[key].forEach((row,i)=>{h+=`<div class="erow">`+fields.map(fd=>cell(key,i,fd[0],fd[1],fd[2],row[fd[0]])).join('')+`<button class="ebtn sm rm" onclick="delRow('${key}',${i})">&#10005;</button></div>`;});
  h+=`</div></div>`;}
  if(group==='credit')h+=`<div class="panel"><div class="h">Profile & US foundation</div><div class="etable"><div class="erow">`+PROFILE_FIELDS.map(fd=>cell('__profile__',0,fd[0],fd[1],fd[2],STATE.user_profile[fd[0]])).join('')+`</div></div></div>`;
  return h;}

/* ---- payoff live state ---- */
let PB=null;
function payoffHtml(){const debts=debtRecords();if(!debts.length)return '<div class="s">No debts tracked.</div>';
  const r=payoffPlan(PB,'avalanche');
  if(r.under)return `<div class="s">Budget below total minimums (${money(r.totalMin)}). Raise it.</div>`;
  return `<div class="s">Budget ${money(r.budget)} (min ${money(r.totalMin)}) &middot; avalanche &rarr; debt-free in ~${r.months} months, interest ~${money(r.interest)}</div>`+r.order.map(d=>`<div class="row"><span class="t">${d.name}</span><div class="s">${money(d.balance)} @ ${d.rate.toFixed(2)}% &rarr; paid ~month ${d.payoff||'—'}</div></div>`).join('');}
window.updBudget=v=>{PB=parseFloat(v)||0;const o=document.getElementById('payoffOut');if(o)o.innerHTML=payoffHtml();};

/* ---- 6 consolidated widgets ---- */
const V={};

/* ---- advisor (first widget) ---- */
let ADVLOG=[];
const usFound=()=>{const p=STATE.user_profile;return !!(p.us_bank_account&&p.us_tax_id&&p.us_address);};
const bizExists=()=>{const p=STATE.user_profile;return STATE.business_accounts.length>0||(+p.business_bank_months||0)>0||(+p.business_revenue_monthly||0)>0;};
function advReport(){
  const A=PL.audit,s=D.scorecard,nw=D.net_worth,m=D.metrics;
  const snaps=A.snapshots||[],last=snaps.length?snaps[snaps.length-1]:null;
  const prev=last
    ? `<div class="s">As of <b>${last.date}</b>: score <b>${last.composite_score}</b>, net worth <b>${money(last.net_worth)}</b>, utilization <b>${last.utilization}%</b>, DTI <b>${last.dti}%</b>.</div>`
    : `<div class="s">No prior statement snapshot yet — take one in the CLI (menu 20) to start your history.</div>`;
  const dl=(A.deadlines||[]).slice(0,4).map(d=>`<div class="row"><span class="tag ${d.overdue?'no':'mid'}">${d.overdue?'OVERDUE':'in '+d.days+'d'}</span><span class="t">${d.label}</span><div class="s">${d.date}</div></div>`).join('')||'<div class="s">No upcoming dates in range.</div>';
  const rw=PL.rate_watch;
  const rline=rw?`Bank of Canada overnight rate <b>${(+rw.overnight).toFixed(2)}%</b> · prime <b>${(+rw.prime).toFixed(2)}%</b>${rw.prime_derived?' (est.)':''} — as of ${rw.as_of}`:'Run the CLI advisor (menu 27) to pull the current Bank of Canada overnight rate and prime.';
  return `<div class="panel" style="margin-bottom:16px;border-color:var(--cyan)"><div class="h" style="color:var(--cyan)">Rate watch</div><div class="s" style="color:var(--cyan)">${rline}</div><div class="s" style="margin-top:8px">${rateImpactLine()}</div></div>
  <div class="grid g2">
    <div class="panel"><div class="h">Previous statement report</div>${prev}
      <div class="s" style="margin-top:8px"><b>Now:</b> score ${s.composite_score} (${s.grade}) · net worth ${money(nw.net_worth)} · util ${pct(s.utilization_pct)} · DTI ${pct(s.dti_pct)} · ${D.matches.filter(x=>x.readiness_pct>=100).length}/${D.matches.length} products ready.</div></div>
    <div class="panel"><div class="h">Upcoming</div>${dl}</div></div>`;
}
function advLogHtml(){return ADVLOG.map(x=>`<div class="advmsg ${x.who}"><b>${x.who==='you'?'YOU':'◈ ADVISOR'}</b><div>${x.t}</div></div>`).join('');}
function svgSpark(series,color){const v=series.filter(x=>x!=null);if(v.length<2)return '';
  const w=120,h=26,lo=Math.min(...v),hi=Math.max(...v),rng=(hi-lo)||1;
  const pts=v.map((x,i)=>[i/(v.length-1)*w,h-((x-lo)/rng)*(h-5)-2.5]);
  const line=pts.map((p,i)=>(i?'L':'M')+p[0].toFixed(1)+' '+p[1].toFixed(1)).join(' ');
  return `<svg viewBox="0 0 ${w} ${h}" width="100%" height="26" preserveAspectRatio="none"><path d="${line} L ${w} ${h} L 0 ${h} Z" fill="${color}" opacity="0.10"/><path d="${line}" fill="none" stroke="${color}" stroke-width="1.5"/></svg>`;}
function deltaChip(series,upGood,isMoney){const v=series.filter(x=>x!=null);
  if(v.length<2)return `<div class="d flat">no trend yet</div>`;
  const diff=v[v.length-1]-v[0],cls=diff===0?'flat':((diff>0)===upGood?'up':'dn'),arrow=diff>0?'▲':diff<0?'▼':'■';
  const val=isMoney?money(Math.abs(diff)):(Math.round(Math.abs(diff)*10)/10);
  return `<div class="d ${cls}">${arrow} ${val} <span style="color:var(--muted)">since first snapshot</span></div>`;}
function rateVarDebt(){return sum(STATE.installment_debts.filter(d=>/loc|heloc|line|variable|prime/i.test((d.debt_type||'')+' '+(d.lender||''))).map(d=>+d.balance||0));}
function rateHisa(){return sum(STATE.personal_accounts.filter(a=>a.liquid&&/sav|hisa|high.?interest/i.test((a.account_type||'')+' '+(a.institution||''))).map(a=>+a.balance||0));}
function rateImpactLine(){const vd=rateVarDebt(),hs=rateHisa(),d=0.0025,dc=vd*d,he=hs*d;
  if(vd===0&&hs===0)return 'Rate impact: no prime-linked debt or high-interest savings tracked — a policy-rate move barely touches your tracked balances.';
  if(vd===0)return `Rate impact: a 0.25% BoC hike lifts the yield on your ${money(hs)} in savings by ~${money(he)}/yr (a cut lowers it); you have no prime-linked debt exposed.`;
  if(hs===0)return `Rate impact: a 0.25% BoC hike raises interest on your ${money(vd)} prime-linked debt by ~${money(dc)}/yr (a cut lowers it); no rate-sensitive savings tracked.`;
  const net=he-dc;return `Rate impact: a 0.25% BoC hike — prime-linked debt (${money(vd)}) costs ~${money(dc)}/yr more, savings (${money(hs)}) earns ~${money(he)}/yr more → net ~${money(Math.abs(net))}/yr ${net>=0?'ahead':'behind'}. A cut is the reverse.`;}
V.advisor=()=>{
  const qs=['What should I do next?','Am I ready for a mortgage?','What Black-entrepreneur programs can I get?','What should I pay off first?','How do I build US credit?','What is my TFSA/RRSP room?'];
  const chips=qs.map(q=>`<span class="chip" onclick="advAsk('${q}')">${q}</span>`).join('');
  const s=D.scorecard,nw=D.net_worth,snaps=(PL.audit.snapshots||[]);
  const nwS=snaps.map(x=>x.net_worth),scS=snaps.map(x=>x.composite_score);
  const hero=`<div class="panel"><div class="h">Overview</div>
    <div class="grid" style="grid-template-columns:auto 1fr;gap:24px;align-items:center">
      <div style="text-align:center">${gauge(s.composite_score,s.grade)}<div class="foot" style="margin-top:6px">Financial health</div></div>
      <div class="statrow" style="grid-template-columns:repeat(3,1fr)">
        <div class="stat"><div class="k">Net worth</div><div class="v green">${money(nw.net_worth)}</div>${deltaChip(nwS,true,true)}<div class="spk">${svgSpark(nwS,'var(--green)')}</div></div>
        <div class="stat"><div class="k">Credit score</div><div class="v cyan">${D.profile.best_score||'—'}</div>${deltaChip(scS,true,false)}<div class="spk">${svgSpark(scS,'var(--cyan)')}</div></div>
        <div class="stat"><div class="k">Liquid cash</div><div class="v">${money(nw.liquid_assets)}</div><div class="d flat">available now</div></div>
      </div></div></div>`;
  return `<div class="jarvis"><div class="greet">◈ CORETRUST ADVISOR — GREETINGS. WEALTH IS ON THE WAY.</div>
    <div class="sub">Local advisor — instant answers from your live data, offline. For web research on the live economy, run the CLI agent (menu 27).</div></div>
  ${hero}
  ${advReport()}
  <div class="panel"><div class="h">Advisor chat</div>
    <div class="advlog" id="advLog">${advLogHtml()||'<div class="s">Ask about your money, credit, funding readiness, programs, or your next move.</div>'}</div>
    <div class="advchips" style="margin:10px 0">${chips}</div>
    <div class="advrow"><input id="advIn" placeholder="Ask the advisor…" onkeydown="if(event.key==='Enter')advisorSend()"><button class="ebtn" onclick="advisorSend()">SEND</button></div>
    <div class="foot">Educational only — not legal, tax, or investment advice. Verify before acting.</div></div>`;
};
window.advisorSend=()=>{const i=document.getElementById('advIn');if(!i)return;const q=(i.value||'').trim();if(!q)return;
  ADVLOG.push({who:'you',t:q});ADVLOG.push({who:'advisor',t:advisorReply(q)});i.value='';
  const l=document.getElementById('advLog');if(l){l.innerHTML=advLogHtml();l.scrollTop=l.scrollHeight;}};
window.advAsk=q=>{const i=document.getElementById('advIn');if(i)i.value=q;advisorSend();};
function advisorReply(q){
  const t=q.toLowerCase(),s=D.scorecard,nw=D.net_worth,m=D.metrics;
  const usf=usFound(),biz=bizExists();
  const has=(...k)=>k.some(x=>t.includes(x));
  if(has('black','bep','face','minority','grant','opportunity fund')){
    const list=PL.access.filter(e=>e.black_focus).map(e=>{const ok=e.country==='CA'?(e.segment!=='business'||biz):usf;return `<div class="row"><span class="tag ${ok?'ok':'mid'}">${ok?'ELIGIBLE':'prereq'}</span><span class="t">${e.name}</span><div class="s">${e.access} — ${e.eligibility}</div></div>`;}).join('');
    return `Programs built for Black entrepreneurs${biz?'':' (register a business to unlock the CA business ones)'}:${list}<div class="s">US Black-owned banks (OneUnited, Industrial, Liberty, Carver) need the cross-border foundation first.</div>`;
  }
  if(has('ready','approve','qualify','mortgage','funding','loan','card','line of credit','approved')){
    const ready=D.matches.filter(x=>x.readiness_pct>=100).slice(0,6);
    const near=D.matches.filter(x=>x.readiness_pct>=60&&x.readiness_pct<100).slice(0,4);
    return `You're <b>ready now</b> for ${ready.length} products: ${ready.map(x=>x.name).join(', ')}.<br><b>Closest next:</b> ${near.map(x=>`${x.name} (${x.readiness_pct}% — ${x.gaps[0]?x.gaps[0].criterion:''})`).join('; ')||'n/a'}.<div class="s">Open Funding for the full ranked list + roadmap.</div>`;
  }
  if(has('pay','payoff','debt first','avalanche','which debt')){
    const r=payoffPlan(Math.round(sum(debtRecords().map(d=>d.min))+200),'avalanche');
    if(r.empty)return 'No debts tracked — add them under Wealth.';
    if(r.under)return 'Set a budget above your total minimums first (Wealth → payoff).';
    return `Attack highest-rate first (avalanche): ${r.order.map(d=>`${d.name} @ ${d.rate.toFixed(1)}%`).join(' → ')}. At ${money(r.budget)}/mo you'd be debt-free in ~<b>${r.months} months</b>, ~${money(r.interest)} interest. Tune the budget under Wealth.`;
  }
  if(has('us ','cross-border','america','usa','itin','build us')){
    return `US foundation: <b>${usf?'established':'not yet'}</b>.${usf?' Pursue US high-yield savings and ITIN/secured cards, then build a US FICO over 6–12 months.':' Do it in order: (1) open a US account via a Canadian bank’s US affiliate (RBC Bank/TD/BMO/Natbank/Desjardins — no SSN), (2) get a US mailing address, (3) first US card via Amex Global Transfer or an ITIN secured card, (4) apply for an ITIN. Your Canadian history does not transfer.'} See Access → Canada→US playbook.`;
  }
  if(has('tfsa','rrsp','fhsa','registered','room')){
    const g=D.portfolios||[];
    const lines=g.map(x=>`${x.type} ${money(x.room)}`).join(' · ')||'none tracked';
    const rr=g.find(x=>x.type==='RRSP');let extra='';
    if(rr&&rr.room>0){const ga=m.gross_monthly_income*12,ben=Math.round(totalTax(ga)-totalTax(Math.max(0,ga-Math.min(rr.room,ga))));extra=` A full RRSP contribution could cut this year’s tax by ~${money(ben)} (estimate).`;}
    return `Your registered room — ${lines}.${extra} FHSA is strongest: deductible <b>and</b> tax-free for a first home.`;
  }
  if(has('tax','marginal','bracket')){
    const ga=m.gross_monthly_income*12,ts=taxSnapshot(ga);
    return `On ${money(ga)} gross salary: est. income tax ${money(ts.tax)}, average ${ts.avg}%, marginal ${ts.marg}%. 2026-rate estimate — confirm with a CPA. Use the CLI payroll planner for take-home.`;
  }
  if(has('rate','hike','cut','boc','bank of canada','variable','prime')){
    const rw=PL.rate_watch,rl=rw?`Bank of Canada overnight ${(+rw.overnight).toFixed(2)}% · prime ${(+rw.prime).toFixed(2)}% (as of ${rw.as_of}). `:'';
    return rl+rateImpactLine();
  }
  if(has('score','health','improve')){
    const c=s.components,weak=Object.keys(c).sort((a,b)=>c[a]-c[b])[0];
    return `Health <b>${s.composite_score}/100 (${s.grade})</b>. Weakest lever: <b>${weak}</b> (${c[weak]}). Utilization ${pct(s.utilization_pct)}, DTI ${pct(s.dti_pct)}. Fastest wins: pay cards below 10% before the statement, clear/dispute any open collection, keep old accounts open.`;
  }
  if(has('net worth','asset','liabilit')){
    const a=nw.assets,l=nw.liabilities;
    return `Net worth <b>${money(nw.net_worth)}</b> — assets ${money(a.total)} (liquid ${money(nw.liquid_assets)}) minus liabilities ${money(l.total)}. Biggest liability: ${l.installment_debts>=l.credit_cards?'installment debt '+money(l.installment_debts):'cards '+money(l.credit_cards)}.`;
  }
  if(has('deadline','due','when','statement')){
    const dl=(PL.audit.deadlines||[]).slice(0,5).map(d=>`${d.date} — ${d.label} (${d.overdue?'OVERDUE':'in '+d.days+'d'})`).join('<br>');
    return dl?('Upcoming:<br>'+dl):'Nothing due in range.';
  }
  const play=D.plays[0],ph=D.roadmap.phases[0];
  return `Here's your picture: score <b>${s.composite_score} (${s.grade})</b>, net worth <b>${money(nw.net_worth)}</b>, ${D.matches.filter(x=>x.readiness_pct>=100).length} products ready. Top move: <b>${play?play.title:'add your data under Wealth/Credit'}</b>${play?' — '+play.estimated_benefit:''}. Next phase: <b>${ph?ph.title:'—'}</b>. Ask me about payoff, mortgage readiness, TFSA/RRSP room, US credit, or Black-entrepreneur programs.`;
}

V.command=()=>{const s=D.scorecard,nw=D.net_worth;
  const dl=(PL.audit.deadlines||[]).slice(0,4).map(d=>`<div class="row"><span class="tag ${d.overdue?'no':'mid'}">${d.overdue?'OVERDUE':'in '+d.days+'d'}</span><span class="t">${d.label}</span><div class="s">${d.date}</div></div>`).join('')||'<div class="s">No deadlines in range. Take snapshots & open cases in the CLI.</div>';
  const pl=D.plays.slice(0,3).map(p=>`<div class="row"><div class="t">${p.title}</div><div class="s">${p.estimated_benefit}</div></div>`).join('')||'<div class="s">Add data in Wealth/Credit to surface plays.</div>';
  const rd=D.matches.filter(x=>x.readiness_pct>=100).slice(0,4).map(x=>`<div class="row"><span class="tag ok">${x.country}/${x.segment}</span><span class="t">${x.name}</span></div>`).join('')||'<div class="s">No ready matches yet.</div>';
  const ph=D.roadmap.phases[0];
  return `<div class="panel"><div class="h">Command Overview</div><div class="grid g3" style="align-items:center">
    <div>${gauge(s.composite_score,s.grade)}<div class="foot" style="text-align:center">Financial health</div></div>
    ${tile('Net worth',money(nw.net_worth),'big green')}${tile('Best credit score',D.profile.best_score||'—','big cyan')}</div>
    <div class="grid g3" style="margin-top:6px">${tile('Utilization',pct(s.utilization_pct))}${tile('DTI',pct(s.dti_pct))}${tile('Liquid',money(nw.liquid_assets))}</div></div>
  <div class="grid g2"><div class="panel"><div class="h">Deadline radar</div>${dl}</div>
    <div class="panel"><div class="h">Top plays</div>${pl}<div class="h" style="margin-top:14px">Ready to apply</div>${rd}</div></div>
  <div class="panel"><div class="h">Next: ${ph?('Phase '+ph.n+' &middot; '+ph.title):'—'}</div><div class="s">Full plan under Funding. Edit numbers under Wealth / Credit. Records under Vault.</div><div class="foot">${DISC}</div></div>`;};
V.wealth=()=>{const a=D.net_worth.assets,l=D.net_worth.liabilities,mx=Math.max(a.total,l.total,1);
  if(PB==null)PB=Math.round(sum(debtRecords().map(d=>d.min))+200);
  const ga=D.metrics.gross_monthly_income*12,ts=taxSnapshot(ga);
  let h=editorHeader();
  const wsnaps=(PL.audit.snapshots||[]),wnwS=wsnaps.map(x=>x.net_worth),wutS=wsnaps.map(x=>x.utilization);
  h+=`<div class="panel"><div class="h">Overview</div><div class="statrow">
    <div class="stat"><div class="k">Net worth</div><div class="v green">${money(D.net_worth.net_worth)}</div>${deltaChip(wnwS,true,true)}<div class="spk">${svgSpark(wnwS,'var(--green)')}</div></div>
    <div class="stat"><div class="k">Assets</div><div class="v">${money(a.total)}</div><div class="d flat">liquid ${money(D.net_worth.liquid_assets)}</div></div>
    <div class="stat"><div class="k">Liabilities</div><div class="v red">${money(l.total)}</div><div class="d flat">cards + loans</div></div>
    <div class="stat"><div class="k">Utilization</div><div class="v">${pct(D.metrics.aggregate_utilization_pct)}</div>${deltaChip(wutS,false,false)}<div class="spk">${svgSpark(wutS,'var(--amber)')}</div></div>
  </div></div>`;
  h+=`<div class="panel"><div class="h">Net worth &middot; ${money(D.net_worth.net_worth)}</div><div class="grid g2">
    <div><div class="h">Assets ${money(a.total)}</div>${bar('Cash',a.cash_accounts,mx,'var(--green)')}${bar('Business cash',a.business_cash,mx,'var(--green)')}${bar('Registered',a.registered_value,mx,'var(--cyan)')}${bar('Other',a.other_assets,mx,'var(--cyan)')}</div>
    <div><div class="h">Liabilities ${money(l.total)}</div>${bar('Credit cards',l.credit_cards,mx,'var(--red)')}${bar('Installment',l.installment_debts,mx,'var(--red)')}${bar('Secured',l.secured_on_assets,mx,'var(--amber)')}</div></div></div>`;
  h+=`<div class="panel"><div class="h">Debt payoff (avalanche)</div><div class="cell" style="max-width:240px"><label>Monthly budget for all debts</label><input type="number" value="${PB}" oninput="updBudget(this.value)"></div><div id="payoffOut">${payoffHtml()}</div></div>`;
  h+=`<div class="panel"><div class="h">Tax snapshot (est. 2026)</div><div class="grid g2">${tile('Taxable income (gross salary)',money(ga))}${tile('Est. income tax',money(ts.tax),'amber')}${tile('Average rate',ts.avg+'%')}${tile('Marginal rate',ts.marg+'%')}</div><div class="foot">Estimate; excludes credits, CPP/EI, Health Premium. Use the CLI payroll planner for take-home. Not tax advice.</div></div>`;
  h+=editorTables('wealth');
  return h;};
V.credit=()=>{const s=D.scorecard,c=s.components,w=s.weights;
  let h=editorHeader();
  h+=`<div class="panel" style="text-align:center">${gauge(s.composite_score,s.grade)}<div class="foot">Composite financial-health score &middot; util ${pct(s.utilization_pct)} &middot; DTI ${pct(s.dti_pct)}</div></div>`;
  h+=`<div class="panel"><div class="h">Score components</div>${Object.keys(c).map(k=>bar(k+' ('+Math.round(w[k]*100)+'%)',c[k],100,gcol(c[k]))).join('')}</div>`;
  const au=D.audit.map(x=>`<div class="row"><span class="tag ${x.disputable_as_outdated?'no':'ok'}">${x.disputable_as_outdated?'DISPUTABLE':'OK'}</span><span class="t">${x.creditor} (${x.entry_type})</span><div class="s">${x.note||''}</div></div>`).join('')||'<div class="s">No credit-file entries yet.</div>';
  h+=`<div class="panel"><div class="h">Ontario reporting-period audit</div>${au}</div>`;
  const cs=(PL.audit.cases||[]).map(x=>`<div class="row"><span class="tag ${x.overdue?'no':'mid'}">#${x.id} ${x.overdue?'OVERDUE':(x.status==='open'?x.days_remaining+'d':x.status)}</span><span class="t">${x.creditor} via ${x.bureau}</span><div class="s">stage: ${x.current_step}</div></div>`).join('')||'<div class="s">No dispute cases (open them in CLI menu 22).</div>';
  h+=`<div class="panel"><div class="h">Dispute cases</div>${cs}</div>`;
  h+=`<div class="panel"><div class="h">Optimization playbook</div><div class="s">1. Pay on time (35%). 2. Utilization &lt;30% (ideally &lt;10% before statement). 3. Keep old accounts open. 4. Batch rate-shopping. 5. Healthy credit mix. 6. Ask for limit increases on clean cards. 7. Check both bureaus monthly.</div></div>`;
  h+=editorTables('credit');
  return h;};
let MF='all'; window.mf=f=>{MF=f;go('funding');};
V.funding=()=>{const chips=[['all','ALL'],['CA','CANADA'],['US','USA'],['personal','PERSONAL'],['business','BUSINESS']].map(c=>`<span class="chip ${MF===c[0]?'active':''}" onclick="mf('${c[0]}')">${c[1]}</span>`).join('');
  const list=D.matches.filter(x=>MF==='all'||x.country===MF||x.segment===MF);
  const rdy=D.matches.filter(x=>x.readiness_pct>=100).length,cl=D.matches.filter(x=>x.readiness_pct>=60&&x.readiness_pct<100).length,bl=D.matches.filter(x=>x.readiness_pct<60).length;
  let h=`<div class="panel"><div class="h">Funding readiness</div><div class="statrow" style="grid-template-columns:repeat(3,1fr)"><div class="stat"><div class="k">Ready now</div><div class="v green">${rdy}</div><div class="d flat">of ${D.matches.length} products</div></div><div class="stat"><div class="k">Close</div><div class="v amber">${cl}</div><div class="d flat">one or two gaps</div></div><div class="stat"><div class="k">Build first</div><div class="v">${bl}</div><div class="d flat">prerequisites</div></div></div></div>`;
  h+=`<div class="panel"><div class="h">Product match &middot; readiest first</div>${chips}<div style="margin-top:6px">`+list.map(x=>{const cls=x.readiness_pct>=100?'ok':x.readiness_pct>=60?'mid':'no';const gap=x.gaps&&x.gaps.length?`<br><b>Next:</b> ${x.gaps[0].criterion} — ${x.gaps[0].fix}`:'';const risk=x.risk?`<div class="risk">RISK: ${x.risk}</div>`:'';return `<div class="row"><span class="tag ${cls}">${x.readiness_pct}%</span><span class="tag">${x.country}/${x.segment}</span><span class="t">${x.name}</span><div class="s"><b>${x.verdict}.</b> Who: ${x.providers.join(', ')}${gap}</div>${risk}</div>`;}).join('')+`</div><div class="foot">Ranks categories, not a guarantee any lender approves you. ${DISC}</div></div>`;
  h+=`<div class="panel"><div class="h">Funding roadmap &middot; ordered plan</div>`+D.roadmap.phases.map(p=>`<div class="phase"><div class="pt">PHASE ${p.n} &middot; ${p.title}</div>`+p.steps.map(st=>`<div class="row"><div class="t">${st.action}</div><div class="s">${st.why}${st.unlocks&&st.unlocks.length?'<br><b>Unlocks:</b> '+st.unlocks.join(', '):''}</div></div>`).join('')+`</div>`).join('')+`</div>`;
  return h;};
let AF={country:null,segment:null,black:null};
window.af=(k,v)=>{AF[k]=(AF[k]===v?null:v);go('access');};
V.access=()=>{
  const av=e=>{const usf=usFound(),biz=bizExists();if(e.id==='sba')return{cls:'no',lab:'not eligible'};if(e.country==='US'&&!usf)return{cls:'mid',lab:'prereq'};if(e.segment==='business'&&!biz)return{cls:'mid',lab:'prereq'};return{cls:'ok',lab:'available'};};
  const _av=PL.access.map(av),nOk=_av.filter(x=>x.lab==='available').length,nPre=_av.filter(x=>x.lab==='prereq').length,nNo=_av.filter(x=>x.lab==='not eligible').length;
  const strip=`<div class="panel"><div class="h">Your eligibility</div><div class="statrow" style="grid-template-columns:repeat(3,1fr)"><div class="stat"><div class="k">Available now</div><div class="v green">${nOk}</div><div class="d flat">standard KYC</div></div><div class="stat"><div class="k">Prerequisite</div><div class="v amber">${nPre}</div><div class="d flat">build foundation / business</div></div><div class="stat"><div class="k">Not eligible</div><div class="v">${nNo}</div><div class="d flat">e.g. SBA citizenship</div></div></div></div>`;
  const chip=(k,v,lab)=>`<span class="chip ${AF[k]===v?'active':''}" onclick="af('${k}','${v}')">${lab}</span>`;
  const chips=chip('country','CA','CANADA')+chip('country','US','USA')+chip('segment','personal','PERSONAL')+chip('segment','business','BUSINESS')+chip('black','y','BLACK-FOCUSED');
  let list=PL.access.filter(e=>(!AF.country||e.country===AF.country)&&(!AF.segment||e.segment===AF.segment||e.segment==='both')&&(AF.black!=='y'||e.black_focus));
  list.sort((a,b)=>a.category.localeCompare(b.category)||a.name.localeCompare(b.name));
  let cat=null,h=strip+`<div class="panel"><div class="h">Access list &middot; banks, credit unions, loans, cross-border & programs</div>${chips}<div style="margin-top:8px">`;
  if(!list.length)h+='<div class="s">No matches for that filter.</div>';
  list.forEach(e=>{if(e.category!==cat){cat=e.category;h+=`<div class="h" style="margin-top:14px">${cat}</div>`;}
    const bf=e.black_focus?'<span class="tag ok">Black-focused</span>':'';const ea=av(e);
    h+=`<div class="row"><span class="tag ${ea.cls}">${ea.lab}</span><span class="tag">${e.country}/${e.segment}</span> ${bf}<span class="t">${e.name}</span><div class="s">${e.access}<br><b>Eligibility:</b> ${e.eligibility}${e.url?' &middot; '+e.url:''}</div></div>`;});
  h+=`</div><div class="foot">Amounts/terms/eligibility change — confirm with each provider. Many US options need a US cross-border foundation; some US minority programs (e.g. SBA 8(a)) require US citizenship. Not advice.</div></div>`;
  const bu=Object.keys(D.reference.bureaus).map(k=>`<div class="row"><div class="t">${k}</div><div class="s">${D.reference.bureaus[k].join(' &middot; ')}</div></div>`).join('');
  h+=`<div class="panel"><div class="h">Credit bureaus (CA + US)</div>${bu}</div>`;
  h+=`<div class="panel"><div class="h">Canada &rarr; US credit playbook</div>${D.reference.crossborder.map(s=>`<div class="row"><div class="s">${s}</div></div>`).join('')}</div>`;
  return h;};
V.vault=()=>{const A=PL.audit;let h='';
  const snaps=A.snapshots||[];
  if(snaps.length>=2){const nwS=snaps.map(s=>s.net_worth),scS=snaps.map(s=>s.composite_score),utS=snaps.map(s=>s.utilization);
    h+=`<div class="panel"><div class="h">Trends (${snaps.length} snapshots)</div><div class="statrow" style="grid-template-columns:repeat(3,1fr)">
      <div class="stat"><div class="k">Net worth</div><div class="v green">${money(nwS[nwS.length-1])}</div>${deltaChip(nwS,true,true)}<div class="spk">${svgSpark(nwS,'var(--green)')}</div></div>
      <div class="stat"><div class="k">Health score</div><div class="v cyan">${scS[scS.length-1]}</div>${deltaChip(scS,true,false)}<div class="spk">${svgSpark(scS,'var(--cyan)')}</div></div>
      <div class="stat"><div class="k">Utilization</div><div class="v">${utS[utS.length-1]}%</div>${deltaChip(utS,false,false)}<div class="spk">${svgSpark(utS,'var(--amber)')}</div></div>
    </div></div>`;}
  else h+=`<div class="panel"><div class="h">Trends</div><div class="s">Take snapshots over time in the CLI (menu 20) to chart your trajectory.</div></div>`;
  const gcards=(A.goals||[]).map(g=>{const pc=Math.min(100,g.progress_pct),col=g.reached?'var(--green)':pc>=60?'var(--cyan)':'var(--amber)';
    return `<div class="goalcard"><div class="gtop"><span class="t">${g.name}</span><span class="gpct" style="color:${col}">${g.reached?'✓ reached':pc+'%'}</span></div>
      <div class="gbar"><div class="gfill" style="width:${pc}%;background:${col}"></div></div>
      <div class="s">${g.metric}: ${Math.round(g.current).toLocaleString()} / ${(+g.target).toLocaleString()} &middot; projected ${g.projected_date}</div></div>`;}).join('')||'<div class="s">No goals yet (add in CLI menu 20).</div>';
  h+=`<div class="panel"><div class="h">Goals</div><div class="goalgrid">${gcards}</div></div>`;
  const dl=(A.deadlines||[]).map(d=>`<div class="row"><span class="tag ${d.overdue?'no':'mid'}">${d.overdue?'OVERDUE':'in '+d.days+'d'}</span><span class="t">${d.label}</span><div class="s">${d.date}</div></div>`).join('')||'<div class="s">Nothing due in range.</div>';
  h+=`<div class="panel"><div class="h">Deadline radar</div>${dl}</div>`;
  const consent=A.consent&&A.consent.consent_obtained?`<span class="tag ok">consent on file (${A.consent.method})</span>`:'<span class="tag no">no consent recorded</span>';
  const sc2=(A.statute_currency||[]).map(x=>`<div class="row"><span class="tag ${x.stale?'no':'ok'}">${x.stale?'STALE':'current'}</span><span class="t">${x.item}</span><div class="s">verified ${x.last_verified} &middot; ${x.source}</div></div>`).join('');
  h+=`<div class="panel"><div class="h">Compliance</div><div class="s">PIPEDA consent: ${consent}</div><div class="h" style="margin-top:12px">Statute & rate currency</div>${sc2}</div>`;
  const bc=A.business_credit||{};
  h+=`<div class="panel"><div class="h">Business credit (PAYDEX readiness)</div><div class="s">On-time reporting vendors: ${bc.on_time_reporting||0} &middot; PAYDEX-ready: ${bc.paydex_ready?'YES':'not yet'}</div>${(bc.gaps||[]).map(g=>'<div class="s">&bull; '+g+'</div>').join('')}</div>`;
  const log=(A.audit_log||[]).map(e=>`<div class="s" style="font-size:11px">${e.ts} &middot; <b>${e.action}</b> ${e.detail||''}</div>`).join('')||'<div class="s">No events yet.</div>';
  h+=`<div class="panel"><div class="h">Audit log (recent)</div>${log}<div class="foot">Snapshots, goals, cases, consent, encrypted backups (AES-256) and the printable audit report are managed in CLI menus 20–25.</div></div>`;
  return h;};

/* ---- editor mutations ---- */
function refreshSummaries(){document.querySelectorAll('.liveSummary').forEach(e=>e.innerHTML=liveSummary());}
window.upd=(sec,i,f,typ,val)=>{let v=val;if(typ==='num')v=(val===''?0:parseFloat(val));if(typ==='bool')v=!!val;
  if(sec==='__profile__')STATE.user_profile[f]=v;else STATE[sec][i][f]=v;
  recompute();refreshSummaries();};
window.addRow=key=>{const def=SCHEMA.find(s=>s[1]===key);STATE[key].push(def[4]());recompute();go(CUR);};
window.delRow=(key,i)=>{STATE[key].splice(i,1);recompute();go(CUR);};

/* ---- export / save ---- */
function currentProfile(){return {personal_accounts:STATE.personal_accounts,credit_cards:STATE.credit_cards,installment_debts:STATE.installment_debts,portfolios:STATE.portfolios,income:STATE.income,business_accounts:STATE.business_accounts,assets:STATE.assets,credit_report_entries:STATE.credit_report_entries,user_profile:STATE.user_profile};}
window.exportJson=()=>{const blob=new Blob([JSON.stringify(currentProfile(),null,2)],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='coretrust_profile.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);toast('Downloaded coretrust_profile.json — import via CLI menu 13 &rarr; g.');};
window.save=async()=>{try{const r=await fetch('/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(currentProfile())});if(!r.ok)throw 0;const j=await r.json();const n=j.counts?Object.values(j.counts).reduce((a,b)=>a+b,0):'';toast('Saved to local database ✓ '+n+' records written.');}catch(e){exportJson();toast('No local server — downloaded JSON instead. Import via CLI menu 13 → g.');}};
let _tt;function toast(m){let t=document.getElementById('toast');if(!t){t=document.createElement('div');t.id='toast';document.body.appendChild(t);}t.textContent=m;t.classList.add('show');clearTimeout(_tt);_tt=setTimeout(()=>t.classList.remove('show'),4200);}

/* ---- router ---- */
let CUR='command';
function go(v){CUR=v;document.querySelectorAll('.navbtn').forEach(b=>b.classList.toggle('active',b.dataset.v===v));const c=document.getElementById('content');c.innerHTML=(V[v]||V.command)();c.scrollIntoView({behavior:'smooth',block:'start'});}
window.go=go;
"""


def render_page_content_live(payload: dict) -> str:
    css = BASE_CSS + EDITOR_CSS
    return ("<style>\n" + css + "\n</style>\n" + BODY +
            "\n<script>\nwindow.PAYLOAD = " + json.dumps(payload) + ";\n</script>\n" +
            "<script>\n" + JS_LIVE + "\n</script>\n")


def render_standalone_live(payload: dict) -> str:
    return ("<!doctype html><html lang='en'><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width, initial-scale=1'>"
            "<title>CoreTrust — Live Financial Core</title></head><body>"
            + render_page_content_live(payload) + "</body></html>")


def write_live_dashboard(db, path: str = "dashboard_live.html") -> str:
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(render_standalone_live(build_editable_payload(db)))
    return path
