/* Every chart is drawn with the shared toolkit (global CK, docs/reports/sources/chartkit.js): the SVG is sized to its
   column (one unit is one CSS px, so text stays 12 px on a phone), tooltips show on hover, keyboard focus and tap, and
   the arrow keys step between marks. */
const NAMES={zeros:'zeros',ones:'ones',twos:'twos',pi:'π everywhere',onebit:'one set bit',checker:'checkerboard 1,0,1,0',ternary:'ternary −1, 0, 1',sparse75:'random normal, 75% zeroed',sparse50:'random normal, 50% zeroed',uniform:'random uniform [0,1)',randn:'random normal',signs:'random sign, ±1',pow2:'random exponent, 2^k',mant:'random mantissa, [1,2)',a_randn_b_ones:'A random, B ones',a_ones_b_randn:'A ones, B random'};
const COL={zeros:'var(--c1)',ones:'var(--c4)',pi:'var(--c3)',sparse50:'var(--c7)',uniform:'var(--c5)',randn:'var(--bad)'};
const MAIN=['zeros','ones','pi','sparse50','uniform','randn'].filter(p=>D.patterns[p]);
const ORDER=Object.keys(D.patterns).sort((a,b)=>D.patterns[a].p80-D.patterns[b].p80);
const col=p=>COL[p]||'var(--ref)';
const f1=v=>v.toFixed(1),f2=v=>v.toFixed(2);
const G=D.grid;
const sgn2=v=>(v>=0?'+':'')+CK.fmt.num(v,2);
/* the sample of a time-sorted trace nearest to time t */
function nearest(tr,t){let lo=0,hi=tr.length-1;while(hi-lo>1){const m=(lo+hi)>>1;if(tr[m].t<t)lo=m;else hi=m;}return t-tr[lo].t<=tr[hi].t-t?tr[lo]:tr[hi];}
/* pointer and keyboard readout for a time series in a CK frame: n vertical bands, each one tab stop (arrow keys step)
   showing the sample nearest its centre; a hairline and dots mark that sample while the band is active */
function bands(ff,x,t0,t1,n,T,B,html,dots,tr){const nodes=[];
 for(let i=0;i<n;i++){const a=t0+(t1-t0)*i/n,b=t0+(t1-t0)*(i+1)/n,p=nearest(tr,(a+b)/2),g=CK.el('g',{class:'band'},ff.svg);
  CK.el('rect',{x:x(a),y:T,width:Math.max(1,x(b)-x(a)),height:ff.H-B-T,class:'ck-hit'},g);
  CK.el('line',{x1:x(p.t),x2:x(p.t),y1:T,y2:ff.H-B,class:'xh',style:'stroke:var(--ink-2)','stroke-dasharray':'2 3'},g);
  for(const [cy,c] of dots(p))CK.el('circle',{cx:x(p.t),cy,r:3.5,class:'xh',style:'fill:'+c},g);
  CK.tip(ff,g,html(p));nodes.push(g);}
 CK.keynav(ff,nodes);}

/* ---------- clusters: every run, temperature and power ---------- */
(function(){const shown=new Set(MAIN),leg=document.getElementById('cl-leg'),TL=D.thermal.model_T_at_launch.mean,frames=[];
 function stair(pts){const o=[];for(const q of pts){if(o.length&&o[o.length-1][1]!==q[1])o.push([q[0],o[o.length-1][1]]);o.push(q);}return o;}
 const tmax=Math.floor(Math.min(...D.runs.map(r=>r.dur))*10)/10;
 /* the legend is built once, so a toggled button keeps keyboard focus */
 leg.innerHTML=MAIN.map(p=>`<button type="button" aria-pressed="true" data-p="${p}"><i style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${col(p)};margin-right:6px"></i>${NAMES[p]}</button>`).join('');
 leg.querySelectorAll('button').forEach(b=>b.addEventListener('click',()=>{const p=b.dataset.p;if(shown.has(p))shown.delete(p);else shown.add(p);b.setAttribute('aria-pressed',String(shown.has(p)));frames.forEach(f=>f.redraw());}));
 for(const [id,key,lo,hi,step] of [['cl-temp','curve_T',79.5,87,1],['cl-pow','curve_P',30,72,10]]){const isT=key==='curve_T';
  frames.push(CK.frame(id,{height:W=>isT?(W<600?300:358):(W<600?230:268),label:isT?'Die temperature of every run of the six main patterns':'Board power of every run of the six main patterns',draw:ff=>{
   const W=ff.W,H=ff.H,L=40,R=14,T=26,B=38,x=CK.lin(-1,tmax+0.1,L,W-R),y=CK.lin(lo,hi,H-B,T);
   const yt=[];for(let v=Math.ceil(lo/step)*step;v<=hi;v+=step)yt.push(v);
   CK.axes(ff,{x,y,L,R,T,B,yt,xt:[0,1,2,3,4,5,6,7].filter(v=>v<=tmax+0.5),xfmt:String,yfmt:String,xl:'seconds since the kernel launched',yl:isT?'die temperature, °C':'board power, W'});
   CK.el('line',{x1:x(0),x2:x(0),y1:T,y2:H-B,style:'stroke:var(--axis)','stroke-dasharray':'3 3'},ff.svg);
   const nodes=[];
   for(const p of MAIN){if(!shown.has(p))continue;const rs=D.runs.filter(r=>r.values===p);
    for(const r of rs){let pts=G.map((g,i)=>[g,r[key][i]]).filter(q=>q[0]>=-1&&q[0]<=tmax);if(isT)pts=stair(pts);
     const g=CK.el('g',{class:'run'},ff.svg),d=CK.path(pts,x,y);
     CK.el('path',{d,class:'vis',style:`fill:none;stroke:${col(p)}`,'stroke-width':1.4,opacity:0.5},g);CK.el('path',{d,style:'fill:none;stroke:transparent','stroke-width':9},g);
     CK.tip(ff,g,()=>`<b>${NAMES[p]}</b>, block ${r.block+1}<br>${f2(r.p80)} W at the launch temperature · ${f2(r.tflops)} TFLOPS<br>rise ${r.rise_fit>=0?'+':''}${f2(r.rise_fit)} °C · heating power from the trace ${f1(r.a_thermal)} W, electrical ${f1(r.a_electrical)} W<br>${Math.round(r.approach_s||0)} s of heating and cooling before launch`);nodes.push(g);}
    let m;if(isT){const n=Math.min(...rs.map(r=>r.curve_fit.length));m=[[0,TL]];for(let i=0;i<n&&(i+1)*0.1<=tmax;i++)m.push([(i+1)*0.1,rs.reduce((a,r)=>a+r.curve_fit[i],0)/rs.length]);}
    else m=G.map((g,i)=>[g,D.patterns[p].mean_power[i]]).filter(q=>q[0]>=-1&&q[0]<=tmax);
    CK.el('path',{d:CK.path(m,x,y),style:`fill:none;stroke:${col(p)}`,'stroke-width':3,'stroke-linejoin':'round'},ff.svg);}
   CK.keynav(ff,nodes);}}));}
})();

/* ---------- heating per FLOP ---------- */
/* The three coolest patterns move the whole-degree reading by at most one degree in a run (launched on a step down), so
   their rise is only bounded (below about 1 °C, section 4). They are shown as that bound, not as a fitted value, and
   labelled with what the thermal network driven by the measured power puts them at. */
const UNRES=new Set(['zeros','checker','sparse75']);
const bound=p=>Math.ceil(1e3/(D.patterns[p].tflops*D.patterns[p].dur));   /* m°C per 10¹² FLOPs for a 1 °C rise */
const netRise=p=>D.chain&&D.chain[p]&&D.chain[p].rise_thermal!=null?D.chain[p].rise_thermal:null;
(function(){const rows=ORDER;
 CK.frame('perflop',{height:W=>8+rows.length*(W<600?44:30)+(W<600?50:34),label:'Heating per FLOP for each operand pattern',draw:ff=>{
  /* wide: the row label sits in a left margin; narrow: above the bar */
  const nar=ff.narrow,W=ff.W,rh=nar?44:30,L=nar?8:210,R=nar?100:150,T=8,bh=nar?18:20,yAx=T+rows.length*rh;
  const mx=Math.max(...rows.map(p=>D.patterns[p].mC_per_tflop_fit))*1.08,x0=CK.lin(0,mx,L,W-R),x=v=>x0(Math.max(0,v));
  const g0=CK.el('g',{'aria-hidden':'true'},ff.svg);
  for(let t=0;t<=mx;t+=20){CK.el('line',{x1:x(t),x2:x(t),y1:T,y2:yAx+4,class:'grid-line'},g0);CK.txt(g0,x(t),yAx+22,t,'tick','middle');}
  if(nar)CK.txt(g0,W-2,yAx+42,'m°C per 10¹² FLOPs','lab','end');else CK.txt(g0,W-R+8,yAx+22,'m°C per 10¹² FLOPs','lab');
  const nodes=[];
  rows.forEach((p,i)=>{const v=D.patterns[p],y0=T+i*rh,by=nar?y0+20:y0+4,un=UNRES.has(p),g=CK.el('g',{},ff.svg);
   CK.el('rect',{x:0,y:y0,width:W,height:rh,class:'ck-hit'},g);
   CK.txt(g,nar?L:L-10,nar?y0+14:by+15,NAMES[p]||p,'lab',nar?'start':'end');
   if(un){CK.el('rect',{x:x(0),y:by+0.75,width:x(bound(p))-x(0),height:bh-1.5,rx:3,style:`fill:none;stroke:${col(p)}`,'stroke-width':1.5,'stroke-dasharray':'3 2'},g);
    CK.txt(g,x(bound(p))+6,by+bh-5,netRise(p)!=null?`not resolved (network: ${f1(netRise(p))} °C)`:'not resolved by the sensor','lab');}
   else{CK.el('rect',{x:x(0),y:by,width:Math.max(1,x(v.mC_per_tflop_fit)-x(0)),height:bh,rx:3,style:'fill:'+col(p)},g);
    CK.txt(g,x(v.mC_per_tflop_fit)+6,by+bh-5,`${v.mC_per_tflop_fit.toFixed(0)}  (${v.rise_fit>=0?'+':''}${f1(v.rise_fit)} °C)`,'lab-strong');}
   CK.tip(ff,g,()=>`<b>${NAMES[p]||p}</b><br>${f1(v.p80)} W at the start temperature · ${f2(v.tflops)} TFLOPS<br>`+(un?`the reading moved by at most one whole degree, so the rise is not resolved: below about 1 °C, under ${bound(p)} m°C per 10¹² FLOPs (de-quantised fit ${f2(v.rise_fit)} °C, sd ${f2(v.rise_fit_sd)} over ${v.n} runs${netRise(p)!=null?`; the thermal network driven by the measured power: ${f2(netRise(p))} °C`:''})`:`rise after ${f1(v.dur)} s: ${f2(v.rise_fit)} °C (sd ${f2(v.rise_fit_sd)} over ${v.n} runs)`)+`<br>as read, whole degrees: ${f2(v.rise_end)} °C · onset ${f2(v.slope)} °C/s`);nodes.push(g);});
  CK.keynav(ff,nodes);}});})();
document.getElementById('tbl').innerHTML='<thead><tr><th>Operands (A and B)</th><th class="num">runs</th><th class="num">board W at 80 °C</th><th class="num">± sd</th><th class="num">rise as read, °C (whole degrees)</th><th class="num">pJ per FLOP, run average</th><th class="num">pJ per FLOP over idle, run average</th></tr></thead><tbody>'+
 ORDER.map(p=>{const v=D.patterns[p];return `<tr><td>${NAMES[p]||p}</td><td class="num">${v.n}</td><td class="num"><b>${f1(v.p80)}</b></td><td class="num">${f2(v.p80_sd)}</td><td class="num">${v.rise_end>=0?'+':''}${f2(v.rise_end)}</td><td class="num">${f2(v.pj_per_flop)}</td><td class="num">${f2(v.pj_per_flop_over_idle)}</td></tr>`;}).join('')+'</tbody>';

