const NS='http://www.w3.org/2000/svg';
function el(t,a,p){const e=document.createElementNS(NS,t);for(const k in a)e.setAttribute(k,a[k]);if(p)p.appendChild(e);return e;}
function txt(p,x,y,s,c,an){const t=el('text',{x,y,class:c||'tick','text-anchor':an||'start'},p);t.textContent=s;return t;}
function host(id,W,H){const h=document.getElementById(id);h.innerHTML='';const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,role:'img'},h);const tip=document.createElement('div');tip.className='tip';h.appendChild(tip);return {svg,tip,h};}
function hover(g,tip,h,html){const s=ev=>{tip.innerHTML=html();tip.style.display='block';const b=h.getBoundingClientRect();tip.style.left=Math.max(0,Math.min(ev.clientX-b.left+12,b.width-290))+'px';tip.style.top=(ev.clientY-b.top+12)+'px';};g.addEventListener('mousemove',s);g.addEventListener('mouseleave',()=>tip.style.display='none');}
const NAMES={zeros:'zeros',ones:'ones',twos:'twos',pi:'π everywhere',onebit:'one set bit',checker:'checkerboard 1,0,1,0',ternary:'ternary −1, 0, 1',sparse75:'random normal, 75% zeroed',sparse50:'random normal, 50% zeroed',uniform:'random uniform [0,1)',randn:'random normal',signs:'random sign, ±1',pow2:'random exponent, 2^k',mant:'random mantissa, [1,2)',a_randn_b_ones:'A random, B ones',a_ones_b_randn:'A ones, B random'};
const COL={zeros:'var(--c1)',ones:'var(--c4)',pi:'var(--c3)',sparse50:'var(--c7)',uniform:'var(--c5)',randn:'var(--bad)'};
const MAIN=['zeros','ones','pi','sparse50','uniform','randn'].filter(p=>D.patterns[p]);
const ORDER=Object.keys(D.patterns).sort((a,b)=>D.patterns[a].p80-D.patterns[b].p80);
const col=p=>COL[p]||'var(--ref)';
const f1=v=>v.toFixed(1),f2=v=>v.toFixed(2);
function axes(svg,o){const {W,H,L,R,T,B,x,y}=o;
 for(const t of o.yt){el('line',{x1:L,x2:W-R,y1:y(t),y2:y(t),class:'grid-line'},svg);txt(svg,L-6,y(t)+4,o.yf?o.yf(t):t,'tick','end');}
 for(const t of o.xt){txt(svg,x(t),H-B+16,o.xf?o.xf(t):t,'tick','middle');}
 if(o.xl)txt(svg,(L+W-R)/2,H-4,o.xl,'lab','middle');if(o.yl)txt(svg,4,T-8,o.yl,'lab');}
function path(pts,x,y){return pts.map((p,i)=>`${i?'L':'M'}${x(p[0]).toFixed(1)},${y(p[1]).toFixed(1)}`).join(' ');}
function smooth(a,n){const o=[];for(let i=0;i<a.length;i++){let s=0,c=0;for(let j=Math.max(0,i-n);j<=Math.min(a.length-1,i+n);j++){s+=a[j];c++;}o.push(s/c);}return o;}
const G=D.grid, I0=G.findIndex(v=>v>=0);

