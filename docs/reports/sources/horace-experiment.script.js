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
 if(D.long&&D.model){const cap=v=>D.long.filter(r=>r.values===v&&r.per_shire===32&&r.reason==='cap').map(r=>r.dur);const rn=cap('randn'),on=cap('ones');
  cards.push(['Seconds from 80 to 90 °C',`${Math.min(...rn).toFixed(0)}–${Math.max(...rn).toFixed(0)} · ${Math.min(...on).toFixed(0)}–${Math.max(...on).toFixed(0)} · never`,'random normal · ones · zeros, in runs of up to ten minutes']);
  if(D.validation){const v=D.validation.timesplit.summary;cards.push(['Flips → temperature, held-out runs',`±${v.median_abs_pct.toFixed(0)}%`,`median error of the predicted time to 90 °C on ${v.capped} runs the model was not fitted to (worst ${v.worst_pct.toFixed(0)}%). At ten minutes it runs hot: ${v.uncapped_end_T_rms.toFixed(1)} °C rms`]);}
  else cards.push(['Flips → temperature',`±${D.model.per_run_summary.median_abs_pct.toFixed(0)}%`,`median error of the fitted time to 90 °C over ${D.model.per_run_summary.n_capped} long runs`]);}
 if(D.structured){const ks=Object.keys(D.structured.measured);const rms=Math.sqrt(ks.reduce((a,k)=>a+(D.structured.before.patterns[k].p_board_at_launch-D.structured.measured[k].p80)**2,0)/ks.length);
  cards.push(['Structured matrices, priced first',`±${f1(rms)} W`,`${ks.length} matrices from Hadamard to kaleidoscope, predicted from their tiles before they ran`]);}
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