/* ---------- strip plot: every run's power, with the model's prediction ---------- */
(function(){const PM=D.power_model,prim=PM.models[PM.primary];const rows=ORDER;
 CK.frame('strip',{height:W=>8+rows.length*(W<600?40:26)+34,label:'Board power of every run, with the activity model fitted without that pattern',draw:ff=>{
  const nar=ff.narrow,W=ff.W,rh=nar?40:26,L=nar?8:210,R=nar?14:30,T=8,yAx=T+rows.length*rh,x=CK.lin(34,70,L,W-R);
  const g0=CK.el('g',{'aria-hidden':'true'},ff.svg),tl=[];
  for(let t=35;t<=70;t+=5){CK.el('line',{x1:x(t),x2:x(t),y1:T,y2:yAx+4,class:'grid-line'},g0);if(!nar||t%10===0)tl.push(CK.txt(g0,x(t),yAx+22,t+' W','tick','middle'));}
  CK.inside(ff,tl);
  const nodes=[];
  rows.forEach((p,i)=>{const yy=nar?T+i*rh+27:T+i*rh+rh/2;CK.txt(ff.svg,nar?L:L-10,nar?yy-13:yy+4,NAMES[p]||p,'lab',nar?'start':'end');CK.el('line',{x1:L,x2:W-R,y1:yy,y2:yy,class:'grid-line',opacity:0.5},ff.svg);
   if(prim.loo[p]!==undefined){CK.el('line',{x1:x(prim.loo[p]),x2:x(prim.loo[p]),y1:yy-9,y2:yy+9,style:'stroke:var(--ink)','stroke-width':2},ff.svg);}
   D.runs.filter(r=>r.values===p).forEach((r,k)=>{const c=CK.el('circle',{cx:x(r.p80),cy:yy+((k%3)-1)*3,r:4.5,style:`fill:${col(p)};stroke:var(--surface)`,opacity:0.8,'stroke-width':1},ff.svg);
    CK.tip(ff,c,()=>`<b>${NAMES[p]||p}</b>, block ${r.block+1}<br>${f2(r.p80)} W at the start temperature (${f2(r.p_early)} W as read in seconds 1–3)<br>model, not shown this pattern: ${prim.loo[p]!==undefined?f1(prim.loo[p])+' W':'n/a'}`);nodes.push(c);});});
  CK.keynav(ff,nodes);}});})();

/* ---------- activity table ---------- */
(function(){const PM=D.power_model,prim=PM.models[PM.primary];const M=v=>(v/1e6).toFixed(v>=1e7?1:v>=1e5?2:3);
 document.getElementById('act').innerHTML='<thead><tr><th>Operands</th><th class="num">valid lane-cycles</th><th class="num">register bits clocked, M</th><th class="num">net toggles, M</th><th class="num">in the multiplier tree</th><th class="num">operand-bus toggles, M</th><th class="num">measured W</th><th class="num">predicted W (fit without it)</th><th class="num">error, W</th></tr></thead><tbody>'+
 ORDER.filter(p=>D.toggles[p]).map(p=>{const t=D.toggles[p].mean,b=D.toggles[p].blocks;const mult=PM.rows.find(r=>r.values===p);const pr=prim.loo[p],me=D.patterns[p].p80;
  return `<tr><td>${NAMES[p]||p}</td><td class="num">${Math.round(t.lane_valid).toLocaleString()}</td><td class="num">${M(t.ff_clocked)}</td><td class="num">${M(t.nets)}</td><td class="num">${mult&&t.nets>0?Math.round(100*mult.mult/(mult.nets||1))+'%':'–'}</td><td class="num">${M(t.bus)}</td><td class="num">${f1(me)}</td><td class="num">${f1(pr)}</td><td class="num">${pr-me>=0?'+':''}${f1(pr-me)}</td></tr>`;}).join('')+'</tbody>';})();

/* ---------- thermal model over the session ---------- */
(function(){const tr=D.thermal.trace.filter(p=>p.t>=180),tmax=tr[tr.length-1].t;
 const lo=Math.floor(Math.min(...tr.map(p=>p.T)))-0.5,hi=Math.ceil(Math.max(...tr.map(p=>Math.max(p.T,p.fit))))+0.5;
 CK.frame('thermal',{height:W=>W<600?260:318,label:'Die temperature over the strict session: sensor reading and the thermal network',draw:ff=>{
  const nar=ff.narrow,W=ff.W,H=ff.H,L=40,R=14,T=26,B=34,x=CK.lin(0,tmax,L,W-R),y=CK.lin(lo,hi,H-B,T);
  const yt=[];for(let v=Math.ceil(lo/2)*2;v<=hi;v+=2)yt.push(v);const xt=[];for(let m=0;m<=tmax/60;m+=nar?20:10)xt.push(m*60);
  CK.axes(ff,{x,y,L,R,T,B,yt,xt,xfmt:t=>(t/60)+' min',yfmt:String,yl:'die temperature, °C'});
  CK.el('path',{d:CK.path(tr.map(p=>[p.t,p.T]),x,y),style:'fill:none;stroke:var(--c1)','stroke-width':1.2,opacity:0.8},ff.svg);
  CK.el('path',{d:CK.path(tr.map(p=>[p.t,p.fit]),x,y),style:'fill:none;stroke:var(--c2)','stroke-width':1.2},ff.svg);
  bands(ff,x,tr[0].t,tmax,nar?20:40,T,B,p=>`<b>${f1(p.t/60)} min</b> into the session<br>sensor ${f1(p.T)} °C · thermal network ${f2(p.fit)} °C<br>measured board power ${f1(p.P)} W`,
   p=>[[y(p.T),'var(--c1)'],[y(p.fit),'var(--c2)']],tr);}});})();
document.getElementById('foster').innerHTML='<thead><tr><th>Time constant</th>'+D.thermal.taus.map(t=>`<th class="num">${t.toLocaleString('en-GB')} s</th>`).join('')+'<th class="num">sum</th></tr></thead><tbody><tr><td>°C per W of board power</td>'+D.thermal.R.map(r=>`<td class="num">${r?r.toFixed(3):'–'}</td>`).join('')+`<td class="num"><b>${D.thermal.R_total.toFixed(2)}</b></td></tr></tbody>`;

/* ---------- the chain: predicted and measured rise ---------- */
(function(){const tmax=Math.floor(Math.min(...D.runs.map(r=>r.dur))*10)/10;
 const PATS=['zeros','ones','uniform','randn'].filter(p=>D.chain[p]);const TL=D.thermal.model_T_at_launch.mean;
 const SHORT={uniform:'uniform',randn:'normal'};   /* end labels under 600 px; the tooltip carries the full name */
 /* per pattern, up to tmax: mean of the whole-degree readings, the recovered temperature (mean of the runs' fitted curves), the RTL prediction */
 const S=PATS.map(p=>{const c=D.chain[p],rs=D.runs.filter(r=>r.values===p);
  const thin=G.map((g,i)=>[g,D.patterns[p].mean_rise[i]]).filter(q=>q[0]>=0&&q[0]<=tmax);
  const n=Math.min(...rs.map(r=>r.curve_fit.length));const m=[[0,0]];for(let i=0;i<n&&(i+1)*0.1<=tmax;i++)m.push([(i+1)*0.1,rs.reduce((a,r)=>a+r.curve_fit[i],0)/rs.length-TL]);
  return {p,n:rs.length,thin,m,pred:c.curve_pred.map((v,i)=>[(i+1)*0.1,v]).filter(q=>q[0]<=tmax)};});
 const end=a=>a[a.length-1];
 CK.frame('chain',{height:W=>W<600?300:358,label:'Temperature rise during a run: readings, recovered temperature and the prediction from RTL activity',draw:ff=>{
  const nar=ff.narrow,W=ff.W,H=ff.H,L=40,R=nar?74:150,T=26,B=38;const x=CK.lin(0,tmax+0.2,L,W-R),y=CK.lin(-1,6,H-B,T);const yt=[];for(let v=-1;v<=6;v++)yt.push(v);
  CK.axes(ff,{x,y,L,R,T,B,yt,xt:[0,1,2,3,4,5,6,7].filter(v=>v<=tmax+0.2),xfmt:String,yfmt:v=>CK.fmt.num(v,0),xl:'seconds since the kernel launched',yl:'rise since launch, °C'});
  const labs=[],nodes=[];
  for(const s of S){const g=CK.el('g',{class:'run'},ff.svg),p=s.p;
   CK.el('path',{d:CK.path(s.thin,x,y),style:`fill:none;stroke:${col(p)}`,'stroke-width':1.2,opacity:0.55},g);
   CK.el('path',{d:CK.path(s.m,x,y),class:'vis',style:`fill:none;stroke:${col(p)}`,'stroke-width':2.8},g);
   CK.el('path',{d:CK.path(s.pred,x,y),style:'fill:none;stroke:var(--ink)','stroke-width':1.8,'stroke-dasharray':'6 4'},g);
   CK.el('path',{d:CK.path(s.m,x,y),style:'fill:none;stroke:transparent','stroke-width':10},g);
   CK.tip(ff,g,`<b>${NAMES[p]}</b>, mean of ${s.n} runs, ${f1(end(s.m)[0])} s after launch<br>recovered temperature ${sgn2(end(s.m)[1])} °C · whole-degree readings ${sgn2(end(s.thin)[1])} °C<br>predicted from RTL activity alone ${sgn2(end(s.pred)[1])} °C`);nodes.push(g);
   labs.push([y(end(s.m)[1]),p]);}
  labs.sort((a,b)=>a[0]-b[0]);for(let i=1;i<labs.length;i++)if(labs[i][0]-labs[i-1][0]<15)labs[i][0]=labs[i-1][0]+15;
  /* end labels in the text colour; the pattern's colour is kept in a short swatch of its line */
  const x0=x(tmax)+6;for(const [yy,p] of labs){CK.el('line',{x1:x0,x2:x0+12,y1:yy,y2:yy,style:`stroke:${col(p)}`,'stroke-width':2.8},ff.svg);CK.txt(ff.svg,x0+16,yy+4,nar&&SHORT[p]||NAMES[p],'lab');}
  CK.keynav(ff,nodes);}});})();
(function(){CK.frame('chain-sc',{maxW:460,height:W=>Math.round(W*0.93),label:'Temperature rise predicted from RTL activity against measured, one dot per pattern',draw:ff=>{
  const W=ff.W,H=ff.H,L=44,R=14,T=26,B=40,lo=-1,hi=7;const x=CK.lin(lo,hi,L,W-R),y=CK.lin(lo,hi,H-B,T),tk=[0,1,2,3,4,5,6,7];
  CK.axes(ff,{x,y,L,R,T,B,yt:tk,xt:tk,xfmt:String,yfmt:String,xl:'measured rise after 7 s, °C',yl:'predicted from RTL activity, °C'});
  CK.el('line',{x1:x(lo),y1:y(lo),x2:x(hi),y2:y(hi),style:'stroke:var(--axis)','stroke-dasharray':'4 4'},ff.svg);
  const nodes=[];
  for(const p of ORDER){const c=D.chain[p];if(!c)continue;const n=CK.el('circle',{cx:x(c.rise_fit),cy:y(c.rise_pred),r:6,style:`fill:${col(p)};stroke:var(--surface)`,opacity:0.9,'stroke-width':1.5},ff.svg);
   CK.tip(ff,n,()=>`<b>${NAMES[p]||p}</b><br>measured ${f2(c.rise_fit)} °C (whole-degree readings: ${f2(c.rise_meas)})<br>from RTL activity: ${f2(c.rise_pred)} °C<br>from measured power: ${f2(c.rise_thermal)} °C`);nodes.push(n);}
  nodes.sort((a,b)=>+a.getAttribute('cx')-+b.getAttribute('cx'));CK.keynav(ff,nodes);}});})();

/* ---------- cool start: the clock governor ---------- */
(function(){const lg=document.createElement('div');document.getElementById('cold').before(lg);
 CK.legend(lg,[...new Set(D.cold.map(r=>r.values))].map(p=>({key:p,label:NAMES[p]||p,mark:'line',color:col(p)})));
 const YL='minion clock, MHz, measured per 0.4 s launch (cycles counted ÷ wall time)';
 CK.frame('cold',{height:W=>W<600?270:300,label:'Minion clock during 7 s runs started from a cool die',draw:ff=>{
  const nar=ff.narrow,W=ff.W,H=ff.H,L=44,R=14,T=nar?40:26,B=38;const x=CK.lin(-0.5,8,L,W-R),y=CK.lin(550,850,H-B,T);
  CK.axes(ff,{x,y,L,R,T,B,yt:[600,700,800],xt:[0,1,2,3,4,5,6,7],xfmt:String,yfmt:String,xl:'seconds since the kernel launched',yl:nar?null:YL});
  if(nar){CK.txt(ff.svg,2,13,'minion clock, MHz, measured per 0.4 s launch','lab');CK.txt(ff.svg,2,28,'(cycles counted ÷ wall time)','lab');}   /* the axis title in two lines */
  const nodes=[];
  D.cold.forEach(r=>{const pts=r.launches.map(l=>[l.t,l.ghz*1000]),g=CK.el('g',{class:'run'},ff.svg),d=CK.path(pts,x,y);
   CK.el('path',{d,class:'vis',style:`fill:none;stroke:${col(r.values)}`,'stroke-width':2.2,opacity:0.85,'stroke-linejoin':'round'},g);
   pts.forEach(q=>CK.el('circle',{cx:x(q[0]),cy:y(q[1]),r:3,style:'fill:'+col(r.values)},g));
   CK.el('path',{d,style:'fill:none;stroke:transparent','stroke-width':9},g);
   CK.tip(ff,g,()=>`<b>${NAMES[r.values]}</b>, started at ${r.start_temp} °C<br>${f2(r.tflops)} TFLOPS over ${f1(r.dur)} s · ${f1(r.s_at_800)} s at 800 MHz<br>mean ${f1(r.p_mean)} W, peak ${f1(r.p_max)} W · reached ${r.end_temp} °C`);nodes.push(g);});
  CK.keynav(ff,nodes);}});})();
