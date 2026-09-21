const NS='http://www.w3.org/2000/svg';
function el(t,a,p){const e=document.createElementNS(NS,t);for(const k in a)e.setAttribute(k,a[k]);if(p)p.appendChild(e);return e;}
function txt(p,x,y,s,c,an){const t=el('text',{x,y,class:c||'tick','text-anchor':an||'start'},p);t.textContent=s;return t;}
function host(id,W,H){const h=document.getElementById(id);h.innerHTML='';const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,role:'img'},h);const tip=document.createElement('div');tip.className='tip';h.appendChild(tip);return {svg,tip,h};}
function hover(g,tip,h,html){const s=ev=>{tip.innerHTML=html();tip.style.display='block';const b=h.getBoundingClientRect();tip.style.left=Math.min(ev.clientX-b.left+12,b.width-280)+'px';tip.style.top=(ev.clientY-b.top+12)+'px';};g.addEventListener('mousemove',s);g.addEventListener('mouseleave',()=>tip.style.display='none');}
const F=D.horace.fit, M2=D.horace2.mean, NAMES={zeros:'zeros',checker:'checkerboard 1,0,1,0',sparse75:'random normal, 75% zeroed',ternary:'ternary −1, 0, 1',pi:'π everywhere',twos:'twos',onebit:'one set bit (0x00800000)',ones:'ones',uniform:'uniform [0,1)',randn:'random normal'};
const order=Object.keys(M2).sort((a,b)=>M2[a].board-M2[b].board);
document.getElementById('leg').innerHTML='<span><i style="background:var(--c1)"></i>minion-core rail</span><span><i style="background:var(--ref)"></i>everything else (SRAM, mesh, DDR, PCIe, regulators)</span>';
(function(){const W=900,rh=34,L=230,R=70,T=8,H=T+order.length*rh+34;const {svg,tip,h}=host('bars',W,H);const x=v=>L+v/70*(W-L-R);
 for(const t of [0,10,20,30,40,50,60,70]){el('line',{x1:x(t),x2:x(t),y1:T,y2:H-30,class:'grid-line'},svg);txt(svg,x(t),H-12,t+' W','tick','middle');}
 order.forEach((p,i)=>{const y=T+i*rh+5,b=M2[p].board,m=M2[p].minion;const g=el('g',{},svg);txt(g,L-10,y+16,NAMES[p],'lab','end');
  el('rect',{x:x(0),y,width:x(m)-x(0)-2,height:22,rx:3,fill:'var(--c1)'},g);el('rect',{x:x(m),y,width:x(b)-x(m)-2,height:22,rx:3,fill:'var(--ref)'},g);
  txt(g,x(b)+6,y+16,b.toFixed(1)+' W','lab-strong');hover(g,tip,h,()=>`<b>${NAMES[p]}</b><br>board ${b.toFixed(2)} W · minion rail ${m.toFixed(2)} W<br>SRAM ${M2[p].sram.toFixed(2)} W · mesh ${M2[p].noc.toFixed(2)} W<br>die ${M2[p].temp.toFixed(1)} °C in the window`);});})();
document.getElementById('tbl').innerHTML='<thead><tr><th>Operands (A and B)</th><th class="num">board W, last 3 s</th><th class="num">die °C</th><th class="num">board W, s 1–3</th><th class="num">die °C</th><th class="num">vs zeros</th><th class="num">minion rail W</th><th class="num">SRAM W</th><th class="num">mesh W</th><th class="num">rounds differ by</th></tr></thead><tbody>'+
 order.map(p=>{const v=M2[p];return `<tr><td>${NAMES[p]}</td><td class="num"><b>${v.board.toFixed(1)}</b></td><td class="num">${v.temp.toFixed(1)}</td><td class="num">${v.board_early.toFixed(1)}</td><td class="num">${v.temp_early.toFixed(1)}</td><td class="num">+${(v.board-M2.zeros.board).toFixed(1)}</td><td class="num">${v.minion.toFixed(1)}</td><td class="num">${v.sram.toFixed(2)}</td><td class="num">${v.noc.toFixed(2)}</td><td class="num">${v.spread.toFixed(2)} W</td></tr>`;}).join('')+
 '</tbody><caption class="small" style="caption-side:bottom;text-align:left;padding-top:6px">Mean of two rounds; every run started at 80 °C and ran at 546.0 cycles per op. No temperature correction.</caption>';
(function(){const tr=D.horace2.trace,W=900,H=240,L=50,R=20,T=14,B=34;const {svg}=host('trace',W,H);const tmax=tr[tr.length-1].t;
 const x=t=>L+t/tmax*(W-L-R),y=v=>H-B-(v-76)/(88-76)*(H-B-T);
 for(const t of [78,80,82,84,86,88]){el('line',{x1:L,x2:W-R,y1:y(t),y2:y(t),class:'grid-line'},svg);txt(svg,L-6,y(t)+4,t,'tick','end');}
 for(let t=0;t<=tmax;t+=60)txt(svg,x(t),H-B+18,(t/60)+' min','tick','middle');
 el('line',{x1:L,x2:W-R,y1:y(80),y2:y(80),stroke:'var(--c2)','stroke-width':1.5,'stroke-dasharray':'5 4'},svg);txt(svg,W-R-4,y(78.6),'dashed: start target, 80 °C','lab','end');
 el('path',{d:tr.map((p,i)=>`${i?'L':'M'}${x(p.t).toFixed(1)},${y(p.temp).toFixed(1)}`).join(' '),class:'ln s1'},svg);
 txt(svg,x(4),y(87),'warm-up, then 20 runs; the tall peaks are the random patterns','lab');})();
