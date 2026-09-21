const NS='http://www.w3.org/2000/svg';
function el(t,a,p){const e=document.createElementNS(NS,t);for(const k in a)e.setAttribute(k,a[k]);if(p)p.appendChild(e);return e;}
function txt(p,x,y,s,c,an){const t=el('text',{x,y,class:c||'tick','text-anchor':an||'start'},p);t.textContent=s;return t;}
function host(id,W,H){const h=document.getElementById(id);h.innerHTML='';const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,role:'img'},h);const tip=document.createElement('div');tip.className='tip';h.appendChild(tip);return {svg,tip,h};}
function hover(g,tip,h,html){const s=ev=>{tip.innerHTML=html();tip.style.display='block';const b=h.getBoundingClientRect();tip.style.left=Math.min(ev.clientX-b.left+12,b.width-280)+'px';tip.style.top=(ev.clientY-b.top+12)+'px';};g.addEventListener('mousemove',s);g.addEventListener('mouseleave',()=>tip.style.display='none');}
const F=D.horace.fit, NAMES={zeros:'zeros',checker:'checkerboard 1,0,1,0',sparse75:'random normal, 75% zeroed',ternary:'ternary −1, 0, 1',pi:'π everywhere',twos:'twos',onebit:'one set bit (0x00800000)',ones:'ones',uniform:'uniform [0,1)',randn:'random normal'};
const order=Object.keys(F.board.at82).sort((a,b)=>F.board.at82[a]-F.board.at82[b]);
document.getElementById('leg').innerHTML='<span><i style="background:var(--c1)"></i>minion-core rail</span><span><i style="background:var(--ref)"></i>everything else (SRAM, mesh, DDR, PCIe, regulators)</span>';
(function(){const W=900,rh=34,L=230,R=70,T=8,H=T+order.length*rh+34;const {svg,tip,h}=host('bars',W,H);const x=v=>L+v/70*(W-L-R);
 for(const t of [0,10,20,30,40,50,60,70]){el('line',{x1:x(t),x2:x(t),y1:T,y2:H-30,class:'grid-line'},svg);txt(svg,x(t),H-12,t+' W','tick','middle');}
 order.forEach((p,i)=>{const y=T+i*rh+5,b=F.board.at82[p],m=F.minion.at82[p];const g=el('g',{},svg);txt(g,L-10,y+16,NAMES[p],'lab','end');
  el('rect',{x:x(0),y,width:x(m)-x(0)-2,height:22,rx:3,fill:'var(--c1)'},g);el('rect',{x:x(m),y,width:x(b)-x(m)-2,height:22,rx:3,fill:'var(--ref)'},g);
  txt(g,x(b)+6,y+16,b.toFixed(1)+' W','lab-strong');hover(g,tip,h,()=>`<b>${NAMES[p]}</b><br>board ${b.toFixed(2)} W · minion rail ${m.toFixed(2)} W<br>SRAM ${F.sram.at82[p].toFixed(2)} W · mesh ${F.noc.at82[p].toFixed(2)} W`);});})();
document.getElementById('tbl').innerHTML='<thead><tr><th>Operands (A and B)</th><th class="num">board W</th><th class="num">vs zeros</th><th class="num">minion rail W</th><th class="num">SRAM W</th><th class="num">mesh W</th><th class="num">cycles/op</th></tr></thead><tbody>'+
 order.map(p=>`<tr><td>${NAMES[p]}</td><td class="num"><b>${F.board.at82[p].toFixed(1)}</b></td><td class="num">+${(F.board.at82[p]-F.board.at82.zeros).toFixed(1)}</td><td class="num">${F.minion.at82[p].toFixed(1)}</td><td class="num">${F.sram.at82[p].toFixed(2)}</td><td class="num">${F.noc.at82[p].toFixed(2)}</td><td class="num">546.0</td></tr>`).join('')+
 `</tbody><caption class="small" style="caption-side:bottom;text-align:left;padding-top:6px">Fitted at 82 °C die temperature; temperature terms: board ${F.board.per_c.toFixed(2)} W/°C, minion rail ${F.minion.per_c.toFixed(2)}, SRAM ${F.sram.per_c.toFixed(2)}, mesh ${F.noc.per_c.toFixed(2)}.</caption>`;
(function(){const rows=D.horace.rows,W=900,H=300,L=56,R=20,T=14,B=40;const {svg,tip,h}=host('scatter',W,H);
 const x=v=>L+(v-78)/(91-78)*(W-L-R),y=v=>H-B-(v-35)/(72-35)*(H-B-T);
 for(const t of [40,50,60,70]){el('line',{x1:L,x2:W-R,y1:y(t),y2:y(t),class:'grid-line'},svg);txt(svg,L-6,y(t)+4,t+' W','tick','end');}
 for(const t of [78,80,82,84,86,88,90]){txt(svg,x(t),H-B+18,t+' °C','tick','middle');}
 const grp=p=>p==='zeros'?'c3':(p==='checker'||p==='sparse75')?'c4':(p==='randn'||p==='uniform')?'c2':'c1';
 for(const g of ['randn','ones','zeros']){const b=F.board.at82[g];el('line',{x1:x(78),y1:y(b+F.board.per_c*(78-82)),x2:x(91),y2:y(b+F.board.per_c*(91-82)),stroke:'var(--axis)','stroke-width':1.5,'stroke-dasharray':'4 4'},svg);}
 for(const r of rows){const g=el('g',{},svg);el('circle',{cx:x(r.temp),cy:y(r.board),r:6,fill:`var(--${grp(r.values)})`,stroke:'var(--surface)','stroke-width':2},g);hover(g,tip,h,()=>`<b>${NAMES[r.values]}</b>, round ${r.round+1}<br>${r.board.toFixed(1)} W at ${r.temp.toFixed(1)} °C`);}
 txt(svg,x(84.2),y(69.5),'random','lab');txt(svg,x(83),y(52.5),'constants, ternary','lab');txt(svg,x(83),y(38.5),'zeros, mostly zeros','lab');txt(svg,x(88.2),y(58),'dashed: fitted 0.78 W/°C','lab');})();