document.getElementById('coldtbl').innerHTML='<thead><tr><th>Operands</th><th class="num">start °C</th><th class="num">end °C</th><th class="num">seconds at 800 MHz</th><th class="num">TFLOPS</th><th class="num">mean W</th><th class="num">peak W</th></tr></thead><tbody>'+
 D.cold.map(r=>`<tr><td>${NAMES[r.values]}</td><td class="num">${r.start_temp}</td><td class="num">${r.end_temp}</td><td class="num">${f1(r.s_at_800)}</td><td class="num"><b>${f2(r.tflops)}</b></td><td class="num">${f1(r.p_mean)}</td><td class="num">${f1(r.p_max)}</td></tr>`).join('')+'</tbody>';

/* ---------- headline cards and the model's coefficients ---------- */
(function(){const P=D.patterns,PM=D.power_model,prim=PM.models[PM.primary];const sg=v=>(v>=0?'+':'')+v.toFixed(1);
 /* aifoundry3's board power for the same pattern (section 10): its idle under those runs plus its switching over idle */
 const CD=D.cards,a3=(v,long)=>{const q=CD&&CD.patterns.find(p=>p.values===v);if(!q)return '';const w=f1(CD.idle.aifoundry3+q.a3)+' W';
  return long?`aifoundry2 at ${CD.launch.aifoundry2.T.toFixed(0)} °C; aifoundry3 at ${CD.launch.aifoundry3.T.toFixed(0)} °C: ${w}`:`aifoundry3: ${w}`;};
 const cards=[['Zeros',f1(P.zeros.p80)+' W',`rise < 1 °C in 7 s, not resolved by the sensor · ${a3('zeros',true)}`],
  ['Ones',f1(P.ones.p80)+' W',`${sg(P.ones.rise_fit)} °C in 7 s · ${P.ones.mC_per_tflop_fit.toFixed(0)} m°C per 10¹² FLOPs · ${a3('ones')}`],
  ['Random normal',f1(P.randn.p80)+' W',`${sg(P.randn.rise_fit)} °C in 7 s · ${P.randn.mC_per_tflop_fit.toFixed(0)} m°C per 10¹² FLOPs · ${a3('randn')}`],
  ['RTL activity → power',f1(prim.loo_rms)+' W rms',`leave-one-out error over ${Object.keys(prim.loo).length} patterns spanning ${f1(P.zeros.p80)}–${f1(P.randn.p80)} W`]];
 if(D.long&&D.model){const cap=v=>D.long.filter(r=>r.values===v&&r.per_shire===32&&r.reason==='cap').map(r=>r.dur);const rn=cap('randn'),on=cap('ones');
  const zn=D.long.filter(r=>r.values==='zeros'&&r.per_shire===32).length,W3=['no','one','two','three','four','five','six'],nw=n=>W3[n]||String(n);
  cards.push(['Seconds from 80 to 90 °C',`${Math.min(...rn).toFixed(0)}–${Math.max(...rn).toFixed(0)} · ${Math.min(...on).toFixed(0)}–${Math.max(...on).toFixed(0)} · never`,`random normal (${nw(rn.length)} runs) · ones (${nw(on.length)}) · zeros (${nw(zn)}), in runs of up to ten minutes: aifoundry2, one session`]);
  if(D.validation){const v=D.validation.timesplit.summary;cards.push(['Flips → temperature, held-out runs',`${v.median_abs_pct.toFixed(0)}% median`,`aifoundry2, one session: median error of the predicted time to 90 °C on ${v.capped} runs the model was not fitted to (worst ${v.worst_pct.toFixed(0)}%). At ten minutes it runs hot: ${v.uncapped_end_T_rms.toFixed(1)} °C rms`]);}
  else cards.push(['Flips → temperature',`${D.model.per_run_summary.median_abs_pct.toFixed(0)}% median`,`median error of the fitted time to 90 °C over ${D.model.per_run_summary.n_capped} long runs`]);}
 if(D.structured){const ks=Object.keys(D.structured.measured);const rms=Math.sqrt(ks.reduce((a,k)=>a+(D.structured.before.patterns[k].p_board_at_launch-D.structured.measured[k].p80)**2,0)/ks.length);
  cards.push(['Structured matrices, priced first',`${f1(rms)} W rms`,`${ks.length} matrices from Hadamard to kaleidoscope, predicted from their tiles before they ran`]);}
 document.getElementById('kpis').innerHTML=cards.map(c=>`<div class="card kpi"><div class="lab">${c[0]}</div><div class="val">${c[1]}</div><div class="sub">${c[2]}</div></div>`).join('');
 const opsPerS=1024*600e6/546, WHAT={ffclk:'register bits clocked (enable high), including the clock network behind them',nets:'net toggles, whole unit',mult:'net toggles in the multiplier tree (Booth encoders, carry-save and 4:2 compressors)',rest:'net toggles in the rest of the unit (exponent path, alignment, adder, normalise, round, pipeline registers)',bus:'toggles of the operand words outside the unit (register-file reads, bypass, fan-out to 8 lanes)'};
 document.getElementById('coef').innerHTML='<thead><tr><th>Term</th><th class="num">W per million events per op</th><th class="num">energy per event</th><th>What it counts</th></tr></thead><tbody>'+
  `<tr><td>constant</td><td class="num">${f1(prim.coef[0])} W</td><td class="num">–</td><td>everything that does not depend on the operands: leakage at 80 °C, clocks, the tensor state machine, DDR, PCIe, regulators</td></tr>`+
  prim.names.map((n,i)=>`<tr><td>${({ffclk:'register bits clocked',nets:'net toggles',mult:'tree toggles',rest:'other toggles',bus:'operand-word toggles'})[n]}</td><td class="num">${prim.coef[i+1].toFixed(3)}</td><td class="num">${prim.coef[i+1]?(prim.coef[i+1]/1e6/opsPerS*1e15).toFixed(2)+' fJ':'–'}</td><td>${WHAT[n]}</td></tr>`).join('')+'</tbody>';})();

/* ---------- three ways to the heating power ---------- */
(function(){const rows=ORDER.filter(p=>D.chain[p]&&D.chain[p].a_thermal!==null);
 CK.frame('three',{height:W=>8+rows.length*(W<600?42:28)+34,label:'Heating power over the pre-launch level three ways, for each pattern',draw:ff=>{
  const nar=ff.narrow,W=ff.W,rh=nar?42:28,L=nar?8:210,R=nar?14:30,T=8,yAx=T+rows.length*rh,x=CK.lin(-5,35,L,W-R);
  const g0=CK.el('g',{'aria-hidden':'true'},ff.svg),tl=[];
  for(let t=-5;t<=35;t+=5){CK.el('line',{x1:x(t),x2:x(t),y1:T,y2:yAx+4,class:'grid-line'},g0);if(!nar||t%10===0)tl.push(CK.txt(g0,x(t),yAx+22,(t>0?'+':'')+CK.fmt.num(t,0)+' W','tick','middle'));}
  CK.inside(ff,tl);
  const nodes=[];
  rows.forEach((p,i)=>{const c=D.chain[p],y0=T+i*rh,yy=nar?y0+28:y0+rh/2,g=CK.el('g',{},ff.svg);
   CK.el('rect',{x:0,y:y0,width:W,height:rh,class:'ck-hit'},g);
   CK.txt(g,nar?L:L-10,nar?y0+13:yy+4,NAMES[p]||p,'lab',nar?'start':'end');CK.el('line',{x1:L,x2:W-R,y1:yy,y2:yy,class:'grid-line',opacity:0.5},g);
   CK.el('rect',{x:x(c.a_flips)-5,y:yy-5,width:10,height:10,style:'fill:var(--c7)',transform:`rotate(45 ${x(c.a_flips)} ${yy})`},g);
   CK.el('circle',{cx:x(c.a_electrical),cy:yy,r:5.5,style:'fill:var(--c1)'},g);
   CK.el('circle',{cx:x(c.a_thermal),cy:yy,r:7.5,style:'fill:none;stroke:var(--c2);stroke-width:2.2px'},g);   /* inline stroke: the ring keeps its colour when the row is active */
   CK.tip(ff,g,()=>`<b>${NAMES[p]||p}</b>, W over the pre-launch level<br>from RTL activity: ${f1(c.a_flips)}<br>measured electrically: ${f1(c.a_electrical)}<br>inferred from the temperature trace: ${f1(c.a_thermal)} (sd ${f1(D.patterns[p].a_thermal_sd)} over ${D.patterns[p].n} runs)`);nodes.push(g);});
  CK.keynav(ff,nodes);}});})();

/* ---------- predictions written down before the new patterns were run ---------- */
(function(){if(!D.before)return;const ms=D.before.models,keys=Object.keys(ms);const pats=Object.keys(ms[keys[0]].pred).filter(p=>D.patterns[p]);
 const LAB={'ffclk+nets':'all toggles','ffclk+mult+rest':'tree + rest','ffclk+nets+bus':'all toggles + operand words','ffclk+mult+rest+bus':'tree + rest + operand words'};
 document.getElementById('pre').innerHTML='<thead><tr><th>Pattern</th>'+keys.map(k=>`<th class="num">${LAB[k]||k}</th>`).join('')+'<th class="num">measured</th></tr></thead><tbody>'+
  pats.map(p=>{const me=D.patterns[p].p_early;return `<tr><td>${NAMES[p]||p}</td>`+keys.map(k=>{const e=ms[k].pred[p]-me;return `<td class="num">${f1(ms[k].pred[p])} <span class="small">(${e>=0?'+':''}${f1(e)})</span></td>`;}).join('')+`<td class="num"><b>${f1(me)}</b></td></tr>`;}).join('')+
  '<tr><td><i>rms error</i></td>'+keys.map(k=>{const e=pats.map(p=>ms[k].pred[p]-D.patterns[p].p_early);return `<td class="num"><i>${f1(Math.sqrt(e.reduce((a,v)=>a+v*v,0)/e.length))} W</i></td>`;}).join('')+'<td></td></tr></tbody>';})();

