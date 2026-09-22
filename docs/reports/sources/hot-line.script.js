const NS='http://www.w3.org/2000/svg';
function el(t,a,p){const e=document.createElementNS(NS,t);for(const k in a)e.setAttribute(k,a[k]);if(p)p.appendChild(e);return e;}
function txt(p,x,y,s,c,an){const t=el('text',{x,y,class:c||'tick','text-anchor':an||'start'},p);t.textContent=s;return t;}
function host(id,W,H){const h=document.getElementById(id);h.innerHTML='';const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,role:'img'},h);const tip=document.createElement('div');tip.className='tip';h.appendChild(tip);return {svg,tip,h};}
function hover(g,tip,h,html){const s=ev=>{tip.innerHTML=html();tip.style.display='block';const b=h.getBoundingClientRect();tip.style.left=Math.max(0,Math.min(ev.clientX-b.left+12,b.width-290))+'px';tip.style.top=(ev.clientY-b.top+12)+'px';};g.addEventListener('mousemove',s);g.addEventListener('mouseleave',()=>tip.style.display='none');}
function path(pts,x,y){return pts.map((p,i)=>`${i?'L':'M'}${x(p[0]).toFixed(1)},${y(p[1]).toFixed(1)}`).join(' ');}
function axes(svg,o){const {W,H,L,R,T,B,x,y}=o;
 for(const t of o.yt){el('line',{x1:L,x2:W-R,y1:y(t),y2:y(t),class:'grid-line'},svg);txt(svg,L-6,y(t)+4,o.yf?o.yf(t):t,'tick','end');}
 for(const t of o.xt){txt(svg,x(t),H-B+16,o.xf?o.xf(t):t,'tick','middle');}
 if(o.xl)txt(svg,(L+W-R)/2,H-4,o.xl,'lab','middle');if(o.yl)txt(svg,4,T-8,o.yl,'lab');}
const f1=v=>v.toFixed(1),f2=v=>v.toFixed(2);
const f3=v=>v.toFixed(3);
const pick=(g,f)=>D[g].filter(f), A2=r=>r.card==='aifoundry2';

/* ---------- KPIs ---------- */
(function(){
 const fair=pick('fairness',r=>A2(r)&&r.home==='0'&&r.per_shire===32)[0];
 const loc=pick('local',r=>A2(r)&&r.home==='scplocal:0'&&r.shires>1)[0];
 const req=pick('requesters',r=>A2(r)).sort((a,b)=>a.remote_minions-b.remote_minions).find(r=>r.frac_of_alone<0.5);
 const pw=D.power.runs, c=pw.find(r=>r.label==='contended'), s=pw.find(r=>r.label==='spread');
 document.getElementById('k1').textContent=f3(fair.host_share);
 document.getElementById('k2').textContent=(100*loc.frac_of_alone).toFixed(2)+'%';
 document.getElementById('k3').textContent=req?req.remote_minions:'—';
 document.getElementById('k4').textContent=(c.nj_per_op/s.nj_per_op).toFixed(0)+'×';
 document.getElementById('enfac').textContent=(c.nj_per_op/s.nj_per_op).toFixed(0);
})();

/* ---------- section 1: per-shire shares ---------- */
(function(){
 const rows=D.fairness.filter(r=>A2(r)&&r.home==='0'&&r.per_shire===32);
 const raw=D.raw_shares||null;
 const W=700,H=300,L=52,R=16,T=26,B=46,{svg,tip,h}=host('fair',W,H);
 const sh=D.shares_home0||[];
 const y=v=>H-B-(H-B-T)*(v-0.9)/0.35, x=i=>L+(W-L-R)*(i+0.5)/32;
 axes(svg,{W,H,L,R,T,B,x,y,yt:[0.9,1.0,1.1,1.2],yf:v=>v.toFixed(2),xt:[],yl:'share of an even split'});
 el('line',{x1:L,x2:W-R,y1:y(1),y2:y(1),stroke:'var(--ref)','stroke-width':1.5,'stroke-dasharray':'5 4'},svg);
 [['1,024 minions: 32 per shire','var(--c1)','full'],['32 minions: 1 per shire','var(--c2)','one']].forEach((s2,i)=>{
   el('rect',{x:W-R-190,y:T-14+i*18,width:11,height:11,fill:s2[1]},svg);txt(svg,W-R-174,T-4+i*18,s2[0],'lab');});
 for(const key of ['full','one']){
   const arr=sh.filter(r=>r.kind===key), col=key==='full'?'var(--c1)':'var(--c2)';
   arr.forEach(r=>{const g=el('g',{},svg);
     el('circle',{cx:x(r.s),cy:y(r.share),r:key==='full'?3.2:3.2,fill:col,'fill-opacity':0.85},g);
     hover(g,tip,h,()=>`shire ${r.s}<br>${key==='full'?'32':'1'} minion${key==='full'?'s':''} per shire<br>share ${f3(r.share)}`);});
 }
 txt(svg,L,H-B+16,'shire 0',' tick');txt(svg,W-R,H-B+16,'shire 31','tick','end');
 document.getElementById('faircap').textContent=
  `Dashed line is an even split. With every minion taking part the whole chip lands within ${f3(Math.min(...sh.filter(r=>r.kind==='full').map(r=>r.share)))}–${f3(Math.max(...sh.filter(r=>r.kind==='full').map(r=>r.share)))}; `+
  `the host shire is at ${f3(rows[0].host_share)}. With one minion per shire the bank is not saturated and the host shire leads.`;
})();

