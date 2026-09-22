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
const TH=D.thresholds;

/* ---------- the limit cycle ---------- */
(function(){const tr=D.traces.find(t=>t.values==='ones')||D.traces[0];
 const W=900,H=330,L=48,R=54,T=14,B=36;const {svg,tip,h}=host('cycle',W,H);
 const tmax=Math.max(...tr.t);const x=v=>L+(v+0.5)/(tmax+0.5)*(W-L-R);
 const yf=v=>H-B-(v-560)/(860-560)*(H-B-T)*0.55-((H-B-T)*0.45);   // clock in the top 55%
 const yp=v=>H-B-(v-25)/(95-25)*(H-B-T)*0.42;                      // power in the bottom 42%
 for(const v of [600,700,800]){el('line',{x1:L,x2:W-R,y1:yf(v),y2:yf(v),class:'grid-line'},svg);txt(svg,L-6,yf(v)+4,v,'tick','end');}
 for(const v of [30,50,70,90]){txt(svg,W-R+6,yp(v)+4,v+' W','tick');}
 for(let s=0;s<=Math.floor(tmax);s++)txt(svg,x(s),H-B+16,s,'tick','middle');
 txt(svg,(L+W-R)/2,H-4,'seconds since the kernel launched','lab','middle');
 txt(svg,4,T-2,'minion clock, MHz','lab');txt(svg,W-R+6,T-2,'board W','lab');
 el('line',{x1:L,x2:W-R,y1:yp(TH.tdp_w),y2:yp(TH.tdp_w),stroke:'var(--bad)','stroke-width':1.2,'stroke-dasharray':'5 4'},svg);
 txt(svg,W-R-4,yp(TH.tdp_w)-5,'TDP '+TH.tdp_w+' W','lab','end');
 // clock as a staircase
 const st=[];for(let i=0;i<tr.t.length;i++){if(i&&tr.mhz[i]!==tr.mhz[i-1])st.push([tr.t[i],tr.mhz[i-1]]);st.push([tr.t[i],tr.mhz[i]]);}
 el('path',{d:path(st,x,yf),fill:'none',stroke:'var(--c1)','stroke-width':2.6},svg);
 el('path',{d:path(tr.t.map((v,i)=>[v,tr.P[i]]),x,yp),fill:'none',stroke:'var(--c2)','stroke-width':1.8},svg);
 // temperature crossing the threshold
 const cross=tr.t.find((v,i)=>tr.T[i]>TH.temp_c);
 if(cross!==undefined){el('line',{x1:x(cross),x2:x(cross),y1:T,y2:H-B,stroke:'var(--c7)','stroke-width':1.2,'stroke-dasharray':'3 3'},svg);
  txt(svg,x(cross)+5,T+12,'die passes '+TH.temp_c+' °C','lab');}
 el('rect',{x:L,y:T,width:W-L-R,height:H-B-T,fill:'transparent'},svg);
 hover(svg,tip,h,()=>`<b>ones, all 1,024 minions, from a 64 °C die</b><br>blue: minion clock · orange: board power<br>the governor has no hysteresis, so it hunts`);})();

/* ---------- what caused each down-step ---------- */
(function(){const rows=D.transitions.filter(r=>r.dir==='down');
 const W=440,H=380,L=52,R=16,T=16,B=42;const {svg,tip,h}=host('attrib',W,H);
 const x=v=>L+(v-60)/(72-60)*(W-L-R),y=v=>H-B-(v-25)/(95-25)*(H-B-T);
 axes(svg,{W,H,L,R,T,B,x,y,yt:[30,45,60,75,90],xt:[60,63,66,69,72],xl:'die temperature at the step, °C',yl:'board power at the step, W'});
 el('line',{x1:x(TH.temp_c),x2:x(TH.temp_c),y1:T,y2:H-B,stroke:'var(--bad)','stroke-width':1.3,'stroke-dasharray':'5 4'},svg);
 el('line',{x1:L,x2:W-R,y1:y(TH.tdp_w),y2:y(TH.tdp_w),stroke:'var(--bad)','stroke-width':1.3,'stroke-dasharray':'5 4'},svg);
 txt(svg,x(TH.temp_c)+4,T+12,TH.temp_c+' °C',' lab');txt(svg,L+4,y(TH.tdp_w)-5,TH.tdp_w+' W','lab');
 const COL={'thermal':'var(--c2)','thermal+power':'var(--bad)','power':'var(--c4)','kernel boundary':'var(--c1)','unexplained':'var(--ink)'};
 for(const r of rows){const g=el('g',{},svg);
  el('circle',{cx:x(r.T),cy:y(r.P),r:6,fill:COL[r.why]||'var(--ref)',opacity:0.85,stroke:'var(--surface)','stroke-width':1.4},g);
  hover(g,tip,h,()=>`<b>${r.values}</b> ${r.f0}→${r.f1} MHz, ${r.mv0}→${r.mv1} mV<br>die ${r.T} °C, board ${r.P} W<br>${r.gap_to_boundary_ms} ms from a kernel boundary<br><b>${r.why}</b>`);}
 document.getElementById('attrib-leg').innerHTML=Object.entries(COL).filter(([k])=>rows.some(r=>r.why===k))
   .map(([k,v])=>`<span><i style="background:${v}"></i>${k}</span>`).join('');})();