/* ---------- where the watts go, all 31 patterns: section 8's energies on every pattern's flip counts ---------- */
const KIND={hadamard:'Hadamard, ±1',hadamard_orth:'Hadamard, orthonormal',dct:'DCT-II',fft_cos:'DFT, cos and sin parts',butterfly:'butterfly factors',kaleidoscope:'kaleidoscope (butterfly products)',identity:'identity',permutation:'permutation',diagonal:'random diagonal',tridiagonal:'random tridiagonal',block_diag:'random 4×4 blocks',upper:'random upper-triangular',lowrank:'rank 1',circulant:'circulant',quant4:'4-bit quantised random',relu:'weights × ReLU activations',negzero:'all −0.0'};
/* the kinds of flip, in the colours of section 3's chart; state machines are the fixed per-op cost of a tensor op */
const FLIPS=[['sm','tensor state machines','var(--ref)'],['ffclk','register clocking','var(--c4)'],['mult','multiplier tree','var(--c5)'],['rest','rest of the unit','var(--bad)'],['bus','operand words','var(--c7)']];
const F_OP=600e6/546;   /* ops per second per minion at 600 MHz: 546 cycles per op for every pattern */
/* switching watts by kind for a workload's flips per op and minion (raw counts), on `act` minions: tools/ettelem/predict_heat.py predict() */
function flipWatts(fl,act){const PW=D.model.power,w={sm:PW.p_sm_full_chip*act/1024};for(const k of ['ffclk','mult','rest','bus'])w[k]=PW.e_fJ[k]*fl[k]*F_OP*act/1e15;return w;}
const sumW=w=>Object.values(w).reduce((a,v)=>a+v,0);
/* a strict-session pattern's flips per op and minion: power_model.rows holds them in millions (valid as a fraction of 4,096) */
const rowFlips=r=>({ffclk:r.ffclk*1e6,mult:r.mult*1e6,rest:r.rest*1e6,bus:r.bus*1e6,valid:r.valid*4096});
if (D.model && D.structured) (function(){const PW=D.model.power,TL=D.thermal.model_T_at_launch.mean;
 const idleAt=T=>PW.P_fix+PW.A_leak_at_80*Math.exp((T-80)/PW.T_L);
 const base=idleAt(TL);   /* the idle card at the launch temperature: measured switching = board W at launch − this */
 const all=[...D.power_model.rows.filter(r=>D.patterns[r.values]).map(r=>({k:r.values,set:'strict',name:NAMES[r.values]||r.values,
    fl:rowFlips(r),meas:D.patterns[r.values].p80})),
  ...Object.keys(D.structured.before.patterns).map(k=>({k,set:'struct',name:KIND[k]||k,fl:D.structured.before.patterns[k].flips,
    meas:D.structured.measured[k]?D.structured.measured[k].p80:null}))];
 all.forEach(r=>{r.w=flipWatts(r.fl,1024);r.model=sumW(r.w);r.msw=r.meas==null?null:r.meas-base;});
 all.sort((a,b)=>(a.msw==null)-(b.msw==null)||(a.msw==null?a.model-b.model:a.msw-b.msw));
 CK.legend('stack-leg',FLIPS.map(([k,l,c])=>({key:k,label:l,mark:'box',color:c})).concat([{key:'m',label:'measured',mark:'line',color:'var(--ink)'}]));
 let set='both',pins=['a_ones_b_randn','a_randn_b_ones'];
 const out=CK.readout('stack-out');
 const SETS={strict:'strict-session patterns (fitted)',struct:'structured matrices (priced before they ran)',both:'both'};
 CK.seg('stack-ctl',{label:'Show',options:Object.entries(SETS),value:set,onChange:v=>{set=v;fr.redraw();}});
 const M=v=>v>=1e6?CK.fmt.num(v/1e6,v>=1e7?1:2)+' M':v>=1e3?CK.fmt.num(v/1e3,0)+' k':CK.fmt.num(v,0);
 const fr=CK.frame('stack',{height:W=>{const n=all.filter(r=>set==='both'||r.set===set).length;return 14+n*(W<600?38:24)+44;},
  label:'Switching power by kind of flip for every pattern, with the measured value',draw:ff=>{
  const rows=all.filter(r=>set==='both'||r.set===set),nar=ff.narrow,W=ff.W,H=ff.H,rh=nar?38:24,L=nar?8:236,R=14,T=14;
  const mx=Math.max(...rows.map(r=>Math.max(r.model,r.msw||0)))*1.04,x=CK.lin(0,mx,L,W-R);
  const g0=CK.el('g',{'aria-hidden':'true'},ff.svg);
  for(const t of x.ticks(Math.max(3,Math.round((W-L-R)/80)))){CK.el('line',{x1:x(t),x2:x(t),y1:T-4,y2:H-40,class:'grid-line'},g0);CK.txt(g0,x(t),H-24,CK.fmt.num(t,0),'tick','middle');}
  CK.txt(g0,W-R,H-6,'switching power, W (over the idle card at launch)','lab','end');
  const nodes=[];
  rows.forEach((r,i)=>{const y0=T+i*rh,bh=nar?14:16,by=nar?y0+18:y0+(rh-bh)/2,g=CK.el('g',{},ff.svg),pin=pins.includes(r.k);
   CK.el('rect',{x:0,y:y0,width:W,height:rh,class:'ck-hit'},g);
   if(pin)CK.el('rect',{x:1,y:y0+1,width:W-2,height:rh-2,rx:4,style:'fill:none;stroke:var(--ink);stroke-width:1'},g);
   CK.txt(g,nar?L:L-8,nar?y0+13:by+bh-3,r.name+(r.set==='struct'&&r.meas==null?' (not run)':''),pin?'lab-strong':'lab',nar?'start':'end');
   let acc=0;for(const [k,,c] of FLIPS){const w=r.w[k];if(w>0.02)CK.el('rect',{x:x(acc),y:by,width:Math.max(0.5,x(acc+w)-x(acc)-1),height:bh,rx:2,style:'fill:'+c},g);acc+=w;}
   if(r.msw!=null)CK.el('line',{x1:x(r.msw),x2:x(r.msw),y1:by-4,y2:by+bh+4,style:'stroke:var(--ink)','stroke-width':2.5},g);
   CK.tip(ff,g,()=>`<b>${r.name}</b> · ${r.set==='strict'?'strict session: the energies were fitted with it':'structured: priced before it ran'}<br>`+
    `${r.meas!=null?`measured ${CK.fmt.num(r.msw,1)} W, `:''}modelled ${CK.fmt.num(r.model,1)} W: `+FLIPS.map(([k,l])=>`${l} ${CK.fmt.num(r.w[k],1)}`).join(', ')+
    `<br>per op and minion: ${M(r.fl.valid)} of 4,096 multiply-adds valid; ${M(r.fl.ffclk)} register bits clocked; ${M(r.fl.mult)} tree and ${M(r.fl.rest)} other toggles; ${M(r.fl.bus)} operand-word toggles<br>Enter or click: select for the comparison`);
   g.addEventListener('click',()=>toggle(r.k));nodes.push(g);});
  CK.keynav(ff,nodes,{onEnter:(n,k)=>toggle(rows[k].k)});}});
 function toggle(k){pins=pins.includes(k)?pins.filter(q=>q!==k):pins.concat([k]).slice(-2);fr.redraw();explain();}
 function explain(){if(pins.length<2){out.set(pins.length?`Selected: ${all.find(r=>r.k===pins[0]).name}. Select a second row to compare.`:'Select two rows to compare them kind by kind.');return;}
  const [a,b]=pins.map(k=>all.find(r=>r.k===k)).sort((p,q)=>(q.meas??q.model)-(p.meas??p.model));
  const sg=v=>(v>=0?'+':'')+CK.fmt.num(v,1);
  const parts=FLIPS.filter(([k])=>Math.abs(a.w[k]-b.w[k])>=0.05).map(([k,l,c])=>`<span style="white-space:nowrap"><i style="display:inline-block;width:10px;height:10px;border-radius:2px;background:${c};margin-right:4px"></i>${l} ${sg(a.w[k]-b.w[k])}</span>`);
  out.set(`<b>${a.name} − ${b.name}:</b> `+(a.meas!=null&&b.meas!=null?`${sg(a.meas-b.meas)} W measured, `:'')+`${sg(a.model-b.model)} W modelled (${parts.join(', ')||'no kind moves by 0.05 W'} W)`);}
 explain();
})();

