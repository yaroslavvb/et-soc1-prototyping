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
 /* N and P are shared with section 2's diagram over bus('hotNP'): a slider tells it, and its steps move the sliders */
 const busNP=CK.bus('hotNP'); let fromBus=false;
 const tell=()=>{if(!fromBus)busNP.emit({N,P},'req');};
 const rN=CK.range('reqN',{label:'Remote minions, N',stops:[1,2,4,8,12,16,20,24,32,64,256,NP],value:N,fmt:n0,onInput:v=>{N=v;upd();tell();}});
 const rP=CK.range('reqP',{label:'Pause between atomics, P (cycles)',stops:[0,1000,4000,8000,10000,12000,16000,20000,40000,100000],value:P,fmt:n0,onInput:v=>{P=v;upd();tell();}});
 busNP.on((v,from)=>{if(from==='req'||!(v.N>0))return;fromBus=true;rN.set(v.N);rP.set(v.P);fromBus=false;});   // N = 0 (nobody hammering) is not on the slider
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

/* ---------- section 2: inside the host shire, step by step ----------
   One shire drawn schematically: its minions and their own loads (blue), the remote atomics arriving over the mesh
   (green), the queues in front of the bank, and the bank. Three steps: nobody else running, remote atomics below the
   bank's capacity, and above it. The queue slots and moving tokens are schematic (queue depth was not measured);
   every number drawn or printed comes from D: the bank's cycles and the round trip (context), the host's counts
   (local, shires, requesters, pace). N and P are shared with section 3's sliders over bus('hotNP'). No motion under
   prefers-reduced-motion, and a Motion switch stops it; the steps work the same either way. */