/* ---------- wake-up probe ---------- */
(function(){const w=D.wakeup;const W=440,H=380,L=56,R=16,T=16,B=42;const {svg,tip,h}=host('wake',W,H);
 const lx=v=>Math.log10(Math.max(v,0.001));
 const x=v=>L+(lx(v)-lx(0.001))/(lx(30)-lx(0.001))*(W-L-R),y=v=>H-B-(v+30)/(90)*(H-B-T);
 axes(svg,{W,H,L,R,T,B,x,y,yt:[-20,0,20,40,60],xt:[0.001,0.01,0.1,1,10],xf:v=>v<1?(v*1000)+' µs':v+' ms',
   xl:'how long the line sat untouched',yl:'load latency minus its own shortest-idle value, cycles'});
 el('line',{x1:L,x2:W-R,y1:y(0),y2:y(0),stroke:'var(--axis)'},svg);
 const COL=['var(--c1)','var(--c3)','var(--c4)','var(--c7)','var(--bad)'];const labs=[];
 w.levels.forEach((lev,k)=>{const base=lev.median_cycles[0];
  const pts=w.idle_ms.map((d,i)=>[Math.max(d,0.001),lev.median_cycles[i]-base]);
  el('path',{d:path(pts,x,y),fill:'none',stroke:COL[k%5],'stroke-width':2.2},svg);
  const g=el('g',{},svg);pts.forEach(q=>el('circle',{cx:x(q[0]),cy:y(q[1]),r:3.5,fill:COL[k%5]},g));
  labs.push([y(pts[pts.length-1][1]),lev.level,COL[k%5]]);
  hover(g,tip,h,()=>`<b>${lev.level}</b><br>same line, longest idle minus shortest: <b>${lev.paired_delta_cycles>=0?'+':''}${lev.paired_delta_cycles} cycles</b> (median of ${lev.paired_n} repeats, IQR ${lev.paired_iqr})`);});
 labs.sort((a,b)=>a[0]-b[0]);for(let i=1;i<labs.length;i++)if(labs[i][0]-labs[i-1][0]<14)labs[i][0]=labs[i-1][0]+14;
 for(const [yy,name,c] of labs)txt(svg,W-R-2,yy+4,name,'lab','end').setAttribute('style','fill:'+c);})();

