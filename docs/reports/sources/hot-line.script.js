/* One hot line stops a shire. Every number comes from D (hotline.json, built by workloads/nocbench/analyze_hotline.py)
   except the pooled rerun energies in POOLED below. Charts use the shared toolkit CK (docs/reports/sources/chartkit.js). */
const $=id=>document.getElementById(id);
const f1=v=>v.toFixed(1),f2=v=>v.toFixed(2),f3=v=>v.toFixed(3);
const num=CK.fmt.num, n0=v=>num(v,0);
const A2=r=>r.card==='aifoundry2', A3=r=>r.card==='aifoundry3';
const CARDS=D.cards, CARD3=CARDS[1];
const CTX=D.context||{};
const BANK=CTX.bank_service_cycles, RT=CTX.remote_atomic_latency_cycles, WIN=CTX.window_cycles;
const CLOCK_MHZ=WIN/1e4;  // the 6,000,000-cycle window is 10 ms: the cards ran at 600 MHz
/* a percentage range over values in [0,1]: "85–87%", or one value when both ends print the same */
const pr=(vals,dp)=>{const d=dp==null?0:dp,a=(100*Math.min(...vals)).toFixed(d),b=(100*Math.max(...vals)).toFixed(d);return a===b?a+'%':a+'–'+b+'%';};
const pct=(v,dp)=>(100*v).toFixed(dp==null?0:dp)+'%';
const both=(a,b)=>a===b?a:a+' / '+b;   // one value when the two cards agree to the printed precision
const WORD=['no','one','two','three','four','five','six','seven','eight','nine'];
const word=n=>WORD[n]||n0(n);

/* Pooled energies: 22 September plus the 23 September passes, both cards, from
   docs/reports/data/2026-09-23-energy-manual/reruns.json (hotline_nj_per_op and hotline_over_idle_w.contended),
   written by
     python3 tools/ettelem/analyze_reruns.py docs/reports/data/2026-09-23-reruns-aifoundry2-warm \
       docs/reports/data/2026-09-23-reruns-aifoundry3 --out reruns.json
   Copied here (4 decimals) rather than read as data: reruns.json is built from this page's power.json, so feeding
   it back into hotline.json would make a file loop (PLAN2 DP-6). Update both together if the reruns change. */
const POOLED={
 nj:{contended:{mean:19.8452,lo:16.9176,hi:23.5655,n:7,per_card:{aifoundry2:{mean:20.8001,n:4},aifoundry3:{mean:18.5721,n:3}}},
  spread:{mean:1.1584,lo:1.0074,hi:1.3706,n:7,per_card:{aifoundry2:{mean:1.2067,n:4},aifoundry3:{mean:1.094,n:3}}},
  contended_scp:{mean:20.5222,lo:16.518,hi:24.4088,n:7,per_card:{aifoundry2:{mean:22.3671,n:4},aifoundry3:{mean:18.0622,n:3}}},
  starved:{mean:20.4218,lo:16.9155,hi:24.2287,n:7,per_card:{aifoundry2:{mean:21.5618,n:4},aifoundry3:{mean:18.9019,n:3}}},
  local_only:{mean:0.501,lo:0.3735,hi:0.8168,n:7,per_card:{aifoundry2:{mean:0.5657,n:4},aifoundry3:{mean:0.4146,n:3}}}},
 w_contended:{mean:1.1904,lo:1.0148,hi:1.4135,n:7,per_card:{aifoundry2:{mean:1.2476,n:4},aifoundry3:{mean:1.1141,n:3}}}
};

/* ---------- KPIs ---------- */
(function(){
 const fair=D.fairness.find(r=>A2(r)&&r.home==='0'&&r.per_shire===32);
 const loc=D.local.find(r=>A2(r)&&r.home==='scplocal:0'&&r.shires>1);
 const reqs=D.requesters.filter(A2).sort((a,b)=>a.remote_minions-b.remote_minions);
 const req=reqs.find(r=>r.frac_of_alone<0.5), prev=req?reqs[reqs.indexOf(req)-1]:null;
 const pw=D.power.runs, c=pw.find(r=>r.label==='contended'), s=pw.find(r=>r.label==='spread');
 $('k1').textContent=f3(fair.host_share);
 $('k2').textContent=pct(loc.frac_of_alone,2);
 $('k3').textContent=req&&prev?`${prev.remote_minions+1}–${req.remote_minions}`:'—';
 $('k3sub').textContent=req&&prev&&RT?
  `${prev.remote_minions} leave the host at ${pct(prev.frac_of_alone,1)}, ${req.remote_minions} stop it (the inequality in section 3 puts the edge at ${Math.ceil(RT/BANK)}); one shire has 32`:'';
 $('k4').textContent=(c.nj_per_op/s.nj_per_op).toFixed(0)+'×';
})();