/* ================= long runs and the flips-to-temperature model ================= */
const SNAME={hadamard:'Hadamard, ±1',kaleidoscope:'kaleidoscope (butterfly products)',relu:'weights × ReLU activations',negzero:'all −0.0',fft_cos:'DFT, cos and sin parts',block_diag:'random 4×4 blocks'};
if (D.long && D.model) (function(){
 const M=D.model,PW=M.power;const LCOL=r=>r.per_shire<32?(r.values==='randn'?'var(--c7)':'var(--c3)'):(COL[r.values]||'var(--ref)');
 const LNAME=r=>(NAMES[r.values]||r.values)+(r.per_shire<32?`, ${r.minions} of 1,024 cores`:'');
 const lx=v=>Math.log10(Math.max(v,1));
 /* every long run on a log time axis */
 (function(){const GROUPS=[['main','zeros, ones, random normal at full load',r=>r.per_shire===32&&['zeros','ones','randn'].includes(r.values)],['fewer','random normal on fewer cores',r=>r.per_shire<32&&r.values==='randn'],
   ['fewer1','ones and uniform on fewer cores',r=>r.per_shire<32&&r.values!=='randn'],['other','other patterns at full load',r=>r.per_shire===32&&!['zeros','ones','randn'].includes(r.values)]];
  const shown=new Set(['main','fewer']);const leg=document.getElementById('long-leg');
  function draw(){leg.innerHTML=GROUPS.map(g=>`<button type="button" aria-pressed="${shown.has(g[0])}" data-g="${g[0]}">${g[1]}</button>`).join('');
   leg.querySelectorAll('button').forEach(b=>b.onclick=()=>{const g=b.dataset.g;shown.has(g)?shown.delete(g):shown.add(g);draw();});
   const W=900,H=380,L=46,R=16,T=12,B=36;const {svg,tip,h}=host('long-curves',W,H);const x=v=>L+lx(v)/lx(600)*(W-L-R),y=v=>H-B-(Math.max(v,75.5)-75)/(91.5-75)*(H-B-T);
   axes(svg,{W,H,L,R,T,B,x,y,yt:[76,78,80,82,84,86,88,90],xt:[1,3,10,30,60,180,600],xf:v=>v<60?v+' s':(v/60)+' min',xl:'time since the kernel launched (log scale)'});
   el('line',{x1:L,x2:W-R,y1:y(90),y2:y(90),stroke:'var(--bad)','stroke-width':1.5,'stroke-dasharray':'5 4'},svg);txt(svg,W-R-4,y(90)-5,'90 °C: the run stops','lab','end');
   for(const r of D.long){if(!GROUPS.some(g=>shown.has(g[0])&&g[2](r)))continue;const pts=r.sec.map((s,i)=>[s,r.T[i]]).filter(q=>q[0]>=1&&q[0]<=r.dur&&q[1]!==null);if(pts.length<2)continue;const g=el('g',{},svg);
    const pr=M.per_run.find(q=>q.session.indexOf('long')>=0&&q.values===r.values&&q.active===r.minions&&Math.abs(q.dur-r.dur)<2);
    if(pr&&pr.curve_pred.length>1){const pp=pr.curve_pred.map((v,i)=>[2*i+1,Math.min(v,91)]).filter(q=>q[0]>=1);el('path',{d:path(pp,x,y),fill:'none',stroke:LCOL(r),'stroke-width':1.3,'stroke-dasharray':'4 3',opacity:0.75},g);}
    el('path',{d:path(pts,x,y),fill:'none',stroke:LCOL(r),'stroke-width':2.2,opacity:0.9},g);el('path',{d:path(pts,x,y),fill:'none',stroke:'transparent','stroke-width':10},g);
    const e=pts[pts.length-1];el('circle',{cx:x(e[0]),cy:y(e[1]),r:3.5,fill:LCOL(r)},g);
    hover(g,tip,h,()=>`<b>${LNAME(r)}</b><br>${r.reason==='cap'?'90 °C after '+r.dur.toFixed(0)+' s':'ran '+r.dur.toFixed(0)+' s, ended at '+(r.T_at['600']||r.t_max).toFixed(1)+' °C'}${pr&&pr.t_cap_pred?'; predicted from flips: '+pr.t_cap_pred.toFixed(0)+' s':''}<br>${f1(r.p_before)} W idle before, ${f1(r.p_mean)} W mean during · ${f2(r.tflops)} TFLOPS<br>${Math.round(r.approach_s)} s of heating and cooling before launch`);}}
  draw();})();
 /* table of long runs with the model's prediction */
 (function(){const pr=M.per_run.filter(p=>p.session.indexOf('long')>=0);
  document.getElementById('long-tbl').innerHTML='<thead><tr><th>Operands</th><th class="num">active cores</th><th class="num">switching power from flip counts, W</th><th class="num">ran, s</th><th>ended</th><th class="num">fitted model: 90 °C after, s</th><th class="num">end °C measured</th><th class="num">end °C, fitted model</th></tr></thead><tbody>'+
   D.long.map(r=>{const p=pr.reduce((b,q)=>Math.abs(q.dur-r.dur)<2&&q.values===r.values&&q.active===r.minions?q:b,null);
    return `<tr><td>${NAMES[r.values]||r.values}</td><td class="num">${r.minions.toLocaleString()}</td><td class="num">${p?f1(p.p_dyn_flips):'–'}</td><td class="num"><b>${r.dur.toFixed(0)}</b></td><td>${r.reason==='cap'?'at 90 °C':'time limit'}</td><td class="num">${p&&p.t_cap_pred?p.t_cap_pred.toFixed(0):(p?'never':'–')}</td><td class="num">${p?f1(p.T_end_meas):'–'}</td><td class="num">${p&&p.T_end_pred?f1(p.T_end_pred):'–'}</td></tr>`;}).join('')+'</tbody>';})();
 /* predicted against measured time to the cap: fitted runs (dots) and held-out runs (rings) */
 (function(){const pr=M.per_run.filter(p=>p.capped&&p.t_cap_pred);const W=440,H=400,L=54,R=16,T=16,B=40;const {svg,tip,h}=host('cap-sc',W,H);
  const lo=Math.log10(10),hi=Math.log10(700),x=v=>L+(Math.log10(v)-lo)/(hi-lo)*(W-L-R),y=v=>H-B-(Math.log10(v)-lo)/(hi-lo)*(H-B-T);const tk=[10,20,50,100,200,500];
  axes(svg,{W,H,L,R,T,B,x,y,yt:tk,xt:tk,xl:'measured seconds to 90 °C',yl:'predicted from flip counts, s'});el('line',{x1:x(10),y1:y(10),x2:x(700),y2:y(700),stroke:'var(--axis)','stroke-dasharray':'4 4'},svg);
  const colr=p=>p.active<1024?'var(--c7)':(COL[p.values]||'var(--ref)');
  for(const p of pr){const g=el('g',{},svg);el('circle',{cx:x(p.dur),cy:y(p.t_cap_pred),r:4.5,fill:colr(p),opacity:0.55},g);
   hover(g,tip,h,()=>`<b>${NAMES[p.values]||p.values}</b>, ${p.active} cores, fitted<br>flips: ${f1(p.p_dyn_flips)} W of switching<br>measured ${p.dur.toFixed(0)} s, model ${p.t_cap_pred.toFixed(0)} s`);}
  if(D.validation)for(const [set,lab] of [[D.validation.timesplit.rows,'held out in time'],[D.validation.afternoon.rows,'afternoon session, new matrices']])for(const p of set){if(!p.capped||!p.t_cap_pred)continue;const g=el('g',{},svg);
   el('circle',{cx:x(p.dur),cy:y(p.t_cap_pred),r:7,fill:'none',stroke:'var(--ink)','stroke-width':2},g);el('circle',{cx:x(p.dur),cy:y(p.t_cap_pred),r:9,fill:'transparent'},g);
   hover(g,tip,h,()=>`<b>${SNAME[p.values]||NAMES[p.values]||p.values}</b>, ${p.active} cores, ${lab}<br>flips: ${f1(p.p_flips)} W of switching<br>measured ${p.dur.toFixed(0)} s, predicted ${p.t_cap_pred.toFixed(0)} s`);}
 })();
 /* held-out runs: second half of the long session, model fitted on the first half */
 (function(){if(!D.validation)return;const rows=D.validation.timesplit.rows;
  document.getElementById('val-tbl').innerHTML='<thead><tr><th>Held-out run</th><th class="num">active cores</th><th class="num">switching power from flips, W</th><th class="num">measured</th><th class="num">predicted</th><th class="num">error</th></tr></thead><tbody>'+
   rows.map(r=>{const pc=r.capped&&r.t_cap_pred?(r.t_cap_pred/r.dur-1)*100:null;
    return `<tr><td>${NAMES[r.values]||r.values}</td><td class="num">${r.active.toLocaleString()}</td><td class="num">${f1(r.p_flips)}</td><td class="num">${r.capped?'90 °C after <b>'+r.dur.toFixed(0)+' s</b>':f1(r.T_end_meas)+' °C after '+r.dur.toFixed(0)+' s'}</td><td class="num">${r.capped?(r.t_cap_pred?r.t_cap_pred.toFixed(0)+' s':'never'):f1(r.T_end_pred)+' °C'+(r.t_cap_pred&&r.t_cap_pred<r.dur?' (90 °C at '+r.t_cap_pred.toFixed(0)+' s)':'')}</td><td class="num">${pc!==null?(pc>=0?'+':'')+pc.toFixed(0)+'%':(r.T_end_pred-r.T_end_meas>=0?'+':'')+f1(r.T_end_pred-r.T_end_meas)+' °C'}</td></tr>`;}).join('')+'</tbody>';})();
 /* leakage: idle power against temperature */
 (function(){const pts=PW.idle_curve.filter(p=>p.n>=30);const W=440,H=400,L=50,R=16,T=16,B=40;const {svg,tip,h}=host('leak',W,H);
  const x=v=>L+(v-60)/(92-60)*(W-L-R),y=v=>H-B-(v-20)/(46-20)*(H-B-T);
  axes(svg,{W,H,L,R,T,B,x,y,yt:[20,25,30,35,40,45],xt:[60,65,70,75,80,85,90],xl:'die temperature, °C',yl:'idle board power, W'});
  const curve=[];for(let t=60;t<=92;t+=0.5)curve.push([t,PW.P_fix+PW.A_leak_at_80*Math.exp((t-80)/PW.T_L)]);
  el('path',{d:path(curve,x,y),fill:'none',stroke:'var(--c2)','stroke-width':2},svg);
  el('line',{x1:L,x2:W-R,y1:y(PW.P_fix),y2:y(PW.P_fix),stroke:'var(--axis)','stroke-dasharray':'4 4'},svg);
  for(const p of pts){const g=el('g',{},svg);el('circle',{cx:x(p.T),cy:y(p.P),r:4.5,fill:'var(--c1)'},g);hover(g,tip,h,()=>`${p.T} °C: ${f2(p.P)} W idle (${p.n.toLocaleString()} samples)`);}})();
 /* step response, open loop and with leakage feedback */
 (function(){const W=440,H=400,L=50,R=16,T=16,B=40;const {svg}=host('step',W,H);const ks=Object.keys(M.step_open).map(Number).sort((a,b)=>a-b);
  const ymax=Math.min(4,Math.max(...ks.map(k=>M.step_closed[k]))*1.05);const x=v=>L+lx(v)/lx(3600)*(W-L-R),y=v=>H-B-Math.min(v,ymax)/ymax*(H-B-T);
  const yt=[];for(let v=0;v<=ymax;v+=0.5)yt.push(v);axes(svg,{W,H,L,R,T,B,x,y,yt,xt:[1,10,60,600,3600],xf:v=>v<60?v+' s':v<3600?(v/60)+' min':'1 h',xl:'time after one watt of switching is added',yl:'°C per W'});
  el('path',{d:path(ks.map(k=>[k,M.step_open[k]]),x,y),fill:'none',stroke:'var(--c1)','stroke-width':2.4},svg);
  el('path',{d:path(ks.filter(k=>M.step_closed[k]<=ymax).map(k=>[k,M.step_closed[k]]),x,y),fill:'none',stroke:'var(--bad)','stroke-width':2.4},svg);
  txt(svg,x(40),y(M.step_open[60])+18,'thermal network alone','lab');txt(svg,x(8),y(Math.min(ymax,M.step_closed[300]))-8,'with leakage feeding back (at 80 °C)','lab');})();
 /* the whole session: sensor against the closed loop from flips alone */
 (function(){const tr=M.trace.filter(p=>p.t>=180);const W=900,H=320,L=46,R=16,T=12,B=34;const {svg}=host('session',W,H);const t0=tr[0].t,tmax=tr[tr.length-1].t;
  const x=t=>L+(t-t0)/(tmax-t0)*(W-L-R),y=v=>H-B-(v-74)/(92-74)*(H-B-T);const xt=[];for(let m=Math.ceil(t0/1800)*1800;m<=tmax;m+=1800)xt.push(m);
  axes(svg,{W,H,L,R,T,B,x,y,yt:[76,80,84,88,92],xt,xf:t=>(t/3600).toFixed(1)+' h'});
  el('path',{d:path(tr.map(p=>[p.t,p.T]),x,y),fill:'none',stroke:'var(--c1)','stroke-width':1.1,opacity:0.85},svg);
  el('path',{d:path(tr.map(p=>[p.t,Math.min(p.fit,92)]),x,y),fill:'none',stroke:'var(--c2)','stroke-width':1.1},svg);})();
 /* temperature per flip */
 (function(){const opsPerS=1024*600e6/546;const LAB={ffclk:'register bit clocked',mult:'net toggle in the multiplier tree',rest:'net toggle elsewhere in the unit',bus:'operand-word bit toggled'};
  const row=D.power_model.rows.find(r=>r.values==='randn');let tw=0;
  const body=Object.keys(PW.e_fJ).map(k=>{const e=PW.e_fJ[k];const rate=row?row[k]*1e6*opsPerS/1e15:0;const w=e*rate;tw+=w;
    return `<tr><td>${LAB[k]}</td><td class="num">${e.toFixed(e<0.1?3:2)} fJ</td><td class="num">${rate.toFixed(rate<1?2:1)}</td><td class="num">${w.toFixed(1)} W</td><td class="num">${(w*M.step_closed[10]).toFixed(1)}</td><td class="num">${(w*M.step_closed[60]).toFixed(1)}</td></tr>`;}).join('');
  document.getElementById('perflip').innerHTML='<thead><tr><th>Kind of flip</th><th class="num">energy each</th><th class="num">a random fp32 matmul does, 10¹⁵ per second</th><th class="num">which is</th><th class="num">°C after 10 s</th><th class="num">°C after 1 min</th></tr></thead><tbody>'+body+
   `<tr><td><i>all four, plus ${f1(PW.p_sm_full_chip)} W for the tensor state machines</i></td><td></td><td></td><td class="num"><i>${(tw+PW.p_sm_full_chip).toFixed(1)} W</i></td><td class="num"><i>${((tw+PW.p_sm_full_chip)*M.step_closed[10]).toFixed(1)}</i></td><td class="num"><i>${((tw+PW.p_sm_full_chip)*M.step_closed[60]).toFixed(1)}</i></td></tr></tbody>`;})();
 /* equilibrium: die temperature the card can hold, against switching power */
 (function(){const W=900,H=320,L=46,R=20,T=12,B=36;const {svg}=host('budget',W,H);const Rt=M.R_total,Ta=M.T_amb;
  const pd=t=>(t-Ta)/Rt-PW.P_fix-PW.A_leak_at_80*Math.exp((t-80)/PW.T_L);let best=[-1e9,0];const pts=[];for(let t=50;t<=100;t+=0.25){const p=pd(t);pts.push([p,t]);if(p>best[0])best=[p,t];}
  const x=v=>L+(v+12)/(12+32)*(W-L-R),y=v=>H-B-(v-50)/(100-50)*(H-B-T);
  axes(svg,{W,H,L,R,T,B,x,y,yt:[50,60,70,80,90,100],xt:[-10,0,10,20,30],xf:v=>(v>0?'+':'')+v+' W',xl:'switching power held for hours (0 = an idle card)'});
  el('path',{d:path(pts.filter(q=>q[1]<=best[1]&&q[0]>=-12),x,y),fill:'none',stroke:'var(--c1)','stroke-width':2.6},svg);
  el('path',{d:path(pts.filter(q=>q[1]>=best[1]&&q[0]>=-12),x,y),fill:'none',stroke:'var(--bad)','stroke-width':2,'stroke-dasharray':'6 4'},svg);
  el('line',{x1:x(best[0]),x2:x(best[0]),y1:T,y2:H-B,stroke:'var(--axis)','stroke-dasharray':'3 3'},svg);txt(svg,x(best[0])+6,T+12,`no equilibrium beyond ${best[0]>=0?'+':''}${best[0].toFixed(1)} W`,'lab');
  for(const [p,lab] of [['zeros','zeros'],['ones','ones'],['randn','random normal']]){const pr=M.per_run.find(q=>q.values===p&&q.active===1024);if(!pr)continue;
   el('line',{x1:x(pr.p_dyn_flips),x2:x(pr.p_dyn_flips),y1:y(52),y2:y(98),stroke:COL[p],'stroke-width':2},svg);txt(svg,x(pr.p_dyn_flips)+4,y(54),lab,'lab');}
  txt(svg,x(-11),y(66),'solid: where the die settles','lab');txt(svg,x(-11),y(96),'dashed: above this, runaway','lab');})();
})();