/* ---------- clusters: every run, temperature and power ---------- */
(function(){const shown=new Set(MAIN);const leg=document.getElementById('cl-leg');const TL=D.thermal.model_T_at_launch.mean;
 function stair(pts){const o=[];for(const q of pts){if(o.length&&o[o.length-1][1]!==q[1])o.push([q[0],o[o.length-1][1]]);o.push(q);}return o;}
 function draw(){leg.innerHTML=MAIN.map(p=>`<button type="button" aria-pressed="${shown.has(p)}" data-p="${p}"><i style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${col(p)};margin-right:6px"></i>${NAMES[p]}</button>`).join('');
  leg.querySelectorAll('button').forEach(b=>b.onclick=()=>{const p=b.dataset.p;shown.has(p)?shown.delete(p):shown.add(p);draw();});
  const tmax=Math.floor(Math.min(...D.runs.map(r=>r.dur))*10)/10;
  for(const [id,key,lo,hi,step] of [['cl-temp','curve_T',79.5,87,1],['cl-pow','curve_P',30,72,10]]){
   const W=900,H=key==='curve_T'?340:250,L=46,R=16,T=12,B=36;const {svg,tip,h}=host(id,W,H);
   const x=v=>L+(v+1)/(tmax+1.1)*(W-L-R),y=v=>H-B-(v-lo)/(hi-lo)*(H-B-T);
   const yt=[];for(let v=Math.ceil(lo/step)*step;v<=hi;v+=step)yt.push(v);
   axes(svg,{W,H,L,R,T,B,x,y,yt,xt:[0,1,2,3,4,5,6,7].filter(v=>v<=tmax+0.5),xl:'seconds since the kernel launched'});
   el('line',{x1:x(0),x2:x(0),y1:T,y2:H-B,stroke:'var(--axis)','stroke-dasharray':'3 3'},svg);
   for(const p of MAIN){if(!shown.has(p))continue;const rs=D.runs.filter(r=>r.values===p);
    for(const r of rs){let pts=G.map((g,i)=>[g,r[key][i]]).filter(q=>q[0]>=-1&&q[0]<=tmax);if(key==='curve_T')pts=stair(pts);
     const g=el('g',{},svg);el('path',{d:path(pts,x,y),fill:'none',stroke:col(p),'stroke-width':1.4,opacity:0.5},g);el('path',{d:path(pts,x,y),fill:'none',stroke:'transparent','stroke-width':9},g);
     hover(g,tip,h,()=>`<b>${NAMES[p]}</b>, block ${r.block+1}<br>${f2(r.p80)} W at the launch temperature · ${f2(r.tflops)} TFLOPS<br>rise ${r.rise_fit>=0?'+':''}${f2(r.rise_fit)} °C · heating power from the trace ${f1(r.a_thermal)} W, electrical ${f1(r.a_electrical)} W<br>${Math.round(r.approach_s||0)} s of heating and cooling before launch`);}
    let m;if(key==='curve_T'){const n=Math.min(...rs.map(r=>r.curve_fit.length));m=[[0,TL]];for(let i=0;i<n&&(i+1)*0.1<=tmax;i++)m.push([(i+1)*0.1,rs.reduce((a,r)=>a+r.curve_fit[i],0)/rs.length]);}
    else m=G.map((g,i)=>[g,D.patterns[p].mean_power[i]]).filter(q=>q[0]>=-1&&q[0]<=tmax);
    el('path',{d:path(m,x,y),fill:'none',stroke:col(p),'stroke-width':3,'stroke-linejoin':'round'},svg);}
  }}
 draw();})();

/* ---------- heating per FLOP ---------- */
(function(){const rows=ORDER;const W=900,rh=30,L=210,R=120,T=8,H=T+rows.length*rh+34;const {svg,tip,h}=host('perflop',W,H);
 const mx=Math.max(...rows.map(p=>D.patterns[p].mC_per_tflop_fit))*1.08;const x=v=>L+Math.max(0,v)/mx*(W-L-R);
 for(let t=0;t<=mx;t+=20){el('line',{x1:x(t),x2:x(t),y1:T,y2:H-30,class:'grid-line'},svg);txt(svg,x(t),H-12,t,'tick','middle');}
 txt(svg,W-R+8,H-12,'m°C per 10¹² FLOPs','lab');
 rows.forEach((p,i)=>{const v=D.patterns[p],yy=T+i*rh+4;const g=el('g',{},svg);txt(g,L-10,yy+15,NAMES[p]||p,'lab','end');
  el('rect',{x:x(0),y:yy,width:Math.max(1,x(v.mC_per_tflop_fit)-x(0)),height:20,rx:3,fill:col(p)},g);
  txt(g,x(v.mC_per_tflop_fit)+6,yy+15,`${v.mC_per_tflop_fit.toFixed(0)}  (${v.rise_fit>=0?'+':''}${f1(v.rise_fit)} °C)`,'lab-strong');
  hover(g,tip,h,()=>`<b>${NAMES[p]||p}</b><br>${f1(v.p80)} W at the start temperature · ${f2(v.tflops)} TFLOPS<br>rise after ${f1(v.dur)} s: ${f2(v.rise_fit)} °C (sd ${f2(v.rise_fit_sd)} over ${v.n} runs)<br>as read, whole degrees: ${f2(v.rise_end)} °C · onset ${f2(v.slope)} °C/s`);});})();