(function(){
 if(!$('starve'))return;
 if(!RT||!BANK){$('inside-the-host-shire').hidden=true;return;}
 const busNP=CK.bus('hotNP'), ms=WIN/(CLOCK_MHZ*1e3);
 const oneEach=rows=>CK.cardsIn(rows.map(r=>r.card)).map(c=>rows.find(r=>r.card===c));   // one row per card, registry order
 const alone=oneEach(D.local.filter(r=>r.home==='scplocal:0'&&r.shires===1));
 const SHIRE=alone[0].host_minions;                                                     // the host's minions, all streaming alone
 const shR=D.shires.filter(r=>r.home==='scplocal:0');                                   // 1 to 31 other shires, every minion hammering
 const NP=Math.max(...D.pace.map(r=>r.remote_minions));
 const paces=[...new Set(D.pace.map(r=>r.pace))].sort((a,b)=>a-b);
 const PB=paces.find(p=>p>0&&D.pace.filter(r=>r.pace===p).every(r=>r.frac_of_alone>=0.9));  // the first pause that gives the host 90% back on every card
 const PRE={alone:{N:0,P:0},below:{N:NP,P:PB},sat:{N:NP,P:0}};
 const STEPS=[['alone','1 · alone'],['below','2 · below the knee'],['sat','3 · saturated']];
 const stateOf=(n,p)=>n===0?'alone':LOAD(n,p)<1?'below':'sat';
 let N=0,P=0,st='alone',motion=!CK.reduced,f=null;
 const hits=()=>st==='alone'?alone:oneEach(RUNS.filter(r=>r.remote_minions===N&&r.pace===P));
 /* a value per card, printed once when every card agrees (this page's convention for a2 / a3) */
 const vals=(rows,fmt)=>{const v=rows.map(fmt);if(v.every(x=>x===v[0]))return v[0];
  const p=rows.map((r,i)=>`${v[i]} (${r.card})`);return p.slice(0,-1).join(', ')+' and '+p[p.length-1];};
 const span=a=>{const lo=Math.min(...a),hi=Math.max(...a);return lo===hi?n0(lo):n0(lo)+'–'+n0(hi);};
 const where=run=>run?(run.shires>2?`${n0(N)} minions in ${run.shires-1} other shires`:`${n0(N)} minion${N>1?'s':''} of one other shire`):`${n0(N)} remote minions`;
 const satRuns=RUNS.filter(r=>r.x>=1);                                                  // every run on section 3's chart at a load of 1 or more
 function say(){
  const h=hits(), run=h[0]||null, x=LOAD(N,P);
  if(st==='alone') return `<b>1 · Alone.</b> Nobody else is running. The host shire's ${SHIRE} minions stream their own scratchpad: `+
   `${vals(h,r=>n0(r.host_ops))} loads in the ${n0(ms)} ms window, one every ${vals(h,r=>f2(r.cycles_per_op))} cycles across the shire.`;
  const ask=`${n0(N)} × ${n0(BANK)} ÷ (${n0(P)} + ${n0(RT)}) = ${lf(x)}`, pause=P?`and then waiting ${n0(P)} cycles`:'with no pause';
  const meas=run?` <b>Measured:</b> the host shire, running ${run.host_minions} minions, kept ${vals(h,r=>pct(r.frac_of_alone,r.frac_of_alone<0.01?2:1))} `+
    `of its rate alone, ${vals(h,r=>n0(r.host_ops))} loads in the window.`:' <b>This setting was not run;</b> the load is a prediction.';
  if(st==='below'){
   const short=!run||Math.min(...h.map(r=>r.frac_of_alone))<0.9;
   return `<b>2 · Below the knee.</b> ${where(run)}, each sending an atomic ${pause}, with the ${n0(RT)}-cycle round trip ask for `+
    `${ask} of the bank's cycles, less than it can retire, so the queue can drain between arrivals and the host's loads get the gaps.${meas}`+
    (short?' Staying below 1 is necessary, not sufficient (section 3).':'');
  }
  const lo=Math.min(...satRuns.map(r=>r.frac_of_alone)), hi=Math.max(...satRuns.map(r=>r.frac_of_alone));
  return `<b>3 · Saturated.</b> ${where(run)}, each sending an atomic ${pause}, ask for ${ask} times the bank's cycles: the remote queue `+
   `does not empty, and remote requests outrank the host's own.${meas}`+
   (run?'':` Every run on section 3's chart at a load of 1 or more left the host at ${pct(lo,2)}${pct(hi,2)===pct(lo,2)?'':'–'+pct(hi,2)} of its rate.`)+
   ` With ${span(shR.map(r=>r.shires-1))} other shires hammering, all of their minions taking part, the host's ${shR[0].host_minions} minions complete `+
   `${span(shR.map(r=>r.host_ops))} loads in the window (${CK.cardsIn(shR.map(r=>r.card)).join(', ')}), stalled in a load that does not return.`;
 }
 const out=CK.readout('starveout');
 const seg=CK.seg('starvestep',{label:'Step',options:STEPS,value:st,onChange:v=>{st=v; ({N,P}=PRE[v]); busNP.emit({N,P},'diagram'); upd();}});
 if(!CK.reduced) CK.seg('starvemotion',{label:'Motion',options:[['on','moving'],['off','still']],value:'on',onChange:v=>{motion=v==='on';upd();}});
 busNP.on((v,from)=>{if(from==='diagram')return; N=v.N; P=v.P; st=stateOf(N,P); seg.quiet(st); upd();});
 function upd(){out.set(say()); if(f)f.redraw();}

 const HOST='var(--c1)', REM='var(--c3)';
 f=CK.frame('starve',{label:'Inside the host shire: its minions’ own loads and the remote atomics queue for one bank; remote requests go first',
  height:W=>W<600?570:300,
  draw(f){
   const svg=f.svg,W=f.W,nar=f.narrow,h=hits(),run=h[0]||null,x=LOAD(N,P),sat=st==='sat',idle=st==='alone';
   const hostOn=idle?SHIRE:(run?run.host_minions:SHIRE);
   const others=idle?0:(run?run.shires-1:Math.ceil(N/SHIRE)), per=others?Math.min(SHIRE,Math.round(N/others)):0;
   const move=motion&&!CK.reduced, labs=[];
   const T=(px,py,s,cls,a)=>{const t=CK.txt(svg,px,py,s,cls||'lab',a);labs.push(t);return t;};
   /* ---- layout: wide runs left to right (minions, bank, mesh), narrow top to bottom (mesh, bank, minions) ---- */
   const S=14,GP=4,gw=8*S+7*GP,gh=4*S+3*GP, SL=12,SP=17, bw=72,bh=54;
   let L;
   if(!nar){
    const x1=W-246, cy=128, gx=22, bx=gx+gw+(x1-gx-gw)*0.45;
    L={box:[8,28,x1,222],title:[18,46,'start'],grid:[gx,cy-gh/2+6],gridLab:[gx,cy+gh/2+26,'start'],
     bank:[bx-bw/2,cy-bh/2],A:[gx+gw+10,cy],B:[bx-bw/2-6,cy],C:[x1,cy],D:[bx+bw/2+6,cy],
     nH:Math.max(2,Math.floor((bx-bw/2-6-gx-gw-24)/SP)),nR:Math.max(2,Math.floor((x1-bx-bw/2-24)/SP)),
     hLab:[(gx+gw+bx-bw/2)/2,cy-16,'middle'],rLab:[(x1+bx+bw/2)/2,cy-16,'middle'],bankNote:[bx,cy+bh/2+18,'middle'],
     first:[bx,cy-bh/2-8,'middle'],blk:[W-200,cy-40],E:[W-208,cy],oLab:[W-200,cy-56,'start'],
     oTxt:[[W-200,cy+58],[W-200,cy+74],[W-200,cy+90]],gauge:[8,262,W-16,12],gLab:[8,254],gEnd:[W-8,290]};
   } else {
    const lx=82, bY=246;
    L={box:[4,122,W-4,496],title:[W-12,142,'end'],grid:[lx-gw/2+4,bY+bh+14+4*SP+14],gridLab:[lx-gw/2+4,bY+bh+14+4*SP+14+gh+18,'start'],
     bank:[lx-bw/2,bY],A:[lx,bY+bh+14+4*SP+6],B:[lx,bY+bh+6],C:[lx,122],D:[lx,bY-6],nH:4,nR:Math.max(2,Math.floor((bY-6-122-10)/SP)),
     hLab:[lx+16,bY+bh+14+2*SP,'start'],rLab:[lx+16,(122+bY)/2+4,'start'],bankNote:[lx+bw/2+8,bY+bh/2+22,'start'],
     first:[lx+bw/2+8,bY+bh/2-6,'start'],blk:[lx-65,34],E:[lx,101],oLab:[8,14,'start'],
     oTxt:[[158,48],[158,66],[158,84]],gauge:[8,532,W-16,12],gLab:[8,524],gEnd:[W-8,560]};
   }
   const lerp=(p,q,t)=>[p[0]+(q[0]-p[0])*t,p[1]+(q[1]-p[1])*t];
   const slotAt=(p,q,n,k)=>{const len=Math.hypot(q[0]-p[0],q[1]-p[1]);return lerp(q,p,(SL/2+2+k*SP)/len);};  // k = 0 is the queue's head, next to the bank
   /* ---- the host shire ---- */
   const [bx0,by0,bx1,by1]=L.box;
   const box=CK.el('rect',{x:bx0,y:by0,width:bx1-bx0,height:by1-by0,rx:12,'aria-hidden':'true'},svg);
   box.style.fill='none'; box.style.stroke='var(--axis)'; box.style.strokeWidth='1.5';
   T(L.title[0],L.title[1],'host shire (holds the hot line)','lab-strong',L.title[2]);
   /* lanes */
   const lane=(p,q,col,dash)=>{const e=CK.el('line',{x1:p[0],y1:p[1],x2:q[0],y2:q[1],'aria-hidden':'true'},svg);e.style.stroke=col;e.style.strokeWidth='2';if(dash)e.style.strokeDasharray='4 4';return e;};
   lane(L.A,L.B,HOST,false); lane(L.C,L.D,idle?'var(--grid)':REM,idle); lane(L.E,L.C,idle?'var(--grid)':REM,idle);
   const tok=(g,p,col,hollow)=>{const c=CK.el('circle',{cx:p[0],cy:p[1],r:5,'aria-hidden':'true'},g);
    if(hollow){c.style.fill='var(--surface)';c.style.stroke=col;c.style.strokeWidth='1.5';}else c.style.fill=col;return c;};
   const slots=(p,q,n)=>{for(let k=0;k<n;k++){const [sx,sy]=slotAt(p,q,n,k);
    const r=CK.el('rect',{x:sx-SL/2-2,y:sy-SL/2-2,width:SL+4,height:SL+4,rx:3,'aria-hidden':'true'},svg);r.style.fill='var(--surface)';r.style.stroke='var(--axis)';}};
   slots(L.A,L.B,L.nH); slots(L.C,L.D,L.nR);
   /* tokens in flight along a path: moving, or (still) spread along it */
   const fly=(pts,col,n,dur)=>{const g=CK.el('g',{'aria-hidden':'true'},svg);
    const segs=pts.slice(1).map((q,i)=>Math.hypot(q[0]-pts[i][0],q[1]-pts[i][1])), tot=segs.reduce((a,b)=>a+b,0);
    const at=t=>{let d=t*tot;for(let i=0;i<segs.length;i++){if(d<=segs[i])return lerp(pts[i],pts[i+1],d/segs[i]);d-=segs[i];}return pts[pts.length-1];};
    for(let k=0;k<n;k++){
     if(move){const c=tok(g,[0,0],col);const a=CK.el('animateMotion',{dur:dur+'s',repeatCount:'indefinite',begin:(-k*dur/n).toFixed(2)+'s',
       path:'M'+pts.map(p=>p[0].toFixed(1)+','+p[1].toFixed(1)).join(' L')},c);a.setAttribute('calcMode','linear');}
     else tok(g,at((k+0.5)/n),col);
    }};
   const q=(p,qq,n,col,hollow)=>{for(let k=0;k<n;k++)tok(svg,slotAt(p,qq,n,k),col,hollow);};
   if(!sat){
    fly([L.A,L.B],HOST,3,1.6);
    if(!idle) fly([L.E,L.C,L.D],REM,2,x>0.5?2.4:3.6);
   } else {
    q(L.A,L.B,L.nH,HOST,false); q(L.C,L.D,L.nR,REM,false);
    fly([slotAt(L.C,L.D,L.nR,0),L.D],REM,1,0.5);      // the head of the remote queue goes in, again and again
    const [sx,sy]=L.B, v=nar?[[sx-10,sy],[sx+10,sy]]:[[sx,sy-10],[sx,sy+10]];   // a bar across the host's lane: its loads wait
    const bar=CK.el('line',{x1:v[0][0],y1:v[0][1],x2:v[1][0],y2:v[1][1],'aria-hidden':'true'},svg); bar.style.stroke='var(--ink)'; bar.style.strokeWidth='3';
   }
   T(L.hLab[0],L.hLab[1],sat?'own loads: waiting':'own loads','lab',L.hLab[2]);
   T(L.rLab[0],L.rLab[1],idle?'no remote atomics':sat?'remote atomics: queue full':'remote atomics: queue drains','lab',L.rLab[2]);
   /* the host's minions */
   const gHost=CK.el('g',{},svg);
   for(let k=0;k<SHIRE;k++){const cx=L.grid[0]+(k%8)*(S+GP),cy2=L.grid[1]+Math.floor(k/8)*(S+GP),on=k<hostOn;
    const r=CK.el('rect',{x:cx,y:cy2,width:S,height:S,rx:2},gHost);
    if(!on){r.style.fill='none';r.style.stroke='var(--grid)';}
    else if(sat){r.style.fill='var(--surface)';r.style.stroke=HOST;r.style.strokeWidth='1.5';}
    else r.style.fill=HOST;}
   T(L.gridLab[0],L.gridLab[1],`${hostOn}${hostOn<SHIRE?' of '+SHIRE:''} minions ${sat?'stalled in a load':'streaming'}`,'lab',L.gridLab[2]);
   CK.tip(f,gHost,()=>`<b>The host shire's minions</b> · ${hostOn} of ${SHIRE} running, ${sat?'each stalled in a load that does not return':'streaming 64-byte-strided loads over their own scratchpad'}`+
    (run?`<br>measured: ${vals(h,r=>n0(r.host_ops))} loads in the ${n0(ms)} ms window`:'<br>this setting was not run'));
   /* the bank */
   const gBank=CK.el('g',{},svg), [kx,ky]=L.bank;
   /* the bank's cycles, split: the share the remote atomics ask for (green, capped at all of them) and what is left (blue) */
   const rs=idle?0:Math.min(1,x), tint=c=>`color-mix(in srgb, ${c} 30%, var(--surface))`;
   const bb=CK.el('rect',{x:kx,y:ky,width:bw,height:bh,rx:8},gBank); bb.style.fill=tint(HOST);
   if(rs>0){const rr=CK.el('rect',{x:kx+bw*(1-rs),y:ky,width:bw*rs,height:bh,rx:rs>0.9?8:0,'aria-hidden':'true'},gBank); rr.style.fill=tint(REM);}
   const bk=CK.el('rect',{x:kx,y:ky,width:bw,height:bh,rx:8,'aria-hidden':'true'},gBank);
   bk.style.fill='none'; bk.style.stroke='var(--ink)'; bk.style.strokeWidth='1.5';
   CK.txt(gBank,kx+bw/2,ky+bh/2+4,'bank','lab-strong','middle');
   T(L.bankNote[0],L.bankNote[1],`${n0(BANK)} cycles per atomic`,'lab',L.bankNote[2]);
   if(sat) T(L.first[0],L.first[1],'remote requests go first','lab-strong',L.first[2]);
   CK.tip(f,gBank,()=>`<b>The bank</b> of the host's shire cache that holds the hot line<br>a global atomic takes ${n0(BANK)} cycles of it (the measured floor, section 3)`+
    `<br>${idle?'no remote atomics: all of it is the host’s':`remote atomics ask for ${lf(x)} of its cycles (predicted; green in the box, capped at all of them)`}`);
   /* the other shires */
   const gRem=CK.el('g',{},svg), [ox,oy]=L.blk, c2=12, g2=3, ow=8*(c2+g2)+5, oh=4*(c2+g2)+5;
   if(others>1) for(const d of [8,4]){const sh=CK.el('rect',{x:ox+d,y:oy-d,width:ow,height:oh,rx:6},gRem);sh.style.fill='var(--surface)';sh.style.stroke='var(--axis)';}
   const ob=CK.el('rect',{x:ox,y:oy,width:ow,height:oh,rx:6},gRem); ob.style.fill='var(--surface)'; ob.style.stroke=idle?'var(--grid)':'var(--axis)';
   for(let k=0;k<SHIRE;k++){const r=CK.el('rect',{x:ox+4+(k%8)*(c2+g2),y:oy+4+Math.floor(k/8)*(c2+g2),width:c2,height:c2,rx:2},gRem);
    if(k<per)r.style.fill=REM;else{r.style.fill='none';r.style.stroke='var(--grid)';}}
   T(L.oLab[0],L.oLab[1],idle?'other shires: idle':!run?'other shires':others>1?`other shires (${others})`:'another shire','lab-strong',L.oLab[2]);
   const lines=idle?['nobody hammering']:[`N = ${n0(N)} minions`,`P = ${n0(P)} cycles' pause`,`round trip ${n0(RT)} cycles`];
   lines.forEach((s,i)=>T(L.oTxt[i][0],L.oTxt[i][1],s,'lab','start'));
   CK.tip(f,gRem,()=>idle?'<b>The other shires</b> · not running':`<b>${where(run)}</b> · each sends an <code>amoaddg.w</code> to the hot line, waits for it, then pauses ${n0(P)} cycles`+
    `<br>an atomic's round trip: ${n0(RT)} cycles (one requester, bank idle, from shire ${CTX.remote_atomic_latency_shire})`);
   /* the bank's cycles the remote atomics ask for (predicted, the x axis of section 3) */
   const gG=CK.el('g',{},svg), [gx0,gy0,gw0,gh0]=L.gauge;
   const bg=CK.el('rect',{x:gx0,y:gy0,width:gw0,height:gh0,rx:3},gG); bg.style.fill='var(--grid)';
   if(x>0){const fl=CK.el('rect',{x:gx0,y:gy0,width:gw0*Math.min(1,x),height:gh0,rx:3},gG); fl.style.fill=REM;}
   T(L.gLab[0],L.gLab[1],idle?'bank cycles asked for by remote atomics: none':`bank cycles asked for: ${n0(N)} × ${n0(BANK)} ÷ (${n0(P)} + ${n0(RT)}) = ${lf(x)}`,'lab','start');
   T(L.gEnd[0],L.gEnd[1],x>=1?`all of them, ${num(x,1)} times over`:'1 = all of its cycles','tick','end');
   CK.tip(f,gG,()=>`<b>Bank load ${idle?'0':lf(x)}</b> (predicted: N × ${n0(BANK)} ÷ (P + ${n0(RT)}))<br>${x>=1?'more than the bank can retire: the remote queue stays full':'less than the bank can retire: the queue drains'}`);
   CK.keynav(f,[gRem,gBank,gHost,gG]);
   CK.inside(f,labs);
  }});
 upd();
 $('starvecap').textContent=
  `Blue is the host shire's own loads, green the remote atomics. The queue slots and tokens are schematic: how deep the queues are was not measured. `+
  `The numbers are this page's: ${n0(BANK)} cycles of bank per atomic and the ${n0(RT)}-cycle round trip from the sweeps (section 3), the host's counts `+
  `from the table below and from section 3's runs. Step 2 is ${n0(NP)} remote minions paced at ${n0(PB)} cycles, the first pause in section 5 that gives `+
  `the host 90% back on every card; step 3 is the same minions with no pause. ${CK.reduced?'Motion is off because this browser asks for reduced motion.':'The Motion switch stops the tokens.'}`;
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

 /* the table's last column drawn: each case's range over the pooled passes, their mean, and each card's mean (CK's
    card registry: every card in per_card, with its colour and mark). The reading-only row is grey: see pooltop. */
 const rows=p.runs.filter(r=>POOLED.nj[r.label]).map(r=>({label:r.label,name:names[r.label]||r.label,q:POOLED.nj[r.label],s:r.nj_per_op}));
 const ecards=CK.cardsIn([...new Set([].concat(...rows.map(r=>Object.keys(r.q.per_card||{}))))]);
 const rough=r=>r.label==='local_only';
 const C=POOLED.nj.contended, Sp=POOLED.nj.spread;
 CK.legend('nrglegend',[{key:'rng',label:`range of the ${word(nP)} passes`,mark:'line',color:'var(--ink-2)'},{key:'mean',label:'their mean (tick)',mark:'box',color:'var(--ink)'}]
  .concat(CK.cardLegend(ecards).map(it=>({...it,label:it.label+' mean'}))));
 const tipE=r=>{const q=r.q,pc=q.per_card||{};
  return `<b>${r.name}</b><br>${f(q.mean)} nJ per operation, mean of ${q.n} passes [${f(q.lo)}–${f(q.hi)}]<br>`+
   ecards.filter(c=>pc[c]).map(c=>`${CK.card(c).label} ${f(pc[c].mean)} (n = ${pc[c].n})`).join(', ')+
   `<br>first session (${CARDS[0]}): ${f(r.s)}`+(rough(r)?'<br>an order of magnitude only: its power is inside the idle baseline\u2019s noise':'');};
 CK.frame('nrg',{label:'Energy per operation for each hot-line case: range over the pooled passes, mean, and each card\u2019s mean, log scale',
  height:()=>rows.length*50+54,
  draw(fr){
   const svg=fr.svg,W=fr.W,L=8,R=12,T=8,RH=50,B=46,H=fr.H;
   const lo=Math.min(...rows.map(r=>r.q.lo)), hi=Math.max(...rows.map(r=>r.q.hi));
   const x=CK.log(lo/1.5,hi*1.6,L+6,W-R);
   CK.axes(fr,{x,y:CK.lin(0,1,H-B,T),L,R,T,B,yt:[],xt:[0.5,1,2,5,10,20].filter(v=>v>lo/1.5&&v<hi*1.6),xfmt:v=>num(v),
    xl:'nJ per operation (log scale)'});
   for(const t of [0.5,1,2,5,10,20].filter(v=>v>lo/1.5&&v<hi*1.6)) CK.el('line',{x1:x(t),x2:x(t),y1:T,y2:H-B,class:'grid-line','aria-hidden':'true'},svg);
   const nodes=[], labs=[];
   rows.forEach((r,i)=>{
    const y0=T+i*RH, yc=y0+32, q=r.q, g=CK.el('g',{},svg), col=rough(r)?'var(--ref)':'var(--ink-2)';
    CK.el('rect',{x:L,y:y0,width:W-L-R,height:RH,class:'ck-hit'},g);
    labs.push(CK.txt(g,L,y0+14,r.name+(rough(r)?' · order of magnitude':''),'lab'));
    const wk=CK.el('g',{'aria-hidden':'true'},g); wk.style.stroke=col; wk.style.strokeWidth='1.5';
    if(rough(r)) wk.style.strokeDasharray='4 3';
    CK.el('line',{x1:x(q.lo),x2:x(q.hi),y1:yc,y2:yc},wk);
    for(const v of [q.lo,q.hi]) CK.el('line',{x1:x(v),x2:x(v),y1:yc-6,y2:yc+6,style:'stroke-dasharray:none'},wk);
    const m=CK.el('rect',{x:x(q.mean)-1.5,y:yc-10,width:3,height:20,'aria-hidden':'true'},g); m.style.fill=rough(r)?'var(--ref)':'var(--ink)';
    const pc=q.per_card||{}, cs=ecards.filter(c=>pc[c]);
    cs.forEach((c,ci)=>CK.cardMark(g,c,x(pc[c].mean),yc+(ci-(cs.length-1)/2)*9,3.5).setAttribute('aria-hidden','true'));
    if(r.label==='spread') labs.push(CK.txt(g,x(q.hi)+10,yc+4,`${(C.mean/Sp.mean).toFixed(0)}× less than one contended line`,'lab'));
    CK.tip(fr,g,tipE(r)); nodes.push(g);
   });
   CK.keynav(fr,nodes);
   CK.inside(fr,labs);
  }});
 $('nrgcap').textContent=`Log scale. Each line is a case's range over the ${word(nP)} pooled passes of the table's last column, the tick their mean, and the marks `+
  `each card's own mean (${ecards.map(c=>`${CK.card(c).label} ${CK.card(c).mark==='dot'?'filled':CK.card(c).mark}`).join(', ')}). The contended line costs `+
  `${f(C.mean)} nJ per atomic [${f(C.lo)}–${f(C.hi)}] and the spread one ${f(Sp.mean)} [${f(Sp.lo)}–${f(Sp.hi)}]: the ranges are far apart. `+
  `The reading-only row is grey and dashed because its power is inside the idle baseline's noise (the note above).`;
})();

/* ---------- section 7: the barrier ---------- */
$('bar1').textContent=CTX.barrier_cycles_chip?n0(CTX.barrier_cycles_chip):'about 5,000';