/* ================= long runs and the flips-to-temperature model ================= */
const SNAME={hadamard:'Hadamard, ±1',kaleidoscope:'kaleidoscope (butterfly products)',relu:'weights × ReLU activations',negzero:'all −0.0',fft_cos:'DFT, cos and sin parts',block_diag:'random 4×4 blocks'};
if (D.long && D.model) (function(){
 const M=D.model,PW=M.power;
 /* colours on the long-run charts: the three main patterns at full load keep their section 1 colours; random normal on
    fewer minions is purple, ones and uniform on fewer minions green, every other pattern at full load grey */
 const MAINL=['zeros','ones','randn'],LC=(v,act)=>act<1024?(v==='randn'?'var(--c7)':'var(--c3)'):(MAINL.includes(v)?COL[v]:'var(--ref)');
 const LCOL=r=>LC(r.values,r.minions);
 const LNAME=r=>(NAMES[r.values]||r.values)+(r.per_shire<32?`, ${r.minions} of 1,024 minions`:'');
 const REC=r=>M.per_run.find(q=>q.session.indexOf('long')>=0&&q.run===r.run);   /* the model record of long run r, if it was in the fit */
 /* switching power from the flip counts: the power line of section 8 without its fixed part and leakage (same formula as the per-flip table) */
 const PDYN=(v,act)=>{const row=D.power_model.rows.find(q=>q.values===v);if(!row)return null;return PW.p_sm_full_chip*act/1024+Object.keys(PW.e_fJ).reduce((a,k)=>a+PW.e_fJ[k]*row[k]*1e6*(600e6/546)*act/1e15,0);};
 /* every long run on a log time axis */
 (function(){const GROUPS=[['main','zeros, ones, random normal at full load',r=>r.per_shire===32&&MAINL.includes(r.values),MAINL.map(v=>COL[v])],['fewer','random normal on fewer minions',r=>r.per_shire<32&&r.values==='randn',['var(--c7)']],
   ['fewer1','ones and uniform on fewer minions',r=>r.per_shire<32&&r.values!=='randn',['var(--c3)']],['other','other patterns at full load',r=>r.per_shire===32&&!MAINL.includes(r.values),['var(--ref)']]];
  const sw=c=>`<i style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${c};margin-right:3px"></i>`;
  const shown=new Set(['main','fewer']);const leg=document.getElementById('long-leg');
  /* the legend is built once, so a toggled button keeps keyboard focus */
  leg.innerHTML=GROUPS.map(g=>`<button type="button" aria-pressed="${shown.has(g[0])}" data-g="${g[0]}">${g[3].map(sw).join('')}<span style="margin-left:3px">${g[1]}</span></button>`).join('');
  leg.querySelectorAll('button').forEach(b=>b.addEventListener('click',()=>{const g=b.dataset.g;if(shown.has(g))shown.delete(g);else shown.add(g);b.setAttribute('aria-pressed',String(shown.has(g)));fr.redraw();}));
  const fr=CK.frame('long-curves',{height:W=>W<600?340:398,label:'Die temperature of the long runs against time since launch, log scale',draw:ff=>{
   const nar=ff.narrow,W=ff.W,H=ff.H,L=40,R=nar?16:34,T=26,B=38;const x=CK.log(1,600,L,W-R),y0=CK.lin(75,91.5,H-B,T),y=v=>y0(Math.max(v,75.5));
   CK.axes(ff,{x,y:y0,L,R,T,B,yt:[76,78,80,82,84,86,88,90],xt:nar?[1,10,60,600]:[1,3,10,30,60,180,600],xfmt:v=>v<60?v+' s':(v/60)+' min',yfmt:String,xl:'time since the kernel launched (log scale)',yl:'die temperature, °C'});
   CK.el('line',{x1:L,x2:W-R,y1:y(90),y2:y(90),style:'stroke:var(--bad)','stroke-width':1.5,'stroke-dasharray':'5 4'},ff.svg);CK.txt(ff.svg,W-R-4,y(90)-5,'90 °C: the run stops','lab halo','end');   /* the halo keeps it legible where a dashed curve crosses */
   const nodes=[];
   for(const r of D.long){if(!GROUPS.some(g=>shown.has(g[0])&&g[2](r)))continue;const pts=r.sec.map((s,i)=>[s,r.T[i]]).filter(q=>q[0]>=1&&q[0]<=r.dur&&q[1]!==null);if(pts.length<2)continue;const g=CK.el('g',{class:'run'},ff.svg);
    const pr=REC(r),d=CK.path(pts,x,y);
    if(pr&&pr.curve_pred.length>1){const pp=pr.curve_pred.map((v,i)=>[2*i+1,Math.min(v,91)]).filter(q=>q[0]>=1);CK.el('path',{d:CK.path(pp,x,y),style:`fill:none;stroke:${LCOL(r)}`,'stroke-width':1.3,'stroke-dasharray':'4 3',opacity:0.75},g);}
    CK.el('path',{d,class:'vis',style:`fill:none;stroke:${LCOL(r)}`,'stroke-width':2.2,opacity:0.9},g);CK.el('path',{d,style:'fill:none;stroke:transparent','stroke-width':10},g);
    const e=pts[pts.length-1];CK.el('circle',{cx:x(e[0]),cy:y(e[1]),r:3.5,style:'fill:'+LCOL(r)},g);
    CK.tip(ff,g,()=>`<b>${LNAME(r)}</b><br>${r.reason==='cap'?'90 °C after '+r.dur.toFixed(0)+' s':'ran '+r.dur.toFixed(0)+' s, ended at '+(r.T_at['600']||r.t_max).toFixed(1)+' °C'}${pr?(pr.t_cap_pred?'; fitted model: 90 °C after '+pr.t_cap_pred.toFixed(0)+' s':''):'; not in the model fit'}<br>${f1(r.p_before)} W idle before, ${f1(r.p_mean)} W mean during · ${f2(r.tflops)} TFLOPS<br>${Math.round(r.approach_s)} s of heating and cooling before launch`);nodes.push([x(e[0]),g]);}
   CK.keynav(ff,nodes.sort((a,b)=>a[0]-b[0]).map(q=>q[1]));}});   /* arrow keys go from the first run to end to the last */
 })();
 /* table of long runs with the model's prediction */
 (function(){const pr=M.per_run.filter(p=>p.session.indexOf('long')>=0);
  document.getElementById('long-tbl').innerHTML='<thead><tr><th>Operands</th><th class="num">active minions</th><th class="num">switching power from flip counts, W</th><th class="num">ran, s</th><th>ended</th><th class="num">fitted model: 90 °C after, s</th><th class="num">end °C measured</th><th class="num">end °C, fitted model</th></tr></thead><tbody>'+
   D.long.map(r=>{const p=pr.find(q=>q.run===r.run),cap=r.reason==='cap',tend=cap?r.t_max:(r.T_at['600']!==undefined&&r.T_at['600']!==null?r.T_at['600']:r.t_max);
    const nf='<td class="num small">not in the fit</td>';
    return `<tr><td>${NAMES[r.values]||r.values}</td><td class="num">${r.minions.toLocaleString()}</td><td class="num">${PDYN(r.values,r.minions)!==null?f1(PDYN(r.values,r.minions)):'–'}</td><td class="num"><b>${r.dur.toFixed(0)}</b></td><td>${cap?'at 90 °C':'time limit'}</td>`+(p?`<td class="num">${p.t_cap_pred?p.t_cap_pred.toFixed(0):'never'}</td>`:nf)+`<td class="num">${cap?'90':f1(tend)}</td>`+(p?`<td class="num">${p.T_end_pred?f1(p.T_end_pred):'–'}</td>`:nf)+'</tr>';}).join('')+'</tbody>';})();
 /* predicted against measured time to the cap: fitted runs (dots, coloured by group as in section 7) and held-out runs (rings) */
 (function(){const pr=M.per_run.filter(p=>p.capped&&p.t_cap_pred);const colr=p=>LC(p.values,p.active);
  const GRP=[['ones at full load',p=>p.active===1024&&p.values==='ones'],['random normal at full load',p=>p.active===1024&&p.values==='randn'],
   ['zeros at full load',p=>p.active===1024&&p.values==='zeros'],['random normal on fewer minions',p=>p.active<1024&&p.values==='randn'],
   ['ones and uniform on fewer minions',p=>p.active<1024&&p.values!=='randn'],['other patterns at full load',p=>p.active===1024&&!MAINL.includes(p.values)]];
  CK.legend('cap-leg',GRP.map(([l,t])=>{const q=pr.find(t);return q?{key:l,label:l,mark:'dot',color:colr(q)}:null;}).filter(Boolean).concat([{key:'held',label:'held out',mark:'ring',color:'var(--ink)'}]));
  CK.frame('cap-sc',{maxW:560,height:W=>Math.round(Math.min(W,560)*0.86),label:'Seconds to 90 °C predicted from flip counts against measured, run by run',draw:ff=>{
   const W=ff.W,H=ff.H,L=54,R=14,T=26,B=40,x=CK.log(10,700,L,W-R),y=CK.log(10,700,H-B,T),tk=[10,20,50,100,200,500];
   CK.axes(ff,{x,y,xt:tk,yt:tk,L,R,T,B,xl:'measured seconds to 90 °C',yl:'predicted from flip counts, s'});
   CK.el('line',{x1:x(10),y1:y(10),x2:x(700),y2:y(700),style:'stroke:var(--axis)','stroke-dasharray':'4 4'},ff.svg);
   const fit=[],held=[];
   for(const p of pr){const c=CK.el('circle',{cx:x(p.dur),cy:y(p.t_cap_pred),r:5,style:`fill:${colr(p)};fill-opacity:0.75;stroke:var(--surface)`,'stroke-width':1.5},ff.svg);
    CK.tip(ff,c,`<b>${NAMES[p.values]||p.values}</b>, ${p.active.toLocaleString('en-GB')} minions, in the fit<br>flips: ${f1(p.p_dyn_flips)} W of switching<br>measured ${p.dur.toFixed(0)} s, model ${p.t_cap_pred.toFixed(0)} s`);fit.push(c);}
   if(D.validation)for(const [set,lab] of [[D.validation.timesplit.rows,'held out in time'],[D.validation.afternoon.rows,'afternoon session, new matrices']])for(const p of set){if(!p.capped||!p.t_cap_pred)continue;
    const c=CK.el('circle',{cx:x(p.dur),cy:y(p.t_cap_pred),r:7,style:'fill:none;stroke:var(--ink)','stroke-width':2,'pointer-events':'all'},ff.svg);
    CK.tip(ff,c,`<b>${SNAME[p.values]||NAMES[p.values]||p.values}</b>, ${p.active.toLocaleString('en-GB')} minions, ${lab}<br>flips: ${f1(p.p_flips)} W of switching<br>measured ${p.dur.toFixed(0)} s, predicted ${p.t_cap_pred.toFixed(0)} s`);held.push(c);}
   const byX=a=>a.sort((u,v)=>+u.getAttribute('cx')-+v.getAttribute('cx'));CK.keynav(ff,byX(fit));CK.keynav(ff,byX(held));}});
 })();
 /* held-out runs: second half of the long session, model fitted on the first half */
 (function(){if(!D.validation)return;const rows=D.validation.timesplit.rows;
  document.getElementById('val-tbl').innerHTML='<thead><tr><th>Held-out run</th><th class="num">active minions</th><th class="num">switching power from flips, W</th><th class="num">measured</th><th class="num">predicted</th><th class="num">error</th></tr></thead><tbody>'+
   rows.map(r=>{const pc=r.capped&&r.t_cap_pred?(r.t_cap_pred/r.dur-1)*100:null;
    return `<tr><td>${NAMES[r.values]||r.values}</td><td class="num">${r.active.toLocaleString()}</td><td class="num">${f1(r.p_flips)}</td><td class="num">${r.capped?'90 °C after <b>'+r.dur.toFixed(0)+' s</b>':f1(r.T_end_meas)+' °C after '+r.dur.toFixed(0)+' s'}</td><td class="num">${r.capped?(r.t_cap_pred?r.t_cap_pred.toFixed(0)+' s':'never'):f1(r.T_end_pred)+' °C'+(r.t_cap_pred&&r.t_cap_pred<r.dur?' (90 °C at '+r.t_cap_pred.toFixed(0)+' s)':'')}</td><td class="num">${pc!==null?(pc>=0?'+':'')+pc.toFixed(0)+'%':(r.T_end_pred-r.T_end_meas>=0?'+':'')+f1(r.T_end_pred-r.T_end_meas)+' °C'}</td></tr>`;}).join('')+'</tbody>';})();
 /* leakage: idle power against temperature */
 (function(){const pts=PW.idle_curve.filter(p=>p.n>=30);
  CK.frame('leak',{maxW:460,height:W=>Math.round(W*0.93),label:'Idle board power against die temperature, with the fitted exponential',draw:ff=>{
   const W=ff.W,H=ff.H,L=44,R=14,T=26,B=40;const x=CK.lin(60,92,L,W-R),y=CK.lin(20,46,H-B,T);
   CK.axes(ff,{x,y,L,R,T,B,yt:[20,25,30,35,40,45],xt:[60,65,70,75,80,85,90],xfmt:String,yfmt:String,xl:'die temperature, °C',yl:'idle board power, W'});
   const curve=[];for(let t=60;t<=92;t+=0.5)curve.push([t,PW.P_fix+PW.A_leak_at_80*Math.exp((t-80)/PW.T_L)]);
   CK.el('path',{d:CK.path(curve,x,y),style:'fill:none;stroke:var(--c2)','stroke-width':2},ff.svg);
   /* the fixed part (P_fix, 12.6 W) lies below this axis, so it is not drawn */
   const nodes=pts.map(p=>{const c=CK.el('circle',{cx:x(p.T),cy:y(p.P),r:4.5,style:'fill:var(--c1)'},ff.svg);CK.tip(ff,c,`${p.T} °C: ${f2(p.P)} W idle (${p.n.toLocaleString('en-GB')} samples)`);return c;});
   CK.keynav(ff,nodes);}});})();
 /* step response, open loop and with leakage feedback */
 (function(){const ks=Object.keys(M.step_open).map(Number).sort((a,b)=>a-b);const ymax=Math.min(4,Math.max(...ks.map(k=>M.step_closed[k]))*1.05);
  const tf=v=>v<60?v+' s':v<3600?(v/60)+' min':(v/3600)+' h';
  CK.frame('step',{maxW:460,height:W=>Math.round(W*0.93),label:'Degrees per watt after a step of switching power, with and without leakage feeding back',draw:ff=>{
   const W=ff.W,H=ff.H,L=44,R=14,T=26,B=40;const x=CK.log(1,3600,L,W-R),y0=CK.lin(0,ymax,H-B,T),y=v=>y0(Math.min(v,ymax));
   const yt=[];for(let v=0;v<=ymax;v+=0.5)yt.push(v);
   CK.axes(ff,{x,y:y0,L,R,T,B,yt,xt:[1,10,60,600,3600],xfmt:v=>v<60?v+' s':v<3600?(v/60)+' min':'1 h',yfmt:v=>CK.fmt.num(v,v%1?1:0),xl:'time after one watt of switching is added',yl:'°C per W'});
   CK.el('path',{d:CK.path(ks.map(k=>[k,M.step_open[k]]),x,y),style:'fill:none;stroke:var(--c1)','stroke-width':2.4},ff.svg);
   CK.el('path',{d:CK.path(ks.filter(k=>M.step_closed[k]<=ymax).map(k=>[k,M.step_closed[k]]),x,y),style:'fill:none;stroke:var(--bad)','stroke-width':2.4},ff.svg);
   const labs=[CK.txt(ff.svg,x(40),y(M.step_open[60])+18,'thermal network alone','lab')],yc=y(Math.min(ymax,M.step_closed[600])*0.75);   /* left of the steep part, clear of the curve */
   if(W<420)labs.push(CK.txt(ff.svg,x(300)-8,yc-7,'with leakage feeding back','lab','end'),CK.txt(ff.svg,x(300)-8,yc+8,'(at 80 °C)','lab','end'));
   else labs.push(CK.txt(ff.svg,x(300)-8,yc,'with leakage feeding back (at 80 °C)','lab','end'));
   const off=ks.find(k=>M.step_closed[k]>ymax);if(off!==undefined)labs.push(CK.txt(ff.svg,W-R,y(ymax)+14,`off scale: ${M.step_closed[off].toFixed(1)} °C/W at ${off>=3600?off/3600+' h':off/60+' min'}`,'lab','end'));
   CK.inside(ff,labs);
   /* one band per computed step time: the hairline and the dots mark both curves there */
   const nodes=[];
   ks.forEach((k,i)=>{const a=i?Math.sqrt(ks[i-1]*k):1,b=i<ks.length-1?Math.sqrt(k*ks[i+1]):3600,o=M.step_open[k],c=M.step_closed[k],g=CK.el('g',{class:'band'},ff.svg);
    CK.el('rect',{x:x(a),y:T,width:x(b)-x(a),height:H-B-T,class:'ck-hit'},g);
    CK.el('line',{x1:x(k),x2:x(k),y1:T,y2:H-B,class:'xh',style:'stroke:var(--ink-2)','stroke-dasharray':'2 3'},g);
    CK.el('circle',{cx:x(k),cy:y(o),r:3.5,class:'xh',style:'fill:var(--c1)'},g);if(c<=ymax)CK.el('circle',{cx:x(k),cy:y(c),r:3.5,class:'xh',style:'fill:var(--bad)'},g);
    CK.tip(ff,g,`<b>${tf(k)} after one watt of switching is added</b><br>thermal network alone: ${f2(o)} °C per W<br>with leakage feeding back (at 80 °C): ${f2(c)} °C per W${c>ymax?' (off scale)':''}`);nodes.push(g);});
   CK.keynav(ff,nodes);}});})();
 /* the whole session: the sensor against the thermal network driven by the measured board power */
 (function(){const tr=M.trace.filter(p=>p.t>=180),t0=tr[0].t,tmax=tr[tr.length-1].t;
  const hm=t=>{const m=Math.round(t/60);return `${Math.floor(m/60)} h ${String(m%60).padStart(2,'0')} min`;};
  CK.frame('session',{height:W=>W<600?280:338,label:'Die temperature over the long session: sensor reading and the thermal network',draw:ff=>{
   const nar=ff.narrow,W=ff.W,H=ff.H,L=40,R=14,T=26,B=34;const x=CK.lin(t0,tmax,L,W-R),y=CK.lin(74,92,H-B,T);const xt=[];for(let m=Math.ceil(t0/1800)*1800;m<=tmax;m+=1800)xt.push(m);
   CK.axes(ff,{x,y,L,R,T,B,yt:[76,80,84,88,92],xt,xfmt:t=>(t/3600).toFixed(1)+' h',yfmt:String,yl:'die temperature, °C'});
   CK.el('path',{d:CK.path(tr.map(p=>[p.t,p.T]),x,y),style:'fill:none;stroke:var(--c1)','stroke-width':1.1,opacity:0.85},ff.svg);
   CK.el('path',{d:CK.path(tr.map(p=>[p.t,Math.min(p.fit,92)]),x,y),style:'fill:none;stroke:var(--c2)','stroke-width':1.1},ff.svg);
   bands(ff,x,t0,tmax,nar?24:48,T,B,p=>`<b>${hm(p.t)}</b> into the session<br>sensor ${f1(p.T)} °C · thermal network ${f2(p.fit)} °C`,p=>[[y(p.T),'var(--c1)'],[y(Math.min(p.fit,92)),'var(--c2)']],tr);}});})();
 /* temperature per flip */
 (function(){const opsPerS=1024*600e6/546;const LAB={ffclk:'register bit clocked',mult:'net toggle in the multiplier tree',rest:'net toggle elsewhere in the unit',bus:'operand-word bit toggled'};
  const row=D.power_model.rows.find(r=>r.values==='randn');let tw=0;
  const body=Object.keys(PW.e_fJ).map(k=>{const e=PW.e_fJ[k];const rate=row?row[k]*1e6*opsPerS/1e15:0;const w=e*rate;tw+=w;
    return `<tr><td>${LAB[k]}</td><td class="num">${e.toFixed(e<0.1?3:2)} fJ</td><td class="num">${rate.toFixed(rate<1?2:1)}</td><td class="num">${w.toFixed(1)} W</td><td class="num">${(w*M.step_closed[10]).toFixed(1)}</td><td class="num">${(w*M.step_closed[60]).toFixed(1)}</td></tr>`;}).join('');
  document.getElementById('perflip').innerHTML='<thead><tr><th>Kind of flip</th><th class="num">energy each</th><th class="num">a random fp32 matmul does, 10¹⁵ per second</th><th class="num">which is</th><th class="num">°C after 10 s</th><th class="num">°C after 1 min</th></tr></thead><tbody>'+body+
   `<tr><td><i>all four, plus ${f1(PW.p_sm_full_chip)} W for the tensor state machines</i></td><td></td><td></td><td class="num"><i>${(tw+PW.p_sm_full_chip).toFixed(1)} W</i></td><td class="num"><i>${((tw+PW.p_sm_full_chip)*M.step_closed[10]).toFixed(1)}</i></td><td class="num"><i>${((tw+PW.p_sm_full_chip)*M.step_closed[60]).toFixed(1)}</i></td></tr></tbody>`;})();
 /* equilibrium: die temperature the card can hold, against switching power; the room is the pricer's ambient (section 9) */
 (function(){const Rt=M.R_total,amb=CK.bus('ambient'),host=document.getElementById('budget');
  const lg=document.createElement('div');host.before(lg);const ro=document.createElement('div');host.after(ro);CK.readout(ro);
  CK.legend(lg,[{key:'s',label:'where the die settles',mark:'line',color:'var(--c1)'},{key:'r',label:'above this, it runs away',mark:'dash',color:'var(--bad)'}]);
  const fb=CK.frame('budget',{height:W=>W<600?300:320,label:'Where the die settles for each switching power held for hours',draw:ff=>{
   const Ta=amb.value==null?M.T_amb:amb.value,W=ff.W,H=ff.H,L=46,R=14,T=26,B=40;
   const pd=t=>(t-Ta)/Rt-PW.P_fix-PW.A_leak_at_80*Math.exp((t-80)/PW.T_L);let best=[-1e9,0];const pts=[];
   for(let t=50;t<=100;t+=0.05){const p=pd(t);pts.push([p,t]);if(p>best[0])best=[p,t];}
   const x=CK.lin(-12,32,L,W-R),y=CK.lin(50,100,H-B,T);
   CK.axes(ff,{x,y,L,R,T,B,xt:ff.narrow?[-10,0,10,20,30]:[-10,-5,0,5,10,15,20,25,30],yt:[50,60,70,80,90,100],xfmt:v=>(v>0?'+':'')+CK.fmt.num(v,0)+' W',
    xl:'switching power held for hours (0 = an idle card)',yl:'die temperature where it settles, °C'});
   const ln=q=>CK.path(q.filter(z=>z[0]>=-12&&z[0]<=32),x,y);
   CK.el('path',{d:ln(pts.filter(q=>q[1]<=best[1])),style:'fill:none;stroke:var(--c1)','stroke-width':2.6},ff.svg);
   CK.el('path',{d:ln(pts.filter(q=>q[1]>=best[1])),style:'fill:none;stroke:var(--bad)','stroke-width':2,'stroke-dasharray':'6 4'},ff.svg);
   CK.el('line',{x1:x(best[0]),x2:x(best[0]),y1:T,y2:H-B,style:'stroke:var(--axis)','stroke-dasharray':'3 3'},ff.svg);
   CK.txt(ff.svg,x(best[0])+6,y(51.5),`+${best[0].toFixed(1)} W`,'lab-strong');
   ro.set(`In a <b>${Ta.toFixed(1)} °C</b> room (model ambient) aifoundry2's die, in its desktop chassis, can hold <b>+${best[0].toFixed(1)} W</b> of switching, settling at ${best[1].toFixed(0)} °C; beyond that there is no equilibrium, only a time to 90 °C.`);
   const nodes=[];
   const top=CK.el('circle',{cx:x(best[0]),cy:y(best[1]),r:6,style:'fill:var(--surface);stroke:var(--ink)','stroke-width':2},ff.svg);
   CK.tip(ff,top,`<b>The flip budget in a ${Ta.toFixed(1)} °C room</b> (model ambient)<br>+${best[0].toFixed(2)} W of switching, with the die at ${best[1].toFixed(0)} °C: beyond it there is no equilibrium, only a time to 90 °C`);nodes.push(top);
   for(const [p,lab] of [['zeros','zeros'],['ones','ones'],['randn','random normal']]){const pr=M.per_run.find(q=>q.values===p&&q.active===1024);if(!pr)continue;
    const g=CK.el('g',{},ff.svg);CK.el('rect',{x:x(pr.p_dyn_flips)-6,y:y(99),width:12,height:y(52)-y(99),class:'ck-hit'},g);
    CK.el('line',{x1:x(pr.p_dyn_flips),x2:x(pr.p_dyn_flips),y1:y(52),y2:y(94),style:'stroke:'+COL[p],'stroke-width':2},g);
    const lx=x(pr.p_dyn_flips),rt=lx>W-R-110;CK.txt(g,lx,y(96),lab,'lab',rt?'end':'middle');CK.tip(ff,g,`<b>${lab}</b> at full load switches ${pr.p_dyn_flips.toFixed(1)} W (flip counts)`);nodes.push(g);}
   CK.keynav(ff,nodes);
}});
  amb.on(()=>fb.redraw());
 })();
})();