document.getElementById('tbl').innerHTML='<thead><tr><th>Operands (A and B)</th><th class="num">runs</th><th class="num">board W at 80 °C</th><th class="num">± sd</th><th class="num">TFLOPS</th><th class="num">rise in 7 s, °C</th><th class="num">as read</th><th class="num">onset, °C/s</th><th class="num">m°C per 10¹² FLOPs</th><th class="num">pJ per FLOP</th><th class="num">pJ per FLOP over idle</th></tr></thead><tbody>'+
 ORDER.map(p=>{const v=D.patterns[p];return `<tr><td>${NAMES[p]||p}</td><td class="num">${v.n}</td><td class="num"><b>${f1(v.p80)}</b></td><td class="num">${f2(v.p80_sd)}</td><td class="num">${f2(v.tflops)}</td><td class="num"><b>${v.rise_fit>=0?'+':''}${f2(v.rise_fit)}</b></td><td class="num">${v.rise_end>=0?'+':''}${f2(v.rise_end)}</td><td class="num">${f2(v.slope)}</td><td class="num">${v.mC_per_tflop_fit.toFixed(0)}</td><td class="num">${f2(v.pj_per_flop)}</td><td class="num">${f2(v.pj_per_flop_over_idle)}</td></tr>`;}).join('')+'</tbody>';

/* ---------- strip plot: every run's power, with the model's prediction ---------- */
(function(){const PM=D.power_model,prim=PM.models[PM.primary];const rows=ORDER;const W=900,rh=26,L=210,R=30,T=8,H=T+rows.length*rh+34;const {svg,tip,h}=host('strip',W,H);
 const x=v=>L+(v-34)/(70-34)*(W-L-R);for(let t=35;t<=70;t+=5){el('line',{x1:x(t),x2:x(t),y1:T,y2:H-30,class:'grid-line'},svg);txt(svg,x(t),H-12,t+' W','tick','middle');}
 rows.forEach((p,i)=>{const yy=T+i*rh+rh/2;txt(svg,L-10,yy+4,NAMES[p]||p,'lab','end');el('line',{x1:L,x2:W-R,y1:yy,y2:yy,class:'grid-line',opacity:0.5},svg);
  if(prim.loo[p]!==undefined){el('line',{x1:x(prim.loo[p]),x2:x(prim.loo[p]),y1:yy-9,y2:yy+9,stroke:'var(--ink)','stroke-width':2},svg);}
  D.runs.filter(r=>r.values===p).forEach((r,k)=>{const g=el('g',{},svg);el('circle',{cx:x(r.p80),cy:yy+((k%3)-1)*3,r:4.5,fill:col(p),opacity:0.8,stroke:'var(--surface)','stroke-width':1},g);
   hover(g,tip,h,()=>`<b>${NAMES[p]||p}</b>, block ${r.block+1}<br>${f2(r.p80)} W at the start temperature (${f2(r.p_early)} W as read in seconds 1–3)<br>model, not shown this pattern: ${prim.loo[p]!==undefined?f1(prim.loo[p])+' W':'n/a'}`);});});})();