/* ---------- section 1: shares by mesh distance, map and scatter ---------- */
(function(){
 const byc=D.shares_home0_by_card, LAY=D.layout, fit=D.share_fit;
 if(!byc||!LAY||!fit){$('fair').textContent='';return;}
 const ids=Object.keys(LAY).map(Number).sort((a,b)=>a-b);
 const share=(card,kind,s)=>{const r=byc[card].find(x=>x.kind===kind&&x.s===s);return r?r.share:null;};
 const hopsOf=s=>{const [x,y]=LAY[s],[x0,y0]=LAY[0];return Math.abs(x-x0)+Math.abs(y-y0);};
 const F=fit[CARDS[0]];
 const fitShare=h=>F.harmonic_mean_cycles/(F.round_trip_cycles_0_hops+F.cycles_per_hop*h);
 /* diverging fill around an even split: towards --c1 above 1, towards --c2 below; 1.0 is the surface */
 const fill=v=>{const d=Math.max(-1,Math.min(1,(v-1)/0.2)),p=(Math.abs(d)*75).toFixed(1);
  return `color-mix(in srgb, var(${d>=0?'--c1':'--c2'}) ${p}%, var(--surface))`;};
 let mode='one';
 CK.seg('fairctl',{label:'Minions taking part',options:[['one','32 minions, one per shire'],['full','1,024 minions, 32 per shire']],
  value:mode,onChange:v=>{mode=v;f.redraw();}});
 const tipHtml=s=>`<b>shire ${s}</b> · ${hopsOf(s)} hop${hopsOf(s)===1?'':'s'} from shire 0, which holds the line<br>`+
  `one minion per shire: ${f3(share(CARDS[0],'one',s))} (${CARDS[0]}), ${f3(share(CARD3,'one',s))} (${CARD3})<br>`+
  `32 per shire: ${f3(share(CARDS[0],'full',s))}, ${f3(share(CARD3,'full',s))}`;
 const f=CK.frame('fair',{label:'Share of the contended atomic for each shire, on the mesh map and against mesh hops from shire 0',
  height:W=>W<600?Math.min(46,Math.floor((W-24)/6))*6+64+300:360,
  draw(f){
   const svg=f.svg,W=f.W,narrow=f.narrow;
   const c=narrow?Math.min(46,Math.floor((W-24)/6)):46, mapW=6*c;
   const mx=narrow?Math.round((W-mapW)/2):8, my=24;
   CK.txt(svg,mx,14,'The mesh, shire by shire','lab');
   const cx=s=>mx+LAY[s][0]*c+c/2, cy=s=>my+LAY[s][1]*c+c/2;
   for(const [ex,ey] of D.empty) CK.el('rect',{x:mx+ex*c+3,y:my+ey*c+3,width:c-6,height:c-6,rx:5,fill:'none',
     style:'stroke:var(--grid);stroke-dasharray:3 3'},svg);
   const cells=[];
   /* cells in reading order (row, then column), so the arrow keys move across the map */
   const order=ids.slice().sort((a,b)=>LAY[a][1]-LAY[b][1]||LAY[a][0]-LAY[b][0]);
   for(const s of order){
    const v=share(CARDS[0],mode,s), g=CK.el('g',{},svg);
    const r=CK.el('rect',{x:mx+LAY[s][0]*c+2,y:my+LAY[s][1]*c+2,width:c-4,height:c-4,rx:6},g);
    r.style.fill=fill(v); r.style.stroke=s===0?'var(--ink)':'var(--grid)'; r.style.strokeWidth=s===0?'2.5':'1';
    CK.txt(g,cx(s),cy(s)+4,String(s),'lab-strong','middle').style.fill='var(--ink)';
    g.dataset.s=s; cells.push(g);
    CK.tip(f,g,()=>tipHtml(s));
    g.addEventListener('pointerenter',()=>hl(s)); g.addEventListener('pointerleave',()=>hl(null));
    g.addEventListener('blur',()=>hl(null));
   }
   /* the highlight line sits above the cells so it stays visible; it takes no pointer events */
   const line=CK.el('g',{'aria-hidden':'true',style:'pointer-events:none'},svg);
   CK.keynav(f,cells,{onFocus:n=>hl(+n.dataset.s),step:(k,K,nodes)=>{
     if(K!=='ArrowUp'&&K!=='ArrowDown')return null;
     const s=+nodes[k].dataset.s,[x,y]=LAY[s],dy=K==='ArrowDown'?1:-1;
     for(let yy=y+dy;yy>=0&&yy<6;yy+=dy){const j=nodes.findIndex(n=>LAY[+n.dataset.s][0]===x&&LAY[+n.dataset.s][1]===yy);if(j>=0)return j;}
     return k;}});
   /* colour key under the map */
   const ky=my+mapW+14, kw=Math.min(mapW,220), kx=mx+(mapW-kw)/2, steps=[0.8,0.85,0.9,0.95,1,1.05,1.1,1.15,1.2];
   steps.forEach((v,i)=>{const r=CK.el('rect',{x:kx+i*kw/steps.length,y:ky,width:kw/steps.length-1,height:10},svg);r.style.fill=fill(v);r.style.stroke='var(--grid)';});
   CK.txt(svg,kx,ky+24,'0.80','tick','start');CK.txt(svg,kx+kw/2,ky+24,'1.00','tick','middle');CK.txt(svg,kx+kw,ky+24,'1.20','tick','end');
   /* scatter: share against hops from shire 0 */
   const sx0=narrow?44:mx+mapW+64, sy0=narrow?ky+54:22, sx1=W-12, sy1=narrow?f.H-40:f.H-40;
   const x=CK.lin(0,10,sx0,sx1), y=CK.lin(0.8,1.25,sy1,sy0);
   CK.axes({svg,W:sx1+12,H:sy1+40},{x,y,L:sx0,R:12,T:sy0,B:40,xt:[0,2,4,6,8,10],yt:[0.8,0.9,1.0,1.1,1.2],
     yfmt:v=>v.toFixed(2),xl:narrow?'mesh hops from shire 0':'mesh hops from shire 0 (Manhattan distance on the map)'});
   CK.txt(svg,sx0-40,sy0-9,'share of an even split','lab');
   CK.el('line',{x1:sx0,x2:sx1,y1:y(1),y2:y(1),style:'stroke:var(--ink-2);stroke-width:1;stroke-dasharray:2 3'},svg);
   if(mode==='one'){
    const pts=[];for(let h=0;h<=10;h+=0.25)pts.push([h,fitShare(h)]);
    CK.el('path',{d:CK.path(pts,x,y),fill:'none',style:'stroke:var(--ref);stroke-width:1.5;stroke-dasharray:5 4'},svg);
    CK.txt(svg,sx1,sy0+12,`dashed: ${num(F.harmonic_mean_cycles,0)}/(${num(F.round_trip_cycles_0_hops,0)} + ${num(F.cycles_per_hop,1)} × hops)`,'lab','end');
   }
   const dots=[];
   for(const s of ids.slice().sort((a,b)=>hopsOf(a)-hopsOf(b)||a-b)){
    const v2=share(CARDS[0],mode,s),v3=share(CARD3,mode,s),g=CK.el('g',{},svg);
    const d=CK.el('circle',{cx:x(hopsOf(s)),cy:y(v2),r:5},g); d.style.fill=fill(v2); d.style.stroke='var(--ink-2)';
    const o=CK.el('circle',{cx:x(hopsOf(s)),cy:y(v3),r:8,fill:'none','aria-hidden':'true'},g); o.style.stroke='var(--ink-2)';
    g.dataset.s=s; dots.push(g);
    CK.tip(f,g,()=>tipHtml(s));
    g.addEventListener('pointerenter',()=>hl(s)); g.addEventListener('pointerleave',()=>hl(null)); g.addEventListener('blur',()=>hl(null));
   }
   CK.keynav(f,dots,{onFocus:n=>hl(+n.dataset.s)});
   const mark=CK.el('g',{'aria-hidden':'true'},svg);
   /* highlight one shire: a straight line to shire 0 (not a route: the mesh's routing order was not measured) and a ring on its point */
   function hl(s){
    line.textContent=''; mark.textContent='';
    if(s==null)return;
    if(s!==0) CK.el('line',{x1:cx(s),y1:cy(s),x2:cx(0),y2:cy(0),style:'stroke:var(--ink);stroke-width:2;stroke-dasharray:4 3'},line);
    const r=CK.el('circle',{cx:x(hopsOf(s)),cy:y(share(CARDS[0],mode,s)),r:11,fill:'none'},mark); r.style.stroke='var(--ink)'; r.style.strokeWidth='2';
   }
  }});
 const full=[...byc[CARDS[0]],...byc[CARD3]].filter(r=>r.kind==='full').map(r=>r.share);
 const one=byc[CARDS[0]].filter(r=>r.kind==='one'), far=Math.max(...one.map(r=>hopsOf(r.s)));
 const at=h=>one.filter(r=>hopsOf(r.s)===h).map(r=>r.share);
 const host=D.fairness.find(r=>A2(r)&&r.home==='0'&&r.per_shire===32).host_share;
 /* section 3's round trip: one requester, the bank idle, from this shire */
 const rtS=CTX.remote_atomic_latency_shire, rtH=rtS!=null&&LAY[rtS]?hopsOf(rtS):null;
 const rtNote=RT&&rtH!=null?`; section 3's ${n0(RT)} cycles is the uncontended round trip of a single requester in shire ${rtS}, ${rtH} hop${rtH===1?'':'s'} away`:'';
 $('faircap').textContent=
  `The map colours each shire by its share (towards blue above an even split, towards orange below; shire 0, outlined, holds the line). `+
  `The scatter plots the same shares against mesh hops from shire 0; dots are ${CARDS[0]}, rings ${CARD3}. `+
  `With one minion per shire the dashed curve is ${num(F.harmonic_mean_cycles,0)}/(${num(F.round_trip_cycles_0_hops,0)} + ${num(F.cycles_per_hop,1)} × hops): `+
  `a request's round trip, ${num(F.round_trip_cycles_0_hops,0)} cycles plus ${num(F.cycles_per_hop,1)} per hop, sets how often a shire gets its turn, and the curve fits every shire `+
  `within ${F.max_share_error} (${fit[CARD3].max_share_error} on ${CARD3}), from ${f3(Math.max(...at(0)))} at 0 hops to ${f3(Math.min(...at(far)))} at ${far}. `+
  `That round trip is taken under the saturated bank, so it includes the queueing${rtNote}. `+
  `With every minion taking part the whole chip lands within ${f3(Math.min(...full))}–${f3(Math.max(...full))} on both cards and the host shire is at ${f3(host)}: the map goes flat. `+
  `A hovered or focused shire is joined to shire 0 by a straight line, not by its route (the mesh's routing order was not measured). `+
  `The same holds for Ivan's exact case, a scratchpad word in shire 0: host share 1.004, every shire 0.998–1.004.`;
})();