/* ---------- section 1 table: home sweep, both cards ---------- */
document.getElementById('fairtab').innerHTML='<thead><tr><th>Card</th><th>Line homed in</th><th class="num">Minions per shire</th><th class="num">Host shire’s share</th><th class="num">Spread across 32 shires</th></tr></thead><tbody>'+
 D.fairness.map(r=>`<tr><td>${r.card}</td><td>shire ${r.home}</td><td class="num">${r.per_shire}</td><td class="num">${f3(r.host_share)}</td><td class="num">${f3(r.min_share)}–${f3(r.max_share)}</td></tr>`).join('')+'</tbody>';

/* ---------- section 2: placement ---------- */
document.getElementById('placetab').innerHTML='<thead><tr><th>Card</th><th>Where the atomic lives</th><th class="num">Atomics in a 10 ms window</th><th class="num">Cycles per atomic</th><th class="num">Rate</th></tr></thead><tbody>'+
 D.placement.map(r=>{const name={'0':'one DRAM line, homed in shire 0','scp:0':'one scratchpad word in shire 0',
   'own':'32 DRAM lines, one per shire','scp:own':'32 scratchpad words, one per shire'}[r.home]||r.home;
  return `<tr><td>${r.card}</td><td>${name}</td><td class="num">${r.total_ops.toLocaleString()}</td><td class="num">${f2(r.cycles_per_op)}</td><td class="num">${(r.total_ops/0.01/1e6).toFixed(0)} M/s</td></tr>`;}).join('')+'</tbody>';

/* ---------- section 3: the host shire's own traffic ---------- */
(function(){
 const alone={},with_={};
 D.local.forEach(r=>{const k=r.card+'|'+r.home;(r.shires===1?alone:with_)[k]=r;});
 const names={'scplocal':'its own scratchpad','dramlocal':'its own scratchpad','scpstream':'DRAM','dramstream':'DRAM'};
 const hotin={'scplocal':'scratchpad of the same shire','dramlocal':'L3 slice of the same shire',
              'scpstream':'scratchpad of the same shire','dramstream':'L3 slice of the same shire'};
 document.getElementById('localtab').innerHTML='<thead><tr><th>Card</th><th>Host shire is reading</th><th>Hot line is in the</th><th class="num">Alone</th><th class="num">While hammered</th><th class="num">Fraction</th></tr></thead><tbody>'+
  Object.keys(with_).map(k=>{const r=with_[k],a=alone[k],base=k.split('|')[1].split(':')[0];
   return `<tr><td>${r.card}</td><td>${names[base]}</td><td>${hotin[base]}</td><td class="num">${a.host_ops.toLocaleString()}</td><td class="num">${r.host_ops}</td><td class="num">${(100*r.frac_of_alone).toFixed(3)}%</td></tr>`;}).join('')+'</tbody>';
 document.getElementById('wintab').innerHTML='<thead><tr><th class="num">Window</th><th class="num">Host shire’s loads</th><th class="num">Remote atomics in the same window</th></tr></thead><tbody>'+
  D.context.window_independence.map(r=>`<tr><td class="num">${(r.window/600e3).toFixed(0)} ms</td><td class="num">${r.host_ops}</td><td class="num">${r.remote_ops.toLocaleString()}</td></tr>`).join('')+'</tbody>';
})();

/* ---------- section 4: requesters ---------- */
(function(){
 const rows=D.requesters.filter(A2).sort((a,b)=>a.remote_minions-b.remote_minions);
 const W=700,H=330,L=58,R=58,T=26,B=52,{svg,tip,h}=host('req',W,H);
 const xs=rows.map(r=>r.remote_minions),mx=Math.max(...xs);
 const x=v=>L+(W-L-R)*(v-1)/(mx-1), y=v=>H-B-(H-B-T)*v/1.2, y2=v=>H-B-(H-B-T)*(250-v)/250;
 axes(svg,{W,H,L,R,T,B,x,y,yt:[0,0.25,0.5,0.75,1.0],yf:v=>Math.round(100*v)+'%',xt:[1,8,16,24,32],
   xl:'minions of one other shire hammering the line',yl:'host shire’s own memory throughput'});
 for(const t of [10,50,100,200]) txt(svg,W-R+6,y2(t)+4,t,'tick');
 txt(svg,W-R-4,T-8,'cycles per remote atomic','lab','end');
 el('path',{d:path(rows.map(r=>[r.remote_minions,Math.min(250,6e6/Math.max(r.remote_ops_per_shire,1))]),x,y2),
            class:'ln s2','stroke-dasharray':'5 4'},svg);
 el('path',{d:path(rows.map(r=>[r.remote_minions,r.frac_of_alone]),x,y),class:'ln s1'},svg);
 rows.forEach(r=>{const g=el('g',{},svg);
  el('circle',{cx:x(r.remote_minions),cy:y(r.frac_of_alone),r:4,fill:'var(--c1)'},g);
  hover(g,tip,h,()=>`${r.remote_minions} remote minions<br>host at ${(100*r.frac_of_alone).toFixed(2)}% of alone<br>remote atomic every ${f1(6e6/r.remote_ops_per_shire)} cycles`);});
 document.getElementById('reqcap').textContent=
  'Solid: the host shire’s own loads, as a fraction of the same loop with nobody hammering. Dashed, right axis: '+
  'how often the remote shire completes an atomic. The cliff is where that reaches 10 cycles, the rate one shire cache can retire.';
})();