/* ---------- activity table ---------- */
(function(){const PM=D.power_model,prim=PM.models[PM.primary];const M=v=>(v/1e6).toFixed(v>=1e7?1:v>=1e5?2:3);
 document.getElementById('act').innerHTML='<thead><tr><th>Operands</th><th class="num">valid lane-cycles</th><th class="num">register bits clocked, M</th><th class="num">net toggles, M</th><th class="num">in the multiplier tree</th><th class="num">operand-bus toggles, M</th><th class="num">measured W</th><th class="num">model W</th><th class="num">error</th></tr></thead><tbody>'+
 ORDER.filter(p=>D.toggles[p]).map(p=>{const t=D.toggles[p].mean,b=D.toggles[p].blocks;const mult=PM.rows.find(r=>r.values===p);const pr=prim.loo[p],me=D.patterns[p].p80;
  return `<tr><td>${NAMES[p]||p}</td><td class="num">${Math.round(t.lane_valid).toLocaleString()}</td><td class="num">${M(t.ff_clocked)}</td><td class="num">${M(t.nets)}</td><td class="num">${mult&&t.nets>0?Math.round(100*mult.mult/(mult.nets||1))+'%':'–'}</td><td class="num">${M(t.bus)}</td><td class="num">${f1(me)}</td><td class="num">${f1(pr)}</td><td class="num">${pr-me>=0?'+':''}${f1(pr-me)}</td></tr>`;}).join('')+'</tbody>';})();

/* ---------- predicted against measured power ---------- */
(function(){const PM=D.power_model,prim=PM.models[PM.primary];const W=440,H=400,L=50,R=16,T=16,B=40;const {svg,tip,h}=host('pm',W,H);
 const lo=35,hi=70,x=v=>L+(v-lo)/(hi-lo)*(W-L-R),y=v=>H-B-(v-lo)/(hi-lo)*(H-B-T);const tk=[35,40,45,50,55,60,65,70];
 axes(svg,{W,H,L,R,T,B,x,y,yt:tk,xt:tk,xl:'measured board power at 80 °C, W',yl:'predicted from RTL activity, W'});
 el('line',{x1:x(lo),y1:y(lo),x2:x(hi),y2:y(hi),stroke:'var(--axis)','stroke-dasharray':'4 4'},svg);
 const bef=D.before&&D.before.models[PM.primary]?D.before.models[PM.primary].pred:{};
 for(const p of ORDER){if(prim.loo[p]===undefined)continue;const me=D.patterns[p].p80;const g=el('g',{},svg);
  el('circle',{cx:x(me),cy:y(prim.loo[p]),r:6,fill:col(p),opacity:0.9,stroke:'var(--surface)','stroke-width':1.5},g);
  hover(g,tip,h,()=>`<b>${NAMES[p]||p}</b><br>measured ${f1(me)} W<br>model fitted without this pattern: ${f1(prim.loo[p])} W`);}
 })();

/* ---------- thermal model over the session ---------- */
(function(){const tr=D.thermal.trace.filter(p=>p.t>=180),W=900,H=300,L=46,R=16,T=12,B=34;const {svg}=host('thermal',W,H);const tmax=tr[tr.length-1].t;
 const lo=Math.floor(Math.min(...tr.map(p=>p.T)))-0.5,hi=Math.ceil(Math.max(...tr.map(p=>Math.max(p.T,p.fit))))+0.5;
 const x=t=>L+t/tmax*(W-L-R),y=v=>H-B-(v-lo)/(hi-lo)*(H-B-T);const yt=[];for(let v=Math.ceil(lo/2)*2;v<=hi;v+=2)yt.push(v);const xt=[];for(let m=0;m<=tmax/60;m+=10)xt.push(m*60);
 axes(svg,{W,H,L,R,T,B,x,y,yt,xt,xf:t=>(t/60)+' min'});
 el('path',{d:path(tr.map(p=>[p.t,p.T]),x,y),fill:'none',stroke:'var(--c1)','stroke-width':1.2,opacity:0.8},svg);
 el('path',{d:path(tr.map(p=>[p.t,p.fit]),x,y),fill:'none',stroke:'var(--c2)','stroke-width':1.2},svg);})();