/* ---------- section 1 table: home sweep, the two cards side by side ---------- */
(function(){
 const key=r=>r.home+'|'+r.per_shire, a3={};
 D.fairness.filter(A3).forEach(r=>{a3[key(r)]=r;});
 $('fairtab').innerHTML='<thead><tr><th>DRAM line homed in</th><th class="num">Minions per shire</th><th class="num">Host shire’s share, a2 / a3</th><th class="num">Spread across 32 shires, a2 / a3</th></tr></thead><tbody>'+
  D.fairness.filter(A2).map(r=>{const b=a3[key(r)];
   return `<tr><td>shire ${r.home}</td><td class="num">${r.per_shire}</td><td class="num">${both(f3(r.host_share),b?f3(b.host_share):'—')}</td>`+
    `<td class="num">${both(f3(r.min_share)+'–'+f3(r.max_share),b?f3(b.min_share)+'–'+f3(b.max_share):'—')}</td></tr>`;}).join('')+'</tbody>';
 CK.stackTable('fairtab');
})();

/* ---------- section 2: the host shire's own traffic ---------- */
(function(){
 const alone={},with_={};
 D.local.forEach(r=>{const k=r.card+'|'+r.home;(r.shires===1?alone:with_)[k]=r;});
 const names={'scplocal':'its own scratchpad','dramlocal':'its own scratchpad','scpstream':'DRAM','dramstream':'DRAM'};
 const hotin={'scplocal':'scratchpad of the same shire','dramlocal':'L3 slice of the same shire',
              'scpstream':'scratchpad of the same shire','dramstream':'L3 slice of the same shire'};
 const homes=D.local.filter(r=>A2(r)&&r.shires>1).map(r=>r.home);
 $('localtab').innerHTML='<thead><tr><th>Host shire is reading</th><th>Hot line is in the</th><th class="num">Alone, a2 / a3</th><th class="num">While hammered, a2 / a3</th><th class="num">Fraction, a2 / a3</th></tr></thead><tbody>'+
  homes.map(h=>{const base=h.split(':')[0],w2=with_[CARDS[0]+'|'+h],w3=with_[CARD3+'|'+h],l2=alone[CARDS[0]+'|'+h],l3=alone[CARD3+'|'+h];
   return `<tr><td>${names[base]}</td><td>${hotin[base]}</td><td class="num">${both(n0(l2.host_ops),n0(l3.host_ops))}</td>`+
    `<td class="num">${both(n0(w2.host_ops),n0(w3.host_ops))}</td><td class="num">${both(pct(w2.frac_of_alone,3),pct(w3.frac_of_alone,3))}</td></tr>`;}).join('')+'</tbody>';
 CK.stackTable('localtab');
 if(CTX.window_independence){
  $('wintab').innerHTML='<thead><tr><th class="num">Window</th><th class="num">Host shire’s loads</th><th class="num">Atomics completed in the window</th></tr></thead><tbody>'+
   CTX.window_independence.map(r=>`<tr><td class="num">${(r.window/(CLOCK_MHZ*1e3)).toFixed(0)} ms</td><td class="num">${r.host_ops}</td><td class="num">${(r.remote_ops/1e6).toPrecision(2)} M</td></tr>`).join('')+'</tbody>';
 } else $('wintab').closest('.table-wrap').hidden=true;
})();