/* ---------- section 5: errata ---------- */
document.getElementById('errata').innerHTML=D.context.errata.map(e=>
 `<div class="card" style="margin:12px 0"><div><b>Erratum ${e.num} — ${e.title}</b> <span class="small">(${e.id})</span></div>`+
 `<p class="small" style="margin:8px 0 6px">${e.quote}</p>`+
 `<p class="small" style="margin:0"><b>Impact:</b> ${e.impact} ${e.workaround?'<b>Workaround:</b> '+e.workaround:''} <b>Fix status:</b> ${e.fix}</p></div>`).join('');

/* ---------- section 6: pacing ---------- */
(function(){
 const rows=D.pace.filter(A2).sort((a,b)=>a.pace-b.pace), sat=rows[0].remote_ops_per_shire;
 const W=700,H=320,L=58,R=16,T=26,B=52,{svg,tip,h}=host('pace',W,H);
 const x=v=>L+(W-L-R)*Math.log10(Math.max(v,500)/500)/Math.log10(100000/500), y=v=>H-B-(H-B-T)*v/1.05;
 axes(svg,{W,H,L,R,T,B,x,y,yt:[0,0.25,0.5,0.75,1.0],yf:v=>Math.round(100*v)+'%',xt:[1000,4000,10000,40000,100000],
   xf:v=>v>=1000?(v/1000)+'k':v,xl:'cycles a remote minion waits between atomics',yl:'fraction of what each side gets unpaced'});
 el('path',{d:path(rows.map(r=>[r.pace,r.frac_of_alone]),x,y),class:'ln s1'},svg);
 el('path',{d:path(rows.map(r=>[r.pace,r.remote_ops_per_shire/sat]),x,y),class:'ln s3'},svg);
 rows.forEach(r=>{const g=el('g',{},svg);
  el('circle',{cx:x(r.pace),cy:y(r.frac_of_alone),r:3.5,fill:'var(--c1)'},g);
  el('circle',{cx:x(r.pace),cy:y(r.remote_ops_per_shire/sat),r:3.5,fill:'var(--c3)'},g);
  hover(g,tip,h,()=>`pace ${r.pace.toLocaleString()} cycles<br>host shire ${(100*r.frac_of_alone).toFixed(1)}% of its own baseline<br>hammering shires ${(100*r.remote_ops_per_shire/sat).toFixed(0)}% of their unpaced rate`);});
 [['host shire’s own memory','var(--c1)'],['the 31 hammering shires','var(--c3)']].forEach((s2,i)=>{
  el('rect',{x:L+12,y:T-14+i*18,width:11,height:11,fill:s2[1]},svg);txt(svg,L+28,T-4+i*18,s2[0],'lab');});
 const knee=rows.find(r=>r.frac_of_alone>0.4);
 document.getElementById('pacecap').textContent=
  `At ${knee.pace.toLocaleString()} cycles between atomics the host shire is back to ${(100*knee.frac_of_alone).toFixed(0)}% `+
  `while the hammering shires keep ${(100*knee.remote_ops_per_shire/sat).toFixed(0)}% of their rate. Nothing below 10,000 cycles helps at all.`;
})();

/* ---------- section 7: power ---------- */
(function(){
 const p=D.power, names={contended:'one DRAM line, 1,024 minions',spread:'32 DRAM lines, 1,024 minions',
  contended_scp:'one scratchpad word, 1,024 minions',starved:'one scratchpad word, host shire reading instead',
  local_only:'host shire reading, nobody hammering'};
 document.getElementById('pwrtab').innerHTML='<thead><tr><th>Case</th><th class="num">Operations per second</th><th class="num">Board W</th><th class="num">Over idle</th><th class="num">nJ per operation</th></tr></thead><tbody>'+
  p.runs.map(r=>`<tr><td>${names[r.label]||r.label}</td><td class="num">${(r.ops_per_s/1e6).toFixed(0)} M</td><td class="num">${f2(r.board_w)}</td><td class="num">${f2(r.over_idle_w)}</td><td class="num">${f1(r.nj_per_op)}</td></tr>`).join('')+
  `<tr><td>idle card</td><td class="num">0</td><td class="num">${f2(p.idle.board_w)}</td><td class="num">—</td><td class="num">—</td></tr></tbody>`;
})();