document.getElementById('foster').innerHTML='<thead><tr><th>Time constant</th>'+D.thermal.taus.map(t=>`<th class="num">${t} s</th>`).join('')+'<th class="num">sum</th></tr></thead><tbody><tr><td>°C per W of board power</td>'+D.thermal.R.map(r=>`<td class="num">${r?r.toFixed(3):'–'}</td>`).join('')+`<td class="num"><b>${D.thermal.R_total.toFixed(2)}</b></td></tr></tbody>`;

/* ---------- the chain: predicted and measured rise ---------- */
(function(){const W=900,H=340,L=46,R=150,T=12,B=36;const {svg}=host('chain',W,H);const tmax=Math.floor(Math.min(...D.runs.map(r=>r.dur))*10)/10;
 const PATS=['zeros','ones','uniform','randn'].filter(p=>D.chain[p]);const TL=D.thermal.model_T_at_launch.mean;
 const hi=6,lo=-1;const x=v=>L+v/(tmax+0.2)*(W-L-R),y=v=>H-B-(v-lo)/(hi-lo)*(H-B-T);const yt=[];for(let v=lo;v<=hi;v++)yt.push(v);
 axes(svg,{W,H,L,R,T,B,x,y,yt,xt:[0,1,2,3,4,5,6,7].filter(v=>v<=tmax+0.2),xl:'seconds since the kernel launched'});
 const labs=[];for(const p of PATS){const c=D.chain[p],rs=D.runs.filter(r=>r.values===p);
  el('path',{d:path(G.map((g,i)=>[g,D.patterns[p].mean_rise[i]]).filter(q=>q[0]>=0&&q[0]<=tmax),x,y),fill:'none',stroke:col(p),'stroke-width':1.2,opacity:0.55},svg);
  const n=Math.min(...rs.map(r=>r.curve_fit.length));const m=[[0,0]];for(let i=0;i<n&&(i+1)*0.1<=tmax;i++)m.push([(i+1)*0.1,rs.reduce((a,r)=>a+r.curve_fit[i],0)/rs.length-TL]);
  el('path',{d:path(m,x,y),fill:'none',stroke:col(p),'stroke-width':2.8},svg);
  el('path',{d:path(c.curve_pred.map((v,i)=>[(i+1)*0.1,v]).filter(q=>q[0]<=tmax),x,y),fill:'none',stroke:'var(--ink)','stroke-width':1.8,'stroke-dasharray':'6 4'},svg);
  labs.push([y(m[m.length-1][1]),p]);}
 labs.sort((a,b)=>a[0]-b[0]);for(let i=1;i<labs.length;i++)if(labs[i][0]-labs[i-1][0]<15)labs[i][0]=labs[i-1][0]+15;
 for(const [yy,p] of labs){const t=txt(svg,x(tmax)+8,yy+4,NAMES[p],'lab');t.setAttribute('style','fill:'+col(p));}})();
(function(){const W=440,H=400,L=50,R=16,T=16,B=40;const {svg,tip,h}=host('chain-sc',W,H);const lo=-1,hi=7;
 const x=v=>L+(v-lo)/(hi-lo)*(W-L-R),y=v=>H-B-(v-lo)/(hi-lo)*(H-B-T);const tk=[0,1,2,3,4,5,6,7];
 axes(svg,{W,H,L,R,T,B,x,y,yt:tk,xt:tk,xl:'measured rise after 7 s, °C',yl:'predicted from RTL activity, °C'});
 el('line',{x1:x(lo),y1:y(lo),x2:x(hi),y2:y(hi),stroke:'var(--axis)','stroke-dasharray':'4 4'},svg);
 for(const p of ORDER){const c=D.chain[p];if(!c)continue;const g=el('g',{},svg);el('circle',{cx:x(c.rise_fit),cy:y(c.rise_pred),r:6,fill:col(p),opacity:0.9,stroke:'var(--surface)','stroke-width':1.5},g);
  hover(g,tip,h,()=>`<b>${NAMES[p]||p}</b><br>measured ${f2(c.rise_fit)} °C (whole-degree readings: ${f2(c.rise_meas)})<br>from RTL activity: ${f2(c.rise_pred)} °C<br>from measured power: ${f2(c.rise_thermal)} °C`);}})();