/* ================= structured matrices: predicted before measuring ================= */
if (D.structured) (function(){
 const SN=KIND;
 const rows=Object.keys(D.structured.measured).map(k=>({k,pred:D.structured.before.patterns[k].p_board_at_launch,meas:D.structured.measured[k].p80,sd:D.structured.measured[k].p80_sd,n:D.structured.measured[k].n,fl:D.structured.before.patterns[k].flips,rise:D.structured.measured[k].rise})).sort((a,b)=>a.meas-b.meas);
 const lg=document.createElement('div');document.getElementById('struct').before(lg);
 CK.legend(lg,[{key:'p',label:'predicted from the tiles, before the first run',mark:'line',color:'var(--ink)'},{key:'m',label:'measured',mark:'dot',color:'var(--c2)'}]);
 CK.frame('struct',{height:W=>8+rows.length*(W<600?42:28)+34,label:'Board power at the launch temperature, predicted from the tiles against measured, per matrix',draw:ff=>{
  const nar=ff.narrow,W=ff.W,rh=nar?42:28,L=nar?8:250,R=nar?14:30,T=8,yAx=T+rows.length*rh,x=CK.lin(34,70,L,W-R);
  const g0=CK.el('g',{'aria-hidden':'true'},ff.svg),tl=[];
  for(let t=35;t<=70;t+=5){CK.el('line',{x1:x(t),x2:x(t),y1:T,y2:yAx+4,class:'grid-line'},g0);if(!nar||t%10===0)tl.push(CK.txt(g0,x(t),yAx+22,t+' W','tick','middle'));}
  CK.inside(ff,tl);
  const nodes=[];
  rows.forEach((r,i)=>{const y0=T+i*rh,yy=nar?y0+28:y0+rh/2,g=CK.el('g',{},ff.svg);
   CK.el('rect',{x:0,y:y0,width:W,height:rh,class:'ck-hit'},g);
   CK.txt(g,nar?L:L-10,nar?y0+13:yy+4,SN[r.k]||r.k,'lab',nar?'start':'end');CK.el('line',{x1:L,x2:W-R,y1:yy,y2:yy,class:'grid-line',opacity:0.5},g);
   CK.el('line',{x1:x(r.pred),x2:x(r.pred),y1:yy-10,y2:yy+10,style:'stroke:var(--ink)','stroke-width':2.5},g);CK.el('circle',{cx:x(r.meas),cy:yy,r:6,style:'fill:var(--c2);stroke:var(--surface)',opacity:0.9,'stroke-width':1.5},g);
   CK.tip(ff,g,()=>`<b>${SN[r.k]||r.k}</b><br>predicted ${f1(r.pred)} W, measured ${f1(r.meas)} W (${r.n} runs, sd ${f2(r.sd)})<br>${Math.round(r.fl.valid).toLocaleString()} of 4,096 multiply-adds valid · ${(r.fl.ffclk/1e6).toFixed(2)} M bits clocked · ${((r.fl.mult+r.fl.rest)/1e6).toFixed(1)} M net toggles per op`);nodes.push(g);});
  CK.keynav(ff,nodes);}});
 const e=rows.map(r=>r.pred-r.meas),rms=Math.sqrt(e.reduce((a,v)=>a+v*v,0)/e.length);
 document.getElementById('struct-tbl').innerHTML='<thead><tr><th>Matrix (A and B, 16×16 tiles)</th><th class="num">multiply-adds not gated</th><th class="num">register bits clocked, M</th><th class="num">net toggles, M</th><th class="num">predicted W</th><th class="num">measured W</th><th class="num">error</th><th class="num">end reading − launch, °C (whole degrees)</th></tr></thead><tbody>'+
  rows.map(r=>`<tr><td>${SN[r.k]||r.k}</td><td class="num">${Math.round(r.fl.valid).toLocaleString()}</td><td class="num">${(r.fl.ffclk/1e6).toFixed(2)}</td><td class="num">${((r.fl.mult+r.fl.rest)/1e6).toFixed(r.fl.mult+r.fl.rest>1e7?1:2)}</td><td class="num">${f1(r.pred)}</td><td class="num"><b>${f1(r.meas)}</b></td><td class="num">${r.pred-r.meas>=0?'+':''}${f1(r.pred-r.meas)}</td><td class="num">${r.rise>=0?'+':''}${f1(r.rise)}</td></tr>`).join('')+
  `<tr><td><i>rms error over ${rows.length} matrices</i></td><td></td><td></td><td></td><td></td><td></td><td class="num"><i>${f2(rms)} W</i></td><td></td></tr></tbody>`;
})();

/* ---------- structured matrices: long runs against the frozen model, nothing fitted on that session ---------- */
if (D.validation) (function(){const SN=Object.assign({randn:'random normal (reference)',ones:'ones (reference)'},SNAME);
 document.getElementById('struct-long').innerHTML='<thead><tr><th>Matrix</th><th class="num">switching power from its flips, W</th><th class="num">measured: 90 °C after, s</th><th class="num">predicted, s</th><th class="num">error</th></tr></thead><tbody>'+
  D.validation.afternoon.rows.map(r=>{const pc=r.capped&&r.t_cap_pred?(r.t_cap_pred/r.dur-1)*100:null;
   return `<tr><td>${SN[r.values]||r.values}</td><td class="num">${f1(r.p_flips)}</td><td class="num">${r.capped?'<b>'+r.dur.toFixed(0)+'</b>':'not in '+r.dur.toFixed(0)+' s: '+f1(r.T_end_meas)+' °C'}</td><td class="num">${r.capped?(r.t_cap_pred?r.t_cap_pred.toFixed(0):'never'):f1(r.T_end_pred)+' °C'}</td><td class="num">${pc!==null?(Math.abs(pc)<0.5?'0%':(pc>=0?'+':'')+pc.toFixed(0)+'%'):(r.T_end_pred-r.T_end_meas>=0?'+':'')+f1(r.T_end_pred-r.T_end_meas)+' °C'}</td></tr>`;}).join('')+'</tbody>';})();