/* ---------- section 3: the inequality, and the explorer that puts both sweeps on one load axis ---------- */
const LOAD=(N,P)=>N*BANK/(P+RT);                               // predicted: bank cycles asked for per round trip
const lf=v=>v>=0.1?f2(v):v.toPrecision(2);                       // a load: 0.81, 45.88; small ones to two figures (0.046)
const MEAS=r=>(r.total_ops-r.host_ops)*BANK/WIN;                  // measured: remote atomics × 10 cycles ÷ window
const RUNS=[...D.requesters.map(r=>({...r,ser:'req'})),...D.pace.map(r=>({...r,ser:'pace'}))]
 .map(r=>({...r,x:LOAD(r.remote_minions,r.pace),m:MEAS(r)}));
(function(){
 if(!RT){return;}
 const unsat=RUNS.filter(r=>r.x<1), err=Math.max(...unsat.map(r=>Math.abs(r.x-r.m)/r.m));
 const tested=[...new Set(D.requesters.map(r=>r.remote_minions))].sort((a,b)=>a-b), edge=Math.ceil(RT/BANK);
 const below=Math.max(...tested.filter(n=>n<edge)), above=Math.min(...tested.filter(n=>n>=edge));
 const NP=Math.max(...D.pace.map(r=>r.remote_minions)), need=NP*BANK-RT;
 const paces=[...new Set(D.pace.map(r=>r.pace))].sort((a,b)=>a-b);
 const lastBad=Math.max(...paces.filter(p=>p<need)), knee=Math.min(...paces.filter(p=>p>need));
 const run=(ser,N,P)=>RUNS.filter(r=>r.ser===ser&&r.remote_minions===N&&r.pace===P);
 const r20=run('req',below,0), p12=run('pace',NP,12000), p16=run('pace',NP,16000);
 $('ineqtext').innerHTML=
  `Here <i>N</i> is the number of remote minions hammering the line, <i>P</i> the cycles each waits between atomics, `+
  `and <i>t</i> the measured ${n0(RT)}-cycle round trip. With <i>P</i> = 0 it puts the edge at ${edge} requesters, between the `+
  `${below} and ${above} that were tested. It also prices section 5: for ${n0(NP)} requesters it needs <i>P</i> above about `+
  `${n0(Math.round(need/100)*100)} cycles, which is why ${n0(lastBad)} does nothing and ${n0(knee)} is the knee. In every unsaturated run `+
  `of both sweeps it predicts the bank's measured load to within about ${(100*err).toFixed(0)}%. <b>Not saturating the bank is `+
  `necessary, not sufficient:</b> one shire's ${below} requesters leave the host at ${pr(r20.map(r=>r.frac_of_alone))} with the bank `+
  `${pct(LOAD(below,0))} busy, while ${n0(NP)} paced requesters leave it at ${pr(p12.map(r=>r.frac_of_alone))} with the bank `+
  `${pct(LOAD(NP,12000))} busy and ${pr(p16.map(r=>r.frac_of_alone))} at ${pct(LOAD(NP,16000))}. The two tests differ in how many `+
  `requesters there are and in how many minions the host runs (${below} against ${p12[0].host_minions}), and which of these matters `+
  `was not tested.`;

 /* verdict bands, each summarised from the runs that fall in it */
 const BANDS=[[1,Infinity,'Saturated'],[0.9,1,'At the knee'],[0.5,0.9,'Below saturation, not free'],[0,0.5,'Light load']];
 const bandOf=x=>BANDS.find(b=>x>=b[0]&&x<b[1]);
 const list=a=>a.length>1?a.slice(0,-1).join(', ')+' and '+a[a.length-1]:String(a[0]);
 const span=a=>{const u=[...new Set(a)].sort((p,q)=>p-q);return u.length>2?n0(u[0])+'–'+n0(u[u.length-1]):list(u.map(n0));};
 function verdict(x){
  const b=bandOf(x), rs=RUNS.filter(r=>bandOf(r.x)===b), q=rs.filter(r=>r.ser==='req'), p=rs.filter(r=>r.ser==='pace');
  if(b[0]>=1){const lo=(100*Math.min(...rs.map(r=>r.frac_of_alone))).toFixed(2),hi=(100*Math.max(...rs.map(r=>r.frac_of_alone))).toFixed(2);
   return `<b>${b[2]}:</b> in all ${rs.length} runs on this chart at a load of 1 or more the host got ${lo===hi?'about '+lo+'%':lo+'–'+hi+'%'} of its memory throughput.`;}
  if(b[0]===0) return `<b>${b[2]}:</b> every run here left the host at ${pct(Math.min(...rs.map(r=>r.frac_of_alone)),1)} or more.`;
  const parts=[];
  if(q.length) parts.push(`one shire's ${span(q.map(r=>r.remote_minions))} requesters left the host at ${pr(q.map(r=>r.frac_of_alone),1)}`);
  if(p.length) parts.push(`${n0(NP)} paced at ${span(p.map(r=>r.pace))} cycles left it at ${pr(p.map(r=>r.frac_of_alone))}`);
  return `<b>${b[2]}:</b> measured in this band, ${parts.join('; ')}.`;
 }
 const out=CK.readout('reqout');
 let N=NP, P=12000;
 const upd=()=>{
  const x=LOAD(N,P), hit=RUNS.filter(r=>r.remote_minions===N&&r.pace===P);
  const hf=hit.map(r=>r.frac_of_alone), hdp=Math.max(...hf)<0.01?2:Math.min(...hf)>=0.95?1:0;  // the band text's precision
  const hitTxt=hit.length?` <b>Measured at this setting:</b> host at ${pr(hf,hdp)}, `+
    `measured load ${both(lf(Math.min(...hit.map(r=>r.m))),lf(Math.max(...hit.map(r=>r.m))))}.`:' This setting was not run.';
  out.set(`<b>Load ${lf(x)}</b> = ${n0(N)} × ${n0(BANK)} cycles of bank per round ÷ (${n0(P)} + ${n0(RT)}) cycles per round `+
   `(predicted). ${verdict(x)}${hitTxt}`);
  if(f) f.redraw();
 };
 CK.range('reqN',{label:'Remote minions, N',stops:[1,2,4,8,12,16,20,24,32,64,256,NP],value:N,fmt:n0,onInput:v=>{N=v;upd();}});
 CK.range('reqP',{label:'Pause between atomics, P (cycles)',stops:[0,1000,4000,8000,10000,12000,16000,20000,40000,100000],value:P,fmt:n0,onInput:v=>{P=v;upd();}});
 let f=null;
 f=CK.frame('req',{label:'Host throughput against predicted bank load, both sweeps, both cards',height:W=>W<600?340:380,
  draw(f){
   const svg=f.svg,W=f.W,H=f.H,L=48,R=14,T=26,B=46,narrow=f.narrow;
   const x=CK.log(0.03,50,L,W-R), y=CK.lin(0,1.15,H-B,T);
   const sat=CK.el('rect',{x:x(1),y:T,width:W-R-x(1),height:H-B-T,'aria-hidden':'true'},svg); sat.style.fill='var(--grid)'; sat.style.opacity='0.6';
   CK.axes(f,{x,y,L,R,T,B,xt:narrow?[0.05,0.25,1,5,40]:[0.05,0.1,0.25,0.5,1,2,5,10,40],yt:[0,0.25,0.5,0.75,1],xfmt:v=>num(v),
    yfmt:v=>Math.round(100*v)+'%',xl:narrow?'predicted load on the bank (1 = saturated)':'predicted load on the host shire’s bank, N × 10 ÷ (P + 216); 1 = saturated'});
   CK.txt(svg,4,T-10,'host shire’s own memory throughput','lab');
   CK.el('line',{x1:x(1),x2:x(1),y1:T,y2:H-B,style:'stroke:var(--ref);stroke-width:1.5;stroke-dasharray:5 4'},svg);
   CK.txt(svg,x(1)+6,T+14,narrow?'saturated: loads stop':'bank saturated: the host’s loads stop','lab');
   /* the load the sliders set */
   const xs=Math.max(0.03,Math.min(50,LOAD(N,P)));
   CK.el('line',{x1:x(xs),x2:x(xs),y1:T,y2:H-B,'aria-hidden':'true',style:'stroke:var(--ink);stroke-width:1.5;stroke-dasharray:2 3'},svg);
   /* label left of the line below saturation (clear of the band's own label); near the left edge, right of it and low, clear of the points */
   const lx=x(xs), left=(xs<1&&lx-L>90)||lx>W-120;
   CK.txt(svg,lx+(left?-6:6),xs>=1?T+32:left?T+14:H-B-10,'load '+lf(LOAD(N,P))+(LOAD(N,P)<0.03?' (off the scale)':''),'lab-strong',left?'end':'start');
   const nodes=[];
   const order=RUNS.slice().sort((a,b)=>a.x-b.x||(a.card<b.card?-1:1));
   for(const r of order){
    const g=CK.el('g',{'data-series':r.ser},svg), a2=A2(r), col=r.ser==='req'?'var(--c1)':'var(--c3)', px=x(Math.min(50,r.x)), py=y(r.frac_of_alone);
    const on=r.remote_minions===N&&r.pace===P;
    let m;
    if(r.ser==='req') m=CK.el('circle',{cx:px,cy:py,r:a2?5:8},g);
    else {const s=a2?10:15;m=CK.el('rect',{x:px-s/2,y:py-s/2,width:s,height:s,rx:1.5},g);}
    if(a2){m.style.fill=col;} else {m.style.fill='none';m.style.stroke=col;m.style.strokeWidth='1.5';}
    if(on&&a2){const ring=CK.el('circle',{cx:px,cy:py,r:13,fill:'none','aria-hidden':'true'},g);ring.style.stroke='var(--ink)';ring.style.strokeWidth='2';}
    const who=r.ser==='req'?`${n0(r.remote_minions)} minion${r.remote_minions>1?'s':''} of one other shire, no pause (host runs ${r.host_minions})`
                          :`${n0(r.remote_minions)} minions of 31 shires, pause ${n0(r.pace)} cycles (host runs ${r.host_minions})`;
    CK.tip(f,g,`<b>${who}</b> · ${r.card}<br>load ${lf(r.x)} predicted, ${lf(r.m)} measured<br>host at ${pct(r.frac_of_alone,r.frac_of_alone<0.01?3:1)} of alone`);
    nodes.push(g);
   }
   CK.keynav(f,nodes);
  }});
 CK.legend('reqlegend',[{key:'req',label:'one other shire, N minions, no pause (host runs N)',mark:'dot',color:'var(--c1)'},
  {key:'pace',label:`${n0(NP)} minions of 31 shires, paced (host runs ${p12[0].host_minions})`,mark:'box',color:'var(--c3)'}],
  {toggle:true,onChange:keys=>CK.showSeries(f,keys)});
 upd();
 $('reqcap').textContent=
  `The x axis is the predicted load, N × ${n0(BANK)} ÷ (P + ${n0(RT)}), not a measurement: each point's tooltip also gives the load `+
  `measured from its completed atomics, and in every unsaturated run the two agree within ${(100*err).toFixed(1)}%. Circles: one other `+
  `shire's N minions with no pause, while the host runs N minions (this section's sweep). Squares: ${n0(NP)} minions of 31 shires, paced, `+
  `while the host runs ${p12[0].host_minions} (section 5's sweep). Filled ${CARDS[0]}, hollow ${CARD3}. The dotted line and the ringed `+
  `point follow the sliders${RUNS.some(r=>r.x>50)?'; loads above 50 are drawn at 50':''}.`;
})();