/* ---------- cool start: the clock governor ---------- */
(function(){const W=900,H=300,L=50,R=16,T=22,B=36;const {svg,tip,h}=host('cold',W,H);const x=v=>L+(v+0.5)/8.5*(W-L-R),y=v=>H-B-(v-550)/(850-550)*(H-B-T);
 axes(svg,{W,H,L,R,T,B,x,y,yt:[600,700,800],xt:[0,1,2,3,4,5,6,7],xl:'seconds since the kernel launched',yl:'minion clock, MHz, measured per 0.4 s launch (cycles counted ÷ wall time)',yf:v=>v});
 D.cold.forEach((r,k)=>{const pts=r.launches.map(l=>[l.t,l.ghz*1000]);const g=el('g',{},svg);
  el('path',{d:path(pts,x,y),fill:'none',stroke:col(r.values),'stroke-width':2.2,opacity:0.85,'stroke-linejoin':'round'},g);
  pts.forEach(q=>el('circle',{cx:x(q[0]),cy:y(q[1]),r:3,fill:col(r.values)},g));
  hover(g,tip,h,()=>`<b>${NAMES[r.values]}</b>, started at ${r.start_temp} °C<br>${f2(r.tflops)} TFLOPS over ${f1(r.dur)} s · ${f1(r.s_at_800)} s at 800 MHz<br>mean ${f1(r.p_mean)} W, peak ${f1(r.p_max)} W · reached ${r.end_temp} °C`);});})();
document.getElementById('coldtbl').innerHTML='<thead><tr><th>Operands</th><th class="num">start °C</th><th class="num">end °C</th><th class="num">seconds at 800 MHz</th><th class="num">TFLOPS</th><th class="num">mean W</th><th class="num">peak W</th></tr></thead><tbody>'+
 D.cold.map(r=>`<tr><td>${NAMES[r.values]}</td><td class="num">${r.start_temp}</td><td class="num">${r.end_temp}</td><td class="num">${f1(r.s_at_800)}</td><td class="num"><b>${f2(r.tflops)}</b></td><td class="num">${f1(r.p_mean)}</td><td class="num">${f1(r.p_max)}</td></tr>`).join('')+'</tbody>';