/* ---------- section 10: the second card, and one number per card ---------- */
(function(){const C=D.cards;if(!C)return;
 const SHORT={zeros:'zeros',sparse50:'50% zeroed',ones:'ones',pi:'π',signs:'random sign',mant:'random mantissa',uniform:'uniform',randn:'normal'};
 const P=C.patterns,f=(v,n)=>v.toFixed(n===undefined?2:n),sg=(v,n)=>(v>=0?'+':'−')+Math.abs(v).toFixed(n===undefined?2:n);
 const rms=a=>Math.sqrt(a.reduce((q,v)=>q+v*v,0)/a.length);
 const LOO=C.loo.per_pattern,worstCal=Object.keys(LOO).reduce((a,k)=>LOO[k]>LOO[a]?k:a);
 const nm=v=>NAMES[v]||v,ratios=P.map(p=>p.a3/p.model);
 const r32=P.filter(p=>p.values!=='signs'&&p.values!=='mant').map(p=>p.a3/p.a2);   /* the six patterns with three runs or more on each card */
 /* the text: every number from D.cards */
 document.getElementById('cardswcap').textContent=
  `Each card at its own launch temperature, ${f(C.launch.aifoundry2.T)} °C and ${f(C.launch.aifoundry3.T)} °C, both at 600 MHz. `+
  `aifoundry3's values are one 13-minute session: three runs per pattern, one of random sign and one of random mantissa. `+
  `Idle power under those runs was ${f(C.idle.aifoundry2,1)} W and ${f(C.idle.aifoundry3,1)} W, and is subtracted. `+
  `The dashed rule on each pair is this report's model, fitted on aifoundry2, times the scale set below (1 = unchanged).`;
 document.getElementById('scaletext').innerHTML=
  `The ordering is the same on both cards wherever the difference exceeds the noise, and the ratios between patterns agree `+
  `within it (aifoundry3 over aifoundry2, ${f(Math.min(...r32))} to ${f(Math.max(...r32))} for the six patterns with three runs on each card). `+
  `Applied to aifoundry3 unchanged, the model is off by `+
  `<b>${f(C.rms_raw)} W rms</b>, worst case ${f(C.max_raw)} W, and it overestimates every pattern, by about ${Math.round(100*(1-C.scale))}% `+
  `(${Math.round(100*(1-Math.max(...ratios)))} to ${Math.round(100*(1-Math.min(...ratios)))}% per pattern; the differences between patterns are within the noise). `+
  `The two cards also ran ${f(C.launch.aifoundry2.T-C.launch.aifoundry3.T,0)} °C apart, so this does not yet separate the card from its temperature. `+
  `Multiply the model's switching power by one `+
  `number, <b>${f(C.scale)}</b>, and the residual falls to <b>${f(C.rms_scaled)} W rms</b> over a `+
  `${f(Math.min(...P.map(p=>p.a3)),1)} to ${f(Math.max(...P.map(p=>p.a3)),0)} W range, which is as good as the in-sample fit on the `+
  `card the coefficients came from. Calibrating that number on one pattern's runs and predicting the other seven patterns gives `+
  `${f(C.loo.median_rms)} W rms in the median and ${f(LOO[worstCal])} W rms at worst (calibrated on ${nm(worstCal)}), with `+
  `${f(C.loo.worst)} W the largest single-pattern error; calibrated on random normal it is ${f(LOO.randn)} W rms.`;
 const lk=C.leakage;
 document.getElementById('leakoff').textContent=sg(lk.mean_offset_W)+' W';
 document.getElementById('leaktab').innerHTML='<thead><tr><th class="num">aifoundry3 die °C</th><th class="num">measured idle W</th><th class="num">aifoundry2 law W</th><th class="num">difference</th><th class="num">samples</th></tr></thead><tbody>'+
  lk.idle_curve.map(r=>`<tr><td class="num">${r.T}</td><td class="num">${f(r.W)}</td><td class="num">${f(r.card2_law_W)}</td><td class="num">${sg(r.W-r.card2_law_W)}</td><td class="num">${r.n.toLocaleString('en-GB')}</td></tr>`).join('')+
  `<tr><td class="num"><b>mean of the four bins</b></td><td class="num"></td><td class="num"></td><td class="num"><b>${sg(lk.mean_offset_W)}</b></td><td class="num"></td></tr></tbody>`;
 const b0=lk.idle_curve[0],mr=lk.model_rule;
 if(mr){const put=(id,v)=>{document.getElementById(id).textContent=v;};const Ts=mr.idle_curve.map(b=>b.T);
  put('ln-T0',b0.T);put('ln-n',b0.n);put('ln-s',f(b0.n/10,1));put('ln-T',`${Math.min(...Ts)}–${Math.max(...Ts)}`);put('ln-off',sg(mr.mean_offset_W));}

 /* one number per card: the model times a scale, against aifoundry3, with the residual per pattern */
 let scale=1,cal=null;
 const resid=s=>P.map(p=>p.a3-s*p.model);
 const RB=Math.ceil(Math.max(...[0.85,1.05].flatMap(s=>resid(s).map(Math.abs)))*2)/2;   /* residual axis covers the slider's range */
 CK.legend('cardsw-leg',[{key:'a2',label:`aifoundry2 at ${f(C.launch.aifoundry2.T,0)} °C`,mark:'box',color:'var(--c1)'},
  {key:'a3',label:`aifoundry3 at ${f(C.launch.aifoundry3.T,0)} °C`,mark:'box',color:'var(--c2)'},
  {key:'m',label:'model (aifoundry2 fit) × scale',mark:'dash',color:'var(--ink)'}]);
 const out=CK.readout('cardsw-out');
 const fr=CK.frame('cardsw',{height:W=>W<600?460:390,label:'Switching power over idle on two cards against the scaled model, with residuals',draw:ff=>{
  const W=ff.W,H=ff.H,L=48,R=10,T=24,B=ff.narrow?76:36,gap=44,hTop=Math.round((H-T-B-gap)*0.62),yb=T+hTop,y0r=yb+gap,yr1=H-B;
  const mx=Math.max(...P.map(p=>Math.max(p.a2,p.a3,p.model)))*1.08,bw=(W-L-R)/P.length;
  const y=CK.lin(0,mx,yb,T),yr=CK.lin(-RB,RB,yr1,y0r),x=i=>L+bw*i;
  const g0=CK.el('g',{'aria-hidden':'true'},ff.svg);
  for(const t of y.ticks(4)){CK.el('line',{x1:L,x2:W-R,y1:y(t),y2:y(t),class:'grid-line'},g0);CK.txt(g0,L-6,y(t)+4,CK.fmt.num(t,0),'tick','end');}
  CK.txt(g0,2,T-10,'switching power over idle, W','lab');
  for(const t of [-RB,0,RB]){CK.el('line',{x1:L,x2:W-R,y1:yr(t),y2:yr(t),class:t?'grid-line':'ck-axis'},g0);CK.txt(g0,L-6,yr(t)+4,(t>0?'+':'')+CK.fmt.num(t,1),'tick','end');}
  CK.txt(g0,2,y0r-16,'aifoundry3 − model × scale, W','lab');
  const e=resid(scale),nodes=[];
  P.forEach((p,i)=>{const g=CK.el('g',{},ff.svg),w=bw*0.3,cx=x(i)+bw/2;
   CK.el('rect',{x:x(i),y:T,width:bw,height:yr1-T,class:'ck-hit'},g);
   CK.el('rect',{x:cx-w-1,y:y(p.a2),width:w,height:yb-y(p.a2),rx:2,style:'fill:var(--c1)'},g);
   CK.el('rect',{x:cx+1,y:y(p.a3),width:w,height:yb-y(p.a3),rx:2,style:'fill:var(--c2)'},g);
   CK.el('line',{x1:cx-w-5,x2:cx+w+5,y1:y(scale*p.model),y2:y(scale*p.model),style:'stroke:var(--ink)','stroke-width':2,'stroke-dasharray':'4 3'},g);
   const r0=yr(0),r1=yr(Math.max(-RB,Math.min(RB,e[i])));
   CK.el('rect',{x:cx-w/2,y:Math.min(r0,r1),width:w,height:Math.max(1,Math.abs(r1-r0)),rx:2,style:'fill:var(--c2)'},g);
   if(bw>=46)CK.txt(g,cx,e[i]>=0?r1-5:r1+14,sg(e[i]),'tick','middle');
   if(ff.narrow){const t=CK.txt(g,cx+4,yr1+14,SHORT[p.values]||p.values,cal===p.values?'lab-strong':'tick','end');t.setAttribute('transform',`rotate(-40 ${cx+4} ${yr1+14})`);}
   else (SHORT[p.values]||p.values).split(' ').forEach((wd,k)=>CK.txt(g,cx,yr1+15+14*k,wd,cal===p.values?'lab-strong':'tick','middle'));
   CK.tip(ff,g,()=>`<b>${nm(p.values)}</b><br>aifoundry2 ${f(p.a2)} W · aifoundry3 ${f(p.a3)} W<br>model ${f(p.model)} W, × ${scale.toFixed(3)} = ${f(scale*p.model)} W<br>aifoundry3 − scaled model: ${sg(e[i])} W · aifoundry3 ÷ model ${f(p.a3/p.model,3)}`);
   nodes.push(g);});
  CK.keynav(ff,nodes);}});
 function update(){const e=resid(scale),iw=e.reduce((a,v,k)=>Math.abs(v)>Math.abs(e[a])?k:a,0);
  let t=`<b>scale ${scale.toFixed(3)}</b>${cal==='ls'?' (least squares over all eight)':cal?` (calibrated on ${nm(cal)})`:''}: rms over all 8 patterns <b>${f(rms(e))} W</b>`;
  if(cal&&cal!=='ls'){const k=P.findIndex(p=>p.values===cal);t+=`; over the other 7 <b>${f(rms(e.filter((v,j)=>j!==k)))} W</b>`;}
  t+=`; largest single error ${f(Math.abs(e[iw]))} W (${nm(P[iw].values)}).`;
  out.set(t);fr.redraw();}
 const ctl=document.getElementById('cardsw-ctl');
 const rg=CK.range(ctl.appendChild(document.createElement('div')),{label:'scale on the model’s switching power',min:0.85,max:1.05,step:0.001,value:1,fmt:v=>v.toFixed(3),onInput:v=>{scale=v;cal=null;mark();update();}});
 const bx=ctl.appendChild(document.createElement('div'));bx.className='controls';bx.setAttribute('role','group');bx.setAttribute('aria-label','calibrate the scale on');
 const lab=bx.appendChild(document.createElement('span'));lab.className='small';lab.textContent='calibrate on:';lab.style.alignSelf='center';
 const btns=[...P.map(p=>[p.values,SHORT[p.values]||p.values,p.a3/p.model]),['ls','least squares',C.scale]].map(([k,t,v])=>{
  const b=bx.appendChild(document.createElement('button'));b.type='button';b.textContent=t;b.dataset.k=k;b.setAttribute('aria-pressed','false');
  b.addEventListener('click',()=>{rg.set(v);scale=v;cal=k;mark();update();});return b;});
 function mark(){btns.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.k===cal)));}
 update();
})();

/* ---------- numbers in the prose, from the data ---------- */
(function(){const put=(id,v)=>{const e=document.getElementById(id);if(e)e.textContent=v;};
 const P=D.patterns,R=D.runs,TL=D.thermal.model_T_at_launch,mean=a=>a.reduce((q,v)=>q+v,0)/a.length,sd=a=>{const m=mean(a);return Math.sqrt(mean(a.map(v=>(v-m)**2)));};
 const WORD=['no','one','two','three','four','five','six','seven','eight','nine','ten','eleven','twelve'],word=n=>WORD[n]||String(n);
 /* section 2: the control held */
 const pb=R.map(r=>r.p_before);
 put('ctl-n',R.length);put('ctl-T',`${f2(TL.mean)} ± ${f2(TL.sd)}`);put('ctl-idle',`${f2(mean(pb))} ± ${f2(sd(pb))}`);
 put('ctl-sdP',f2(P.randn.p80_sd));put('ctl-sdT',f2(P.randn.rise_fit_sd));
 /* section 4: the slow stages, from section 8's model */
 if(D.model){const M=D.model;put('r-slow',f2(M.R.reduce((q,r,k)=>q+(M.taus[k]>=60?r:0),0)));put('r-all',f2(M.R_total));}
 /* section 4: thermal against electrical heating power over the patterns that heat the die by more than a degree */
 const hot=Object.values(P).filter(p=>p.a_thermal!=null&&p.rise_fit>1);
 if(hot.length){const k=hot.reduce((q,p)=>q+p.a_electrical*p.a_thermal,0)/hot.reduce((q,p)=>q+p.a_electrical**2,0);
  put('hot-n',hot.length);put('hot-slope',f2(k));put('hot-rms',f1(Math.sqrt(mean(hot.map(p=>(p.a_thermal-p.a_electrical)**2)))));}
 /* section 5: random normal's own heating between seconds 1-3 and the last two seconds, on the sensor's scale */
 const rn=P.randn,win=(a,b)=>mean(D.grid.map((g,i)=>[g,rn.mean_rise[i]]).filter(q=>q[0]>=a&&q[0]<=b).map(q=>q[1]));
 put('lf-dP',f1(rn.p_late-rn.p_early));put('lf-dT',f1(win(rn.dur-2,rn.dur)-win(1,3)));put('lf-all',f1(rn.rise_end));
 if(D.model){const M=D.model,lam=M.power.lambda_at_80;
  /* section 8: leakage loop */
  put('lg-lam',f2(lam));put('lg-10m',f1(M.step_open[600]));put('lg-10m2',f1(M.step_open[600]));put('lg-R',f2(M.R_total));
  put('lg-gain',`${f2(lam)} × ${f2(M.R_total)} = ${f2(M.loop_gain_at_80)}`);put('lg-10c',f1(M.step_closed[600]));
  /* section 8: how well it fits the ten-minute runs */
  const unc=M.per_run.filter(q=>q.session.indexOf('long')>=0&&!q.capped),e=unc.map(q=>q.T_end_pred-q.T_end_meas);
  const fc=unc.filter(q=>q.t_cap_pred).sort((a,b)=>b.t_cap_pred-a.t_cap_pred);
  const who=q=>({sparse75:'the 75%-zero matrix'}[q.values]||NAMES[q.values]||q.values)+(q.active<1024?` on ${q.active.toLocaleString('en-GB')} minions`:'');
  const and=a=>a.length<2?a.join(''):a.slice(0,-1).join(', ')+' and '+a[a.length-1];
  put('fit10',`For the ${word(unc.length)} ten-minute runs the end temperature is off by ${f1(Math.sqrt(mean(e.map(v=>v*v))))} °C rms and ${f1(mean(e))} °C hot on average`+
   (fc.length?`; ${word(fc.length)} of them (${and(fc.map(who))}) are fitted to reach 90 °C, at ${and(fc.map(q=>q.t_cap_pred.toFixed(0)))} s, though they ended at ${and(fc.map(q=>q.T_end_meas.toFixed(0)))} °C.`:'.'));}
 if(D.validation){const v=D.validation.timesplit.summary;put('acc-med',v.median_abs_pct.toFixed(0));put('acc-worst',v.worst_pct.toFixed(0));}
})();