/* ================= structured matrices: predicted before measuring ================= */
if (D.structured) (function(){
 const SN={hadamard:'Hadamard, ±1',hadamard_orth:'Hadamard, orthonormal',dct:'DCT-II',fft_cos:'DFT, cos and sin parts',butterfly:'butterfly factors',kaleidoscope:'kaleidoscope (butterfly products)',identity:'identity',permutation:'permutation',diagonal:'random diagonal',tridiagonal:'random tridiagonal',block_diag:'random 4×4 blocks',upper:'random upper-triangular',lowrank:'rank 1',circulant:'circulant',quant4:'4-bit quantised random',relu:'weights × ReLU activations',negzero:'all −0.0'};
 const rows=Object.keys(D.structured.measured).map(k=>({k,pred:D.structured.before.patterns[k].p_board_at_launch,meas:D.structured.measured[k].p80,sd:D.structured.measured[k].p80_sd,n:D.structured.measured[k].n,fl:D.structured.before.patterns[k].flips,rise:D.structured.measured[k].rise})).sort((a,b)=>a.meas-b.meas);
 const W=900,rh=28,L=250,R=30,T=8,H=T+rows.length*rh+34;const {svg,tip,h}=host('struct',W,H);const x=v=>L+(v-34)/(70-34)*(W-L-R);
 for(let t=35;t<=70;t+=5){el('line',{x1:x(t),x2:x(t),y1:T,y2:H-30,class:'grid-line'},svg);txt(svg,x(t),H-12,t+' W','tick','middle');}
 rows.forEach((r,i)=>{const yy=T+i*rh+rh/2;const g=el('g',{},svg);txt(g,L-10,yy+4,SN[r.k]||r.k,'lab','end');el('line',{x1:L,x2:W-R,y1:yy,y2:yy,class:'grid-line',opacity:0.5},g);
  el('line',{x1:x(r.pred),x2:x(r.pred),y1:yy-10,y2:yy+10,stroke:'var(--ink)','stroke-width':2.5},g);el('circle',{cx:x(r.meas),cy:yy,r:6,fill:'var(--c2)',opacity:0.9,stroke:'var(--surface)','stroke-width':1.5},g);
  el('rect',{x:L,y:yy-rh/2,width:W-L-R,height:rh,fill:'transparent'},g);
  hover(g,tip,h,()=>`<b>${SN[r.k]||r.k}</b><br>predicted ${f1(r.pred)} W, measured ${f1(r.meas)} W (${r.n} runs, sd ${f2(r.sd)})<br>${Math.round(r.fl.valid).toLocaleString()} of 4,096 multiply-adds valid · ${(r.fl.ffclk/1e6).toFixed(2)} M bits clocked · ${((r.fl.mult+r.fl.rest)/1e6).toFixed(1)} M net toggles per op`);});
 const e=rows.map(r=>r.pred-r.meas),rms=Math.sqrt(e.reduce((a,v)=>a+v*v,0)/e.length);
 document.getElementById('struct-tbl').innerHTML='<thead><tr><th>Matrix (A and B, 16×16 tiles)</th><th class="num">multiply-adds not gated</th><th class="num">register bits clocked, M</th><th class="num">net toggles, M</th><th class="num">predicted W</th><th class="num">measured W</th><th class="num">error</th><th class="num">rise in 7 s, °C</th></tr></thead><tbody>'+
  rows.map(r=>`<tr><td>${SN[r.k]||r.k}</td><td class="num">${Math.round(r.fl.valid).toLocaleString()}</td><td class="num">${(r.fl.ffclk/1e6).toFixed(2)}</td><td class="num">${((r.fl.mult+r.fl.rest)/1e6).toFixed(r.fl.mult+r.fl.rest>1e7?1:2)}</td><td class="num">${f1(r.pred)}</td><td class="num"><b>${f1(r.meas)}</b></td><td class="num">${r.pred-r.meas>=0?'+':''}${f1(r.pred-r.meas)}</td><td class="num">${r.rise>=0?'+':''}${f1(r.rise)}</td></tr>`).join('')+
  `<tr><td><i>rms error over ${rows.length} matrices</i></td><td></td><td></td><td></td><td></td><td></td><td class="num"><i>${f2(rms)} W</i></td><td></td></tr></tbody>`;
})();