/* ---------- section 4: errata ---------- */
if(CTX.errata) $('errata').innerHTML=CTX.errata.map(e=>
 `<div class="card" style="margin:12px 0"><div><b>Erratum ${e.num} — ${e.title}</b> <span class="small">(${e.id})</span></div>`+
 `<p class="small" style="margin:8px 0 6px">${e.quote}</p>`+
 `<p class="small" style="margin:0"><b>Impact:</b> ${e.impact} ${e.workaround?'<b>Workaround:</b> '+e.workaround:''} <b>Fix status:</b> ${e.fix}</p></div>`).join('');

/* ---------- section 5: pacing ---------- */
(function(){
 const rows=D.pace.filter(A2).sort((a,b)=>a.pace-b.pace), sat=rows[0].remote_ops_per_shire;
 const r3=D.pace.filter(A3), sat3=r3.find(r=>r.pace===0).remote_ops_per_shire, at3=p=>r3.find(r=>r.pace===p);
 const drawn=rows.filter(r=>r.pace>0), zero=rows[0], z3=at3(0);
 CK.legend('pacelegend',[{key:'host',label:'host shire’s own memory',mark:'dot',color:'var(--c1)'},
  {key:'rem',label:'the 31 hammering shires',mark:'box',color:'var(--c3)'},
  {key:'a3',label:`hollow: ${CARD3}`,mark:'ring',color:'var(--ink-2)'}]);
 CK.frame('pace',{label:'Host and hammering shires against the pause between atomics',height:W=>W<600?300:330,
  draw(f){
   const svg=f.svg,W=f.W,H=f.H,L=48,R=14,T=26,B=46,narrow=f.narrow;
   const x=CK.log(700,140000,L,W-R), y=CK.lin(0,1.05,H-B,T);
   CK.axes(f,{x,y,L,R,T,B,xt:narrow?[1000,10000,100000]:[1000,4000,10000,40000,100000],yt:[0,0.25,0.5,0.75,1],
    yfmt:v=>Math.round(100*v)+'%',xfmt:v=>v>=1000?n0(v/1000)+'k':String(v),xl:'cycles a remote minion waits between atomics'});
   CK.txt(svg,4,T-10,'fraction of what each side gets unpaced','lab');
   CK.el('path',{d:CK.path(drawn.map(r=>[r.pace,r.frac_of_alone]),x,y),fill:'none',style:'stroke:var(--c1);stroke-width:2'},svg);
   CK.el('path',{d:CK.path(drawn.map(r=>[r.pace,r.remote_ops_per_shire/sat]),x,y),fill:'none',style:'stroke:var(--c3);stroke-width:2'},svg);
   const nodes=[];
   for(const r of drawn){
    const b=at3(r.pace), g=CK.el('g',{},svg);
    const hit=CK.el('rect',{x:x(r.pace)-12,y:T,width:24,height:H-B-T,class:'ck-hit'},g);
    const d1=CK.el('circle',{cx:x(r.pace),cy:y(r.frac_of_alone),r:4.5},g); d1.style.fill='var(--c1)';
    const d2=CK.el('rect',{x:x(r.pace)-4.5,y:y(r.remote_ops_per_shire/sat)-4.5,width:9,height:9,rx:1.5},g); d2.style.fill='var(--c3)';
    const o1=CK.el('circle',{cx:x(b.pace),cy:y(b.frac_of_alone),r:7.5,fill:'none'},g); o1.style.stroke='var(--c1)';
    const o2=CK.el('rect',{x:x(b.pace)-7,y:y(b.remote_ops_per_shire/sat3)-7,width:14,height:14,rx:2,fill:'none'},g); o2.style.stroke='var(--c3)';
    CK.tip(f,g,`<b>pause ${n0(r.pace)} cycles</b> (${n0(r.remote_minions)} remote minions)<br>host shire ${pct(r.frac_of_alone,1)} of its own baseline (${pct(b.frac_of_alone,1)} on ${CARD3})`+
     `<br>hammering shires ${pct(r.remote_ops_per_shire/sat)} of their unpaced rate (${pct(b.remote_ops_per_shire/sat3)})`);
    nodes.push(g);
   }
   CK.keynav(f,nodes);
  }});
 const knee=rows.find(r=>r.frac_of_alone>0.4), before=rows.filter(r=>r.pace>0&&r.pace<knee.pace).map(r=>n0(r.pace));
 $('pacecap').textContent=
  `At ${n0(knee.pace)} cycles between atomics the host shire is back to ${pct(knee.frac_of_alone)} `+
  `while the hammering shires keep ${pct(knee.remote_ops_per_shire/sat)} of their rate. Nothing tested below ${n0(knee.pace)} cycles `+
  `(${before.slice(0,-1).join(', ')} or ${before[before.length-1]}) helps at all. No pause at all, not drawn on the log axis, gives the same as `+
  `${before[0]}: the host at ${pct(zero.frac_of_alone,2)}. Filled marks ${CARDS[0]}, hollow ${CARD3}.`;

 /* section 7's pacing rule, priced from the same runs */
 const NP=rows[0].remote_minions, need=NP*BANK-RT, ok=rows.find(r=>r.pace>need);
 const cost=r=>pct(1-r.remote_ops_per_shire/sat), at=p=>rows.find(r=>r.pace===p);
 const more=[12000,16000].map(at).filter(Boolean);
 $('pacerule').textContent=
  `keep N × ${n0(BANK)} cycles below the pause plus the ${n0(RT)}-cycle round trip. For the ${n0(NP)} here that is ${n0(ok.pace)} `+
  `cycles (about ${(ok.pace/CLOCK_MHZ).toFixed(0)} µs), which gives the host shire back about half its memory path (${pct(ok.frac_of_alone)}) for `+
  `${cost(ok)} of the hammering shires' rate; `+more.map(r=>`${n0(r.pace)} gives it ${pct(r.frac_of_alone)} for ${cost(r)}`).join(', and ')+` (section 5).`;
})();