/* ---------- leakage fraction against temperature ---------- */
(function(){const m=D.leak_model;const W=440,H=380,L=52,R=16,T=16,B=42;const {svg,tip,h}=host('leakfrac',W,H);
 const x=v=>L+(v-55)/(95-55)*(W-L-R),y=v=>H-B-v/0.8*(H-B-T);
 axes(svg,{W,H,L,R,T,B,x,y,yt:[0,0.2,0.4,0.6,0.8],yf:v=>Math.round(v*100)+'%',xt:[55,65,75,85,95],
   xl:'die temperature, °C',yl:'leakage as a share of board power'});
 const band=D.leak_fraction.kanter_range;
 el('rect',{x:L,y:y(band[1]),width:W-L-R,height:y(band[0])-y(band[1]),fill:'var(--c3)',opacity:0.16},svg);
 txt(svg,L+6,y(band[1])-6,'Kanter: "typically 5–30%"','lab');
 const leak=t=>m.A_at_80*Math.exp((t-80)/m.T_L);
 const idle=[],busy=[];
 for(let t=55;t<=95;t+=0.5){idle.push([t,leak(t)/(m.P_fix+leak(t))]);busy.push([t,leak(t)/(m.P_fix+leak(t)+(D.busy_randn_80c-D.idle_80c))]);}
 el('path',{d:path(idle,x,y),fill:'none',stroke:'var(--c1)','stroke-width':2.4},svg);
 el('path',{d:path(busy,x,y),fill:'none',stroke:'var(--bad)','stroke-width':2.4},svg);
 txt(svg,x(58),y(idle[8][1])+16,'idle card','lab').setAttribute('style','fill:var(--c1)');
 txt(svg,x(58),y(busy[8][1])+16,'random-data matmul','lab').setAttribute('style','fill:var(--bad)');
 const ic=D.idle_check;const g=el('g',{},svg);
 el('circle',{cx:x(ic.die_c),cy:y(ic.temp_dependent_frac),r:6,fill:'var(--c1)',stroke:'var(--surface)','stroke-width':1.5},g);
 hover(g,tip,h,()=>`measured today after ${ic.hours_idle} h idle:<br>${f2(ic.board_w)} W at ${f1(ic.die_c)} °C, ${Math.round(100*ic.temp_dependent_frac)}% temperature-dependent`);})();

/* ---------- tables ---------- */
document.getElementById('trans').innerHTML='<thead><tr><th>Pattern</th><th class="num">t</th><th class="num">MHz</th><th class="num">mV</th><th class="num">die °C</th><th class="num">board W</th><th class="num">ms from a kernel boundary</th><th>Cause</th></tr></thead><tbody>'+
 D.transitions.filter(r=>r.dir==='down').map(r=>`<tr><td>${r.values}</td><td class="num">${f1(r.t)} s</td><td class="num">${r.f0}→${r.f1}</td><td class="num">${r.mv0}→${r.mv1}</td><td class="num">${r.T}</td><td class="num">${f1(r.P)}</td><td class="num">${r.gap_to_boundary_ms}</td><td>${r.why}</td></tr>`).join('')+'</tbody>';
(function(){const s=D.transition_summary,w=D.wakeup,ic=D.idle_check;
 const V=[['“Any mature design runs a DVFS loop that steps voltage and frequency to stay inside a power and thermal envelope.”','confirmed',
   `Three operating points, ${D.operating_points.map(o=>o.mhz+' MHz at '+f2(o.volts)+' V').join(', ')}. Voltage moved with frequency in all ${s.total} observed transitions.`],
  ['“The chip counts bus bits and execution-unit activity factors and computes its own power estimate on millisecond timescales.”','not on this chip',
   'The loop reads a measured PMIC power number and a PVT temperature over I2C. There is no activity counter anywhere in it. He hedged that Esperanto might not have it; that hedge was right.'],
  ['“Thermal sensors are part of the same loop, because leakage depends on temperature.”','confirmed, and thermal has priority',
   `The temperature branch is tested before the power branch, and ${s.by_cause['thermal']||0} of ${s.down} down-steps were thermal-only.`],
  ['“Cache data arrays sit behind leakage-suppression transistors… un-suppress only what you need, at a small wake-up latency.”','built, not used',
   `The silicon has per-minion sleep and isolation control; the open configuration ties it off and no firmware line drives it. After 27 ms of idle no level shows a wake-up: paired shifts are ${w.levels.map(l=>l.level+' '+(l.paired_delta_cycles>=0?'+':'')+l.paired_delta_cycles).join(', ')} cycles, and the only positive one is DRAM row closure.`],
  ['“Leakage is typically 5–30% of a design’s power, about 20% common.”','this card is worse',
   `${Math.round(100*D.leak_fraction.busy_randn_80c)}% of a random-data matmul and ${Math.round(100*D.leak_fraction.idle_80c)}% of an idle card at 80 °C.`],
  ['“Leakage costs power, not correctness.”','confirmed',
   `Nothing anywhere in this work produced a wrong result; ${ic.hours_idle} h of idling cost ${f1(ic.board_w)} W and no errors.`]];
 document.getElementById('verdict').innerHTML='<thead><tr><th>What David Kanter said</th><th>Verdict on the ET-SoC-1</th><th>Evidence</th></tr></thead><tbody>'+
  V.map(v=>`<tr><td>${v[0]}</td><td class="lvl">${v[1]}</td><td class="small">${v[2]}</td></tr>`).join('')+'</tbody>';})();