/* ---------- section 9: price a workload, flips → watts → degrees (a port of tools/ettelem/predict_heat.py predict()) ---------- */
if (D.model && D.structured) (function(){const M=D.model,PW=M.power,amb=CK.bus('ambient');
 const leak=T=>PW.A_leak_at_80*Math.exp((Math.min(T,110)-80)/PW.T_L);
 const T_IDLE_22SEP=73;   /* the die reading after 20.6 h idle on 22 September (the DVFS report's idle check, dvfs.json idle_check) */
 const TA_22SEP=T_IDLE_22SEP-M.R_total*(PW.P_fix+leak(T_IDLE_22SEP));   /* the room that idle implies, by the heat line */
 const WL=[...D.power_model.rows.filter(r=>D.patterns[r.values]).map(r=>({k:r.values,set:'strict',name:NAMES[r.values]||r.values,fl:rowFlips(r)})),
  ...Object.keys(D.structured.before.patterns).map(k=>({k,set:'struct',name:KIND[k]||k,fl:D.structured.before.patterns[k].flips}))];
 const byK=k=>WL.find(w=>w.k===k);
 /* the run: an idle die at `start` (fast stages settled at idle power, the rest of the rise on the slow stages), then the workload */
 function run(fl,act,start,Ta){const taus=M.taus,Rs=M.R,w=flipWatts(fl,act),pdyn=sumW(w),pidle=PW.P_fix+leak(start);
  let x=Rs.map((r,k)=>taus[k]<=25?r*pidle:0);const slowR=Rs.reduce((q,r,k)=>q+(taus[k]>25?r:0),0)||1,rest=start-Ta-x.reduce((q,v)=>q+v,0);
  x=x.map((v,k)=>taus[k]<=25?v:rest*Rs[k]/slowR);
  const dt=0.1,al=taus.map(t=>1-Math.exp(-dt/t)),curve=[],at={};let T=start,tcap=null,next=1;
  for(let n=1;n<=6000;n++){const p=PW.P_fix+leak(T)+pdyn;x=x.map((v,k)=>v+al[k]*(Rs[k]*p-v));T=Ta+x.reduce((q,v)=>q+v,0);const t=n*dt;
   if(n===100)at[10]=T;if(n===600)at[60]=T;if(n===6000)at[600]=T;
   if(tcap===null&&T>=90)tcap=t;if(t>=next-1e-9){curve.push([t,T]);next*=1.04;}if(T>93)break;}   /* the runs stopped at 90 °C */
  const hold=Math.max(0,(start-Ta)/M.R_total-pidle);
  /* where it settles: the first balance point from the launch temperature in the direction it moves */
  const g=t=>Ta+M.R_total*(PW.P_fix+leak(t)+pdyn)-t;let settle=null;const d=g(start)>=0?0.02:-0.02;
  for(let t=start;t>Ta&&t<110;t+=d){if(g(t)*g(t+d)<=0){settle=t+d/2;break;}}
  return {w,pdyn,board:pidle+pdyn,pidle,curve,at,tcap,hold,duty:pdyn>0?Math.min(1,hold/pdyn):1,settle};}
 /* controls */
 const ctl=document.getElementById('pr-controls');
 const sw=ctl.appendChild(document.createElement('label'));sw.className='ck-range';sw.textContent='workload ';
 const sel=sw.appendChild(document.createElement('select'));sel.style.font='inherit';sel.style.minHeight='32px';sel.style.maxWidth='100%';
 for(const [set,lab] of [['strict','measured patterns'],['struct','structured matrices']]){const og=sel.appendChild(document.createElement('optgroup'));og.label=lab;
  for(const w of WL.filter(q=>q.set===set)){const o=og.appendChild(document.createElement('option'));o.value=w.k;o.textContent=w.name;}}
 sel.value='kaleidoscope';
 const st={k:'kaleidoscope',act:1024,start:80.9,Ta:M.T_amb};   /* 80.9 °C: the protocol's launch state in the sensor's units (section 9's note) */
 const mk=o=>CK.range(ctl.appendChild(document.createElement('div')),o);
 const rA=mk({label:'active minions',min:128,max:1024,step:128,value:st.act,fmt:v=>v.toLocaleString('en-GB'),onInput:v=>{st.act=v;upd();}});
 const rS=mk({label:'launch temperature',min:76,max:84,step:0.1,value:st.start,fmt:v=>v.toFixed(1)+' °C',onInput:v=>{st.start=v;upd();}});
 const rT=mk({label:'room and airflow (model ambient)',min:20,max:28,step:0.1,value:st.Ta,fmt:v=>v.toFixed(1)+' °C',onInput:v=>{st.Ta=v;upd();}});
 const bx=ctl.appendChild(document.createElement('div'));bx.className='controls';bx.setAttribute('role','group');bx.setAttribute('aria-label','presets');
 for(const [t,f] of [[`launch ${st.start.toFixed(1)} °C (the protocol)`,()=>rS.set(80.9)],['launch 80.0 °C (predict_heat.py)',()=>rS.set(80)],
   [`room ${M.T_amb.toFixed(1)} °C (fitted, 21 September)`,()=>rT.set(M.T_amb)],[`room ${TA_22SEP.toFixed(1)} °C (22 September: idle at ${T_IDLE_22SEP} °C)`,()=>rT.set(TA_22SEP)]]){
  const b=bx.appendChild(document.createElement('button'));b.type='button';b.textContent=t;b.addEventListener('click',f);}
 sel.addEventListener('change',()=>{st.k=sel.value;upd();});
 CK.legend('pr-leg',FLIPS.map(([k,l,c])=>({key:k,label:l,mark:'box',color:c})).concat([{key:'pred',label:'predicted',mark:'line',color:'var(--ink)'},
  {key:'meas',label:'a measured long run (sensor)',mark:'line',color:'var(--c1)'},{key:'fit',label:'the model with that run’s own history',mark:'dash',color:'var(--c1)'},
  {key:'cap',label:'measured: 90 °C reached',mark:'dot',color:'var(--c1)'}]));
 const out=CK.readout('pr-out');
 const maxSw=Math.max(...WL.map(w=>sumW(flipWatts(w.fl,1024))))*1.06;
 let R0=null;
 const fBar=CK.frame('pr-bar',{height:()=>104,maxW:520,label:'Switching power of the chosen workload by kind of flip',draw:ff=>{if(!R0)return;
  const W=ff.W,L=16,R=16,x=CK.lin(0,maxSw,L,W-R),y0=24,bh=30,nodes=[];
  for(const t of x.ticks(Math.max(3,Math.round(W/90)))){CK.el('line',{x1:x(t),x2:x(t),y1:y0-6,y2:y0+bh+6,class:'grid-line'},ff.svg);CK.txt(ff.svg,x(t),y0+bh+22,CK.fmt.num(t,0)+' W','tick','middle');}
  let acc=0;for(const [k,l,c] of FLIPS){const v=R0.w[k];if(v<0.01){acc+=v;continue;}
   const r=CK.el('rect',{x:x(acc),y:y0,width:Math.max(1,x(acc+v)-x(acc)-2),height:bh,rx:2,style:'fill:'+c},ff.svg);
   CK.tip(ff,r,`<b>${l}</b>: ${v.toFixed(2)} W (${(100*v/R0.pdyn).toFixed(0)}% of the switching)`);nodes.push(r);acc+=v;}
  const tx=x(R0.pdyn);CK.txt(ff.svg,Math.min(tx+6,W-R),y0-8,`${R0.pdyn.toFixed(1)} W switching`,'lab-strong',tx+6>W-120?'end':'start');
  CK.keynav(ff,nodes);}});
 const fT=CK.frame('pr-temp',{height:W=>W<600?280:300,label:'Predicted die temperature after launch, with any measured long run',draw:ff=>{if(!R0)return;
  const W=ff.W,H=ff.H,L=40,R=26,T=12,B=38,lo=Math.min(76,Math.floor(st.start-1)),hi=92;
  const x=CK.log(1,600,L,W-R),y=CK.lin(lo,hi,H-B,T);
  CK.axes(ff,{x,y,L,R,T,B,xt:ff.narrow?[1,10,60,600]:[1,3,10,30,60,180,600],xfmt:v=>v<60?v+' s':v/60+' min',xl:'time since launch (log scale)'});
  CK.el('line',{x1:L,x2:W-R,y1:y(90),y2:y(90),style:'stroke:var(--bad)','stroke-width':1.5,'stroke-dasharray':'5 4'},ff.svg);
  CK.txt(ff.svg,L+6,y(90)-6,'90 °C: the runs stopped here','lab');   /* top left: no curve is above 90 °C this early */
  const cl=q=>q.filter(z=>z[0]>=1&&z[0]<=600&&z[1]<=hi);
  const nodes=[];
  /* measured long runs of this workload on this many minions, and the model driven by each run's own history */
  for(const r of (D.long||[]).filter(r=>r.values===st.k&&r.minions===st.act)){
   const pts=r.sec.map((t,i)=>[t,r.T[i]]).filter(q=>q[1]!=null&&q[0]<=r.dur);
   const g=CK.el('g',{},ff.svg);CK.el('path',{d:CK.path(cl(pts),x,y),style:'fill:none;stroke:var(--c1)','stroke-width':1.3,opacity:0.9},g);
   const pr=M.per_run.find(q=>q.session.indexOf('long')>=0&&q.run===r.run);
   if(pr&&pr.curve_pred.length>1)CK.el('path',{d:CK.path(cl(pr.curve_pred.map((v,i)=>[2*i+1,v])),x,y),style:'fill:none;stroke:var(--c1)','stroke-width':1.3,'stroke-dasharray':'4 3'},g);
   const e=cl(pts).pop();if(e){const c=CK.el('circle',{cx:x(e[0]),cy:y(e[1]),r:4,style:'fill:var(--c1)'},g);
    CK.tip(ff,c,`<b>measured long run</b> (section 7): ${r.reason==='cap'?'90 °C after '+r.dur.toFixed(0)+' s':'ran '+r.dur.toFixed(0)+' s, ended at '+r.t_max.toFixed(0)+' °C'}, launched after ${Math.round(r.approach_s)} s of heating and cooling`+(pr&&pr.t_cap_pred?`<br>with that run's own history the model says ${pr.t_cap_pred.toFixed(0)} s`:''));nodes.push(c);}}
  /* afternoon session: structured matrices run long once, only their time to the cap is kept */
  if(D.validation)for(const r of D.validation.afternoon.rows.filter(r=>r.values===st.k&&r.active===st.act&&r.capped&&r.dur<=600)){
   const c=CK.el('circle',{cx:x(r.dur),cy:y(90),r:5,style:'fill:var(--c1);stroke:var(--surface)','stroke-width':1.5},ff.svg);
   CK.tip(ff,c,`<b>measured</b> in the afternoon session (section 9): 90 °C after ${r.dur.toFixed(0)} s; the frozen model, from that launch's own history, said ${r.t_cap_pred.toFixed(0)} s`);nodes.push(c);}
  CK.el('path',{d:CK.path(cl(R0.curve),x,y),style:'fill:none;stroke:var(--ink)','stroke-width':2.2},ff.svg);
  for(const [t,v] of [[10,R0.at[10]],[60,R0.at[60]],[600,R0.at[600]]]){if(v==null||v>hi)continue;
   const c=CK.el('circle',{cx:x(t),cy:y(v),r:4,style:'fill:var(--ink);stroke:var(--surface)'},ff.svg);
   CK.tip(ff,c,`predicted: ${v.toFixed(1)} °C after ${t<60?t+' s':t/60+' min'}`);nodes.push(c);}
  if(R0.tcap&&R0.tcap<=600){const c=CK.el('circle',{cx:x(R0.tcap),cy:y(90),r:5,style:'fill:var(--surface);stroke:var(--ink)','stroke-width':2},ff.svg);
   CK.tip(ff,c,`predicted: 90 °C after ${R0.tcap.toFixed(0)} s`);nodes.push(c);}
  nodes.sort((a,b)=>a.getBBox().x-b.getBBox().x);CK.keynav(ff,nodes);}});
 function upd(){const w=byK(st.k);R0=run(w.fl,st.act,st.start,st.Ta);amb.emit(st.Ta);
  const r=R0,c=v=>v.toFixed(1)+' °C',marks=[[10,'10 s'],[60,'1 min'],[600,'10 min']].filter(([t])=>r.at[t]!=null&&(!r.tcap||t<r.tcap)).map(([t,l])=>`${c(r.at[t])} after ${l}`);
  const end=r.tcap?`reaches <b>90 °C after ${r.tcap.toFixed(0)} s</b>`:r.settle!=null&&r.settle<90?`stays below 90 °C and settles at about <b>${r.settle.toFixed(1)} °C</b> after hours`:
   `stays below 90 °C for ten minutes, but by the model it has no balance point, so it would keep heating`;
  out.set(`<b>${w.name}</b> on ${st.act.toLocaleString('en-GB')} minions: <b>${r.pdyn.toFixed(1)} W</b> of switching, board <b>${r.board.toFixed(1)} W</b> at ${st.start.toFixed(1)} °C (idle ${r.pidle.toFixed(1)} W). `+
   `From an idle die at ${st.start.toFixed(1)} °C in a ${st.Ta.toFixed(1)} °C room it `+(marks.length?`reads ${marks.join(', ')}, and `:'')+`${end}. `+
   `To hold ${st.start.toFixed(1)} °C the card can shed ${r.hold.toFixed(2)} W of switching: run this workload ${(100*r.duty).toFixed(0)}% of the time.`);
  fBar.redraw();fT.redraw();}
 upd();
})();