/* ---------- section 6: placement ---------- */
(function(){
 const name={'0':'one DRAM line, homed in shire 0','scp:0':'one scratchpad word in shire 0',
   'own':'32 DRAM lines, one per shire','scp:own':'32 scratchpad words, one per shire'};
 const a3={}; D.placement.filter(A3).forEach(r=>{a3[r.home]=r;});
 const ms=WIN/(CLOCK_MHZ*1e3), rate=r=>n0(r.total_ops/(ms/1e3)/1e6)+' M/s';
 $('placetab').innerHTML=`<thead><tr><th>Where the atomic lives</th><th class="num">Atomics in a ${n0(ms)} ms window, a2 / a3</th><th class="num">Cycles per atomic</th><th class="num">Rate</th></tr></thead><tbody>`+
  D.placement.filter(A2).map(r=>{const b=a3[r.home];
   return `<tr><td>${name[r.home]||r.home}</td><td class="num">${both(n0(r.total_ops),n0(b.total_ops))}</td><td class="num">${both(f2(r.cycles_per_op),f2(b.cycles_per_op))}</td><td class="num">${both(rate(r),rate(b))}</td></tr>`;}).join('')+'</tbody>';
 CK.stackTable('placetab');
})();

/* ---------- section 6: energy ---------- */
(function(){
 const p=D.power, names={contended:'one DRAM line, 1,024 minions',spread:'32 DRAM lines, 1,024 minions',
  contended_scp:'one scratchpad word, 1,024 minions',starved:'one scratchpad word, host shire reading instead',
  local_only:'host shire reading, nobody hammering'};
 const nP=POOLED.nj.contended.n, pc=POOLED.nj.contended.per_card;
 const pool=l=>{const q=POOLED.nj[l];return q?`${f(q.mean)} [${f(q.lo)}–${f(q.hi)}]`:'—';}, f=v=>v<3?f2(v):f1(v);
 $('pwrtab').innerHTML=`<thead><tr><th>Case</th><th class="num">Operations per second</th><th class="num">Over idle, W</th><th class="num">nJ, first session (a2)</th><th class="num">nJ per operation, all passes: mean [range], n = ${nP}</th></tr></thead><tbody>`+
  p.runs.map(r=>`<tr><td>${names[r.label]||r.label}</td><td class="num">${n0(r.ops_per_s/1e6)} M</td><td class="num">${f2(r.over_idle_w)}</td><td class="num">${f(r.nj_per_op)}</td><td class="num">${pool(r.label)}</td></tr>`).join('')+
  `<tr><td>idle card, die at ${p.idle.die_c.toFixed(0)} °C</td><td class="num">0</td><td class="num">(idle ${f2(p.idle.board_w)} W)</td><td class="num">—</td><td class="num">—</td></tr></tbody>`;
 CK.stackTable('pwrtab');
 $('pooln').textContent=`n = ${nP}, ${word(pc[CARDS[0]].n)} on ${CARDS[0]} including this one, ${word(pc[CARD3].n)} on ${CARD3}`;
 /* the two reductions the pool mixes (power.json: analyze_hotline_power.py; the passes: analyze_reruns.py), and the reading-only row */
 const lo_=p.runs.find(r=>r.label==='local_only');
 $('pooltop').textContent=`This session was reduced against one idle for the whole session, with no leakage correction; `+
  `the 23 September passes against the idle just before and after each burst, corrected for leakage. The pool mixes the two. `+
  (lo_?`The reading-only row's ${f2(lo_.over_idle_w)} W is inside the idle baseline's ±0.2 W, so its energy is an order of magnitude, not a measurement.`:'');
 const w=POOLED.w_contended, c=p.runs.find(r=>r.label==='contended'), s=p.runs.find(r=>r.label==='spread');
 $('hlw').textContent=`about ${f1(w.mean)} W over idle (${f2(w.mean)} W on the mean of ${word(w.n)} passes, ${f1(w.lo)}–${f1(w.hi)} W; this session read ${f1(c.over_idle_w)} W)`;
 $('enfac').textContent=(POOLED.nj.contended.mean/POOLED.nj.spread.mean).toFixed(0);
})();

/* ---------- section 7: the barrier ---------- */
$('bar1').textContent=CTX.barrier_cycles_chip?n0(CTX.barrier_cycles_chip):'about 5,000';