/* ---------- headline cards and the model's coefficients ---------- */
(function(){const P=D.patterns,PM=D.power_model,prim=PM.models[PM.primary];const sg=v=>(v>=0?'+':'')+v.toFixed(1);
 const cz=D.cold.filter(r=>r.values==='zeros'),cr=D.cold.filter(r=>r.values==='randn');const mean=a=>a.reduce((s,v)=>s+v,0)/a.length;
 const cards=[['Zeros',f1(P.zeros.p80)+' W',`${sg(P.zeros.rise_fit)} °C in 7 s · ${P.zeros.mC_per_tflop_fit.toFixed(0)} m°C per 10¹² FLOPs`],
  ['Ones',f1(P.ones.p80)+' W',`${sg(P.ones.rise_fit)} °C in 7 s · ${P.ones.mC_per_tflop_fit.toFixed(0)} m°C per 10¹² FLOPs`],
  ['Random normal',f1(P.randn.p80)+' W',`${sg(P.randn.rise_fit)} °C in 7 s · ${P.randn.mC_per_tflop_fit.toFixed(0)} m°C per 10¹² FLOPs`],
  ['RTL activity → power','±'+f1(prim.loo_rms)+' W',`leave-one-out error over ${Object.keys(prim.loo).length} patterns spanning ${f1(P.zeros.p80)}–${f1(P.randn.p80)} W`],
  ['From a cool die',`${f1(mean(cz.map(r=>r.tflops)))} vs ${f1(mean(cr.map(r=>r.tflops)))}`,'TFLOPS, zeros against random: the governor holds 800 MHz only for the cool pattern']];
 document.getElementById('kpis').innerHTML=cards.map(c=>`<div class="card kpi"><div class="lab">${c[0]}</div><div class="val">${c[1]}</div><div class="sub">${c[2]}</div></div>`).join('');
 const opsPerS=1024*600e6/546, WHAT={ffclk:'register bits clocked (enable high), including the clock network behind them',nets:'net toggles, whole unit',mult:'net toggles in the multiplier tree (Booth encoders, carry-save and 4:2 compressors)',rest:'net toggles in the rest of the unit (exponent path, alignment, adder, normalise, round, pipeline registers)',bus:'toggles of the operand words outside the unit (register-file reads, bypass, fan-out to 8 lanes)'};
 document.getElementById('coef').innerHTML='<thead><tr><th>Term</th><th class="num">W per million events per op</th><th class="num">energy per event</th><th>What it counts</th></tr></thead><tbody>'+
  `<tr><td>constant</td><td class="num">${f1(prim.coef[0])} W</td><td class="num">–</td><td>everything that does not depend on the operands: leakage at 80 °C, clocks, the tensor state machine, DDR, PCIe, regulators</td></tr>`+
  prim.names.map((n,i)=>`<tr><td>${({ffclk:'register bits clocked',nets:'net toggles',mult:'tree toggles',rest:'other toggles',bus:'operand-word toggles'})[n]}</td><td class="num">${prim.coef[i+1].toFixed(3)}</td><td class="num">${prim.coef[i+1]?(prim.coef[i+1]/1e6/opsPerS*1e15).toFixed(2)+' fJ':'–'}</td><td>${WHAT[n]}</td></tr>`).join('')+'</tbody>';})();

/* ---------- three ways to the heating power ---------- */
(function(){const rows=ORDER.filter(p=>D.chain[p]&&D.chain[p].a_thermal!==null);const W=900,rh=28,L=210,R=30,T=8,H=T+rows.length*rh+34;const {svg,tip,h}=host('three',W,H);
 const x=v=>L+(v+5)/(40)*(W-L-R);for(let t=-5;t<=35;t+=5){el('line',{x1:x(t),x2:x(t),y1:T,y2:H-30,class:'grid-line'},svg);txt(svg,x(t),H-12,(t>0?'+':'')+t+' W','tick','middle');}
 rows.forEach((p,i)=>{const c=D.chain[p],yy=T+i*rh+rh/2;const g=el('g',{},svg);txt(g,L-10,yy+4,NAMES[p]||p,'lab','end');el('line',{x1:L,x2:W-R,y1:yy,y2:yy,class:'grid-line',opacity:0.5},g);
  el('rect',{x:x(c.a_flips)-5,y:yy-5,width:10,height:10,fill:'var(--c7)',transform:`rotate(45 ${x(c.a_flips)} ${yy})`},g);
  el('circle',{cx:x(c.a_electrical),cy:yy,r:5.5,fill:'var(--c1)'},g);
  el('circle',{cx:x(c.a_thermal),cy:yy,r:7.5,fill:'none',stroke:'var(--c2)','stroke-width':2.2},g);
  el('rect',{x:L,y:yy-rh/2,width:W-L-R,height:rh,fill:'transparent'},g);
  hover(g,tip,h,()=>`<b>${NAMES[p]||p}</b>, W over the pre-launch level<br>from RTL activity: ${f1(c.a_flips)}<br>measured electrically: ${f1(c.a_electrical)}<br>inferred from the temperature trace: ${f1(c.a_thermal)} (sd ${f1(D.patterns[p].a_thermal_sd)} over ${D.patterns[p].n} runs)`);});})();