/* ---------- structured matrices: long runs against the frozen model, nothing fitted on that session ---------- */
if (D.validation) (function(){const SN=Object.assign({randn:'random normal (reference)',ones:'ones (reference)'},SNAME);
 document.getElementById('struct-long').innerHTML='<thead><tr><th>Matrix</th><th class="num">switching power from its flips, W</th><th class="num">measured: 90 °C after, s</th><th class="num">predicted, s</th><th class="num">error</th></tr></thead><tbody>'+
  D.validation.afternoon.rows.map(r=>{const pc=r.capped&&r.t_cap_pred?(r.t_cap_pred/r.dur-1)*100:null;
   return `<tr><td>${SN[r.values]||r.values}</td><td class="num">${f1(r.p_flips)}</td><td class="num">${r.capped?'<b>'+r.dur.toFixed(0)+'</b>':'not in '+r.dur.toFixed(0)+' s: '+f1(r.T_end_meas)+' °C'}</td><td class="num">${r.capped?(r.t_cap_pred?r.t_cap_pred.toFixed(0):'never'):f1(r.T_end_pred)+' °C'}</td><td class="num">${pc!==null?(Math.abs(pc)<0.5?'0%':(pc>=0?'+':'')+pc.toFixed(0)+'%'):(r.T_end_pred-r.T_end_meas>=0?'+':'')+f1(r.T_end_pred-r.T_end_meas)+' °C'}</td></tr>`;}).join('')+'</tbody>';})();