/* ---------- predictions written down before the new patterns were run ---------- */
(function(){if(!D.before)return;const ms=D.before.models,keys=Object.keys(ms);const pats=Object.keys(ms[keys[0]].pred).filter(p=>D.patterns[p]);
 const LAB={'ffclk+nets':'all toggles','ffclk+mult+rest':'tree + rest','ffclk+nets+bus':'all toggles + operand words','ffclk+mult+rest+bus':'tree + rest + operand words'};
 document.getElementById('pre').innerHTML='<thead><tr><th>Pattern</th>'+keys.map(k=>`<th class="num">${LAB[k]||k}</th>`).join('')+'<th class="num">measured</th></tr></thead><tbody>'+
  pats.map(p=>{const me=D.patterns[p].p_early;return `<tr><td>${NAMES[p]||p}</td>`+keys.map(k=>{const e=ms[k].pred[p]-me;return `<td class="num">${f1(ms[k].pred[p])} <span class="small">(${e>=0?'+':''}${f1(e)})</span></td>`;}).join('')+`<td class="num"><b>${f1(me)}</b></td></tr>`;}).join('')+
  '<tr><td><i>rms error</i></td>'+keys.map(k=>{const e=pats.map(p=>ms[k].pred[p]-D.patterns[p].p_early);return `<td class="num"><i>${f1(Math.sqrt(e.reduce((a,v)=>a+v*v,0)/e.length))} W</i></td>`;}).join('')+'<td></td></tr></tbody>';})();

/* ---------- where the model puts the watts ---------- */
(function(){const PM=D.power_model,prim=PM.models[PM.primary];const rows=ORDER.filter(p=>PM.rows.find(r=>r.values===p));
 const PART={ffclk:['clocking the pipeline registers','var(--c4)'],mult:['multiplier tree toggles','var(--c5)'],rest:['toggles in the rest of the unit','var(--bad)'],nets:['net toggles','var(--bad)'],bus:['operand words outside the unit','var(--c7)']};
 document.getElementById('stack-leg').innerHTML=prim.names.map(n=>`<span><i style="background:${PART[n][1]}"></i>${PART[n][0]}</span>`).join('')+'<span><i style="background:var(--ink);width:3px"></i>measured</span>';
 const base=prim.coef[0],W=900,rh=28,L=210,R=60,T=8,H=T+rows.length*rh+34;const {svg,tip,h}=host('stack',W,H);const x=v=>L+v/28*(W-L-R);
 for(let t=0;t<=25;t+=5){el('line',{x1:x(t),x2:x(t),y1:T,y2:H-30,class:'grid-line'},svg);txt(svg,x(t),H-12,'+'+t+' W','tick','middle');}
 rows.forEach((p,i)=>{const f=PM.rows.find(r=>r.values===p),yy=T+i*rh+4;const g=el('g',{},svg);txt(g,L-10,yy+15,NAMES[p]||p,'lab','end');let acc=0;const parts=[];
  prim.names.forEach((n,k)=>{const w=prim.coef[k+1]*f[n];parts.push([n,w]);if(w>0.02)el('rect',{x:x(acc),y:yy,width:Math.max(0.5,x(acc+w)-x(acc)-1),height:20,rx:2,fill:PART[n][1]},g);acc+=w;});
  const me=D.patterns[p].p80-base;el('line',{x1:x(me),x2:x(me),y1:yy-3,y2:yy+23,stroke:'var(--ink)','stroke-width':2.5},g);
  el('rect',{x:L,y:yy-4,width:W-L-R,height:rh,fill:'transparent'},g);
  hover(g,tip,h,()=>`<b>${NAMES[p]||p}</b>: ${f1(D.patterns[p].p80)} W measured, ${f1(base+acc)} W modelled<br>constant ${f1(base)} W`+parts.map(q=>`<br>${PART[q[0]][0]}: ${q[1].toFixed(1)} W`).join(''));});})();
